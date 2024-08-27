# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djx_cmds',
 'djx_cmds.management',
 'djx_cmds.management.commands',
 'djx_cmds.migrations',
 'djx_cmds.services']

package_data = \
{'': ['*'], 'djx_cmds': ['templates/*']}

install_requires = \
['django>=4.1', 'inflection>=0.5.1,<0.6.0', 'jinja2>=3.1.2,<4.0.0']

setup_kwargs = {
    'name': 'djx-cmds',
    'version': '0.1.1',
    'description': '',
    'long_description': '',
    'author': 'nope',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
