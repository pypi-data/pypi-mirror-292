# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['functional',
 'pycomex',
 'pycomex.app',
 'pycomex.examples',
 'pycomex.functional',
 'pycomex.plugins.notify',
 'pycomex.plugins.plot_track',
 'pycomex.plugins.weights_biases']

package_data = \
{'': ['*'], 'pycomex': ['templates/*']}

install_requires = \
['click>=7.1.2',
 'desktop-notifier>=5.0.1,<=6.0.0',
 'jinja2>=3.0.3',
 'matplotlib>=3.5.3',
 'moviepy>=1.0.3',
 'numpy>=1.22.0',
 'psutil>=5.7.2',
 'rich-click>=1.7.0,<=1.8.0']

entry_points = \
{'console_scripts': ['pycomex = pycomex.cli:cli']}

setup_kwargs = {
    'name': 'pycomex',
    'version': '0.12.3',
    'description': 'Python Computational Experiments',
    'long_description': 'None',
    'author': 'Jonas Teufel',
    'author_email': 'jonseb1998@gmail.com',
    'maintainer': 'Jonas Teufel',
    'maintainer_email': 'jonseb1998@gmail.com',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
