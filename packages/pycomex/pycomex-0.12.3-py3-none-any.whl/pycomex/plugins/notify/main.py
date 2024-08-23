import os
import asyncio
import subprocess

import imageio
import matplotlib.pyplot as plt
import desktop_notifier

from pycomex.config import Config
from pycomex.plugin import Plugin, hook
from pycomex.functional.experiment import Experiment
from pycomex.utils import OS_NAME


class NotifyPlugin(Plugin):
    """
    This plugin will send a desktop notification to the user when the experiment is done.
    
    At the end of the experiment (either due to error or completion) this plugin will send a desktop
    notification to the user that the experiment is done and that the results are ready. Clicking the 
    notification will open the archive folder of the experiment.
    """
    
    timeout: int = 5
    
    @hook('after_experiment_finalize', priority=0)
    def after_experiment_finalize(self, config: Config, experiment: Experiment):
        """
        This hook is executed right after the experiment.finalize method was executed. The finalized method 
        will handle the saving of the experiment data and metadata storage at the end of the actual experiment 
        runtime (either completed execution or error).
        
        This method will send a desktop notification to the user that the experiment is done and that the
        results are ready.
        """
        # We'll wrap this in a try-except because we dont want to do this
        
        asyncio.run(self.send_notification(config, experiment))

    def open_experiment_folder(self, path: str) -> None:
        
        if OS_NAME == 'Linux':
            subprocess.run(
                f'nautilus {path}',
                shell=True,
                start_new_session=True,
            )

    async def send_notification(self, config: Config, experiment: Experiment):
        
        notify = desktop_notifier.DesktopNotifier(
            app_name='PyComex',
            notification_limit=10,
        )
        
        stop_event = asyncio.Event()
        
        duration_hours = experiment.metadata['duration'] / 3600
        message = (
            f'Experiment "{experiment.namespace}/{experiment.name}" is done after {duration_hours:.1f} hours!\n'
            f'Error: {experiment.error}. Click to open archive folder.'
        )
        
        await notify.send(
            title='Experiment Finished',
            message=message,
            urgency=desktop_notifier.Urgency.Normal,
            on_clicked=lambda: self.open_experiment_folder(experiment.path),
            on_dismissed=stop_event.set,
        )
        
        loop = asyncio.get_running_loop()
        loop.call_later(self.timeout, stop_event.set)
        
        await stop_event.wait()
        