# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bioplunger']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bioplunger',
    'version': '0.15',
    'description': '',
    'long_description': None,
    'author': 'ParsaGhadermazi',
    'author_email': '54489047+ParsaGhadermazi@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
