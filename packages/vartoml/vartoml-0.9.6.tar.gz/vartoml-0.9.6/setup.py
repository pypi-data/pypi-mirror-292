# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vartoml']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.9']

setup_kwargs = {
    'name': 'vartoml',
    'version': '0.9.6',
    'description': 'Enable variables in a TOML file',
    'long_description': '# Overview\n\n`vartoml` allows using variables in TOML config files. It uses the `toml` package.\n\n# Acknowledgent\n\nThe idea how to tackle the problem of variable interpolation was taken\nfrom the `envtoml` package which is at https://github.com/mrshu/envtoml .\n\n# Variable names in TOML file\n\nVariables are specified this way: `${section[:section]:variable}`, i.e. sections can be nested.\n\n# Example usage\n\n```python\nfrom vartoml import VarToml\n\n\nTOML ="""\n\n[default]\n\nbasedir = "/myproject"\nbindir = "${default:basedir}/bin"\ndatadir = "${default:basedir}/data"\n\n\n[other_dirs-sub]\n\nlogdir = "${default:datadir}/logs"\n"""\n\ntoml = VarToml()\ntoml.loads(TOML)\n\nassert toml.get(\'other_dirs-sub\', \'logdir\') == \'/myproject/data/logs\'\n```\n\n# API\n\n## VarToml.load(f, _dict=dict)\n\n    same like what the toml package offers\n\n## VarToml.loads(s, _dict=dict)\n\n    same like what the toml package offers\n\n## VarToml.get(v,... ) \n\n    returns a specific value from the toml dictionary\n\n    Example: \n    ```python\n    toml = VarToml()\n    toml.loads(\'some.toml\')\n    val = toml.get(\'default\', \'id\' )\n    ```\n\n## VarToml.toml()\n\n  returns the dictionary of the parsed toml data\n',
    'author': 'Manfred Lotz',
    'author_email': 'manfred.lotz@posteo.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/manfredlotz/vartoml',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
