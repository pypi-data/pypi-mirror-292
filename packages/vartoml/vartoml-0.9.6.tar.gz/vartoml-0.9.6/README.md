# Overview

`vartoml` allows using variables in TOML config files. It uses the `toml` package.

# Acknowledgent

The idea how to tackle the problem of variable interpolation was taken
from the `envtoml` package which is at https://github.com/mrshu/envtoml .

# Variable names in TOML file

Variables are specified this way: `${section[:section]:variable}`, i.e. sections can be nested.

# Example usage

```python
from vartoml import VarToml


TOML ="""

[default]

basedir = "/myproject"
bindir = "${default:basedir}/bin"
datadir = "${default:basedir}/data"


[other_dirs-sub]

logdir = "${default:datadir}/logs"
"""

toml = VarToml()
toml.loads(TOML)

assert toml.get('other_dirs-sub', 'logdir') == '/myproject/data/logs'
```

# API

## VarToml.load(f, _dict=dict)

    same like what the toml package offers

## VarToml.loads(s, _dict=dict)

    same like what the toml package offers

## VarToml.get(v,... ) 

    returns a specific value from the toml dictionary

    Example: 
    ```python
    toml = VarToml()
    toml.loads('some.toml')
    val = toml.get('default', 'id' )
    ```

## VarToml.toml()

  returns the dictionary of the parsed toml data
