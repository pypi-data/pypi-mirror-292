"""vartoml - Enable variables in a TOML file"""

__version__ = "0.9.6"
__author__ = "Manfred Lotz <manfred.lotz@posteo.de>"
# __all__ = []

import importlib
import os
import re
from typing import Any, Dict, List, Match, MutableMapping

from icecream import ic

"""
According to the TOML specification (https://toml.io/en/v1.0.0-rc.1)

- naming rules for sections (aka tables) are the same as for keys
- keys may consist of ASCII letters, digits, underscores and dashes


Example:

database = "/var/db/mydb.db"
home_dir = "/home/johndoe"
db-port = 4711
_a = "hey"
-bla = "something"
1ab = true

"""
RE_VAR = re.compile(
    r"""
             [$][{]
             (
                [a-zA-Z0-9_-]+     # section name
                ([:][a-zA-Z0-9_-]+)+     # variable name
             )
             [}]
""",
    re.VERBOSE,
)


class VarToml:
    def __init__(self, which_toml="toml") -> None:
        self.toml = importlib.import_module(which_toml)
        self.which_toml = which_toml
        if which_toml == "toml":
            self.decoder = self.toml.TomlDecoder()

    def load(self, *args, **kwargs):
        self.data = self.toml.load(*args, **kwargs)
        self._process(self.data)

    def loads(self, *args, **kwargs):
        self.data = self.toml.loads(*args, **kwargs)
        self._process(self.data)
        print(f"{self.data=}")

    def _var_replace(self, x):
        toml_var = x.groups()[0]
        lst = toml_var.split(":")
        val = self.data[lst[0]]
        for v in lst[1:]:
            val = val[v]

        return str(val)

    def get(self, *args):
        gotten = self.data
        for arg in args:
            gotten = gotten[arg]
        return gotten

    def dict(self):
        return self.data

    def _process(self, item):
        iter_ = None
        if isinstance(item, dict):
            iter_ = item.items()
        elif isinstance(item, list):
            iter_ = enumerate(item)

        for i, val in iter_:
            ic(i, val)
            if isinstance(val, (dict, list)):
                self._process(val)
            elif isinstance(val, str):
                if re.search(RE_VAR, val):
                    r = re.sub(RE_VAR, self._var_replace, val)
                    if self.which_toml == "toml":
                        # Try to first load the value from the variable contents
                        # (i.e. make what seems like a float a float, what seems like a
                        # boolean a bool and so on). If that fails, fail back to
                        # string.
                        try:
                            item[i], _ = self.decoder.load_value(r)
                            continue
                        except ValueError:
                            pass

                        item[i], _ = self.decoder.load_value('"{}"'.format(r))

                        print(f"{item[i]=}, {r=}")
                    else:
                        item[i] = r
                        print(f"{item[i]=}, {r=}")
                        continue
