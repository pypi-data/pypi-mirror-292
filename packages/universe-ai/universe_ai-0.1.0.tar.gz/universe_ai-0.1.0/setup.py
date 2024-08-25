# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['universe_ai',
 'universe_ai.models',
 'universe_ai.models.claude',
 'universe_ai.models.monica',
 'universe_ai.models.monica.chat']

package_data = \
{'': ['*']}

install_requires = \
['anthropic>=0.34.1,<0.35.0',
 'httpx>=0.27.0,<0.28.0',
 'pydantic>=2.8.2,<3.0.0',
 'python-dotenv>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'universe-ai',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Hongpei Zheng',
    'author_email': 'zhenghongpei@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
