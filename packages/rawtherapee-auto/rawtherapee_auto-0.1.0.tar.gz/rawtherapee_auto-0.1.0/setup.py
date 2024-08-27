# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rawtherapee_auto']

package_data = \
{'': ['*'], 'rawtherapee_auto': ['res/*']}

install_requires = \
['click>=8.1.7,<9.0.0', 'tqdm>=4.66.5,<5.0.0']

entry_points = \
{'console_scripts': ['rawtherapee-auto = rawtherapee_auto.cli:main']}

setup_kwargs = {
    'name': 'rawtherapee-auto',
    'version': '0.1.0',
    'description': 'Import raw photos and use RawTherapee to auto-level them before copying them to an output location.',
    'long_description': "# RawTherapee Auto\n\nA CLI to automatically adjust raw photos using RawTherapee.\n\n## Installation\n\nRawTherapee is an excellent, free and open-source raw photo editor. Download it from <https://rawtherapee.com>. Note that you will need to install both the application and the CLI tool for `rawtherapee-auto` to function.\n\nAfter this, install `rawtherapee-auto` using Pip or your Python package management tool of choice.\n\n## Usage\n\n```shell\nrawtherapee-auto /path/to/raw/photos /desired/output/location\n```\n\nThis will run RawTherapee on all the raw photos found in `/path/to/raw/photos`. It will use RawTherapee's auto-level functionality to try to get exposure, contrast, etc. in the right ball-park for each photo found. Then it will move the original raw photo along with the outputted .pp3 file from RawTherapee's processing to the `/desired/output/location`.\n\nRun `rawtherapee-auto --help` for additional help.\n",
    'author': 'Ryan McKeown',
    'author_email': 'ryanmckeown@mail4me.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
