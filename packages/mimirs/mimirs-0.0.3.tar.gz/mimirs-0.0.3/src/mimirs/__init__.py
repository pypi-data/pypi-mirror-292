__all__ = ["Mimir", "DataWell"]

from typing import Any


class Mimir(dict):
    def __getitem__(self, key: Any) -> Any:
        try:
            return super().__getitem__(key)
        except KeyError:
            pass
        ans = self.well(self._getitem, key)
        self[key] = ans
        return ans
    def __init__(self, other=None, /, well=None):
        if other is None:
            other = dict()
        super().__init__(other)
        self.well = well
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "well":
            object.__setattr__(self, name, value)
        return super().__setattr__(name, value)
    def _getitem(self, *keys):
        ans = self
        for k in keys:
            ans = ans[k]
        return ans

class DataWell:
    def __call__(self, getitem, key) -> Any:
        if type(key) is not str:
            raise TypeError(key)
        if key.startswith("_"):
            raise ValueError(key)
        return getattr(self.data, key)(getitem)
    def __init__(self, data) -> None:
        self.data = data