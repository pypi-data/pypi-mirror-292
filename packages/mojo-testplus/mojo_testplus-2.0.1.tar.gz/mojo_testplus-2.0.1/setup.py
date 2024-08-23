# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'source/packages'}

packages = \
['mojo',
 'mojo.factories',
 'mojo.testplus',
 'mojo.testplus.cli',
 'mojo.testplus.cli.cmdtree',
 'mojo.testplus.cli.cmdtree.testing',
 'mojo.testplus.cli.cmdtree.utilities',
 'mojo.testplus.sequencing',
 'mojo.testplus.templates']

package_data = \
{'': ['*'],
 'mojo.testplus.templates': ['v0/*',
                             'v0/static/*',
                             'v0/tabs/*',
                             'v1/*',
                             'v1/static/*',
                             'v1/tabs/*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'debugpy>=1.6.5,<2.0.0',
 'mojo-collections>=2.0.0,<2.1.0',
 'mojo-config>=2.0.0,<2.1.0',
 'mojo-errors>=2.0.0,<2.1.0',
 'mojo-extension>=2.0.0,<2.1.0',
 'mojo-results>=2.0.0,<2.1.0',
 'mojo-runtime>=2.0.0,<2.1.0',
 'mojo-xmodules>=2.0.0,<2.1.0',
 'requests>=2.32.3,<3.0.0']

extras_require = \
{'couchdb': ['couchdb>=1.2,<2.0'], 'mongodb': ['pymongo>=4.0.0,<5.0.0']}

entry_points = \
{'console_scripts': ['testplus = '
                     'mojo.testplus.cli.testplus_command:testplus_root_command']}

setup_kwargs = {
    'name': 'mojo-testplus',
    'version': '2.0.1',
    'description': 'Automation Mojo TestPlus Test Framework',
    'long_description': '\n==========================\nAutomation Mojo - Testplus\n==========================\n \nThis is preliminary release of the \'testplus\' automation framework in a separate package from\nthe AutomationKit.  This release is not ready for public consumption because it is under "very active" development.\n\n',
    'author': 'Myron Walker',
    'author_email': 'myron.walker@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'http://automationmojo.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
