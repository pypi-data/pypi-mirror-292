# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

class KeyMapDB:
    """KeyMapDB KeySet to Store mapping, as well as Store and Store Type mapping"""

    _keysets:dict[str,list[str]]
    _store_types:dict[str,list[str]]
    _store_names:list[str]

    @property
    def store_names(self) -> list[str]:
        """Registered Secrets Store Paths/Names
        @retval list[str] List of Secrets Store Names
        """
        return self._store_names

    @property
    def keysets(self) -> list[str]:
        """Registered KeySet Names
        @retval list[str] List of KeySet Names
        """
        return list(self._keysets.keys())

    def __init__(self,data:dict[str,typing.Union[dict[str,typing.Any],list[typing.Any]]]) -> None:
        """Initializer
        @param dict[str,dict[str,Any]] \c data KeyMapDB Content as Dictionary
        """
        self._keysets = {}
        self._store_types = {}
        self._store_names = []
        for k in data["keysets"]:
            self._keysets[k] = []
        for k,v in dict(data["keymap"]).items():
            self.add_store(k,v["keyset"],v["store_type"])

    def get_store_keyset_name(self,store_name:str) -> str:
        """Get Name of KeySet Store is Using
        @param str \c store_name Name of Secrets Store
        @retval str KeySet Name
        """
        for k,v in self._keysets.items():
            if store_name in v:
                return k
        raise KeyError(f"No Such Store: `{store_name}`")

    def get_store_type(self,store_name:str) -> str:
        """Get Store Type Name Store is Using
        @param str \c store_name Name of Secrets Store
        @retval str Store Type Name
        """
        for k,v in self._store_types.items():
            if store_name in v:
                return k
        raise KeyError(f"No Such Store: `{store_name}`")

    def get_store_count(self,keyset_name:str) -> int:
        """Get Number of Secrets Stores KeySets is associated with
        @param str \c keyset_name Name of KeySet
        @retval int Number of Stores KeySet is associated with
        """
        if keyset_name not in self.keysets:
            raise KeyError(f"No Such Keyset `{keyset_name}`")
        return len(self._keysets[keyset_name])

    def add_keyset(self,keyset_name:str) -> None:
        """Add KeySet to KeyMapDB
        @param str \c keyset_name Name of Keyset
        @retval None Nothing
        """
        if keyset_name in self.keysets:
            return
        self._keysets[keyset_name] = []

    def add_store(self,store_name:str,keyset_name:str,store_type:str) -> None:
        """Add Secrets Store to KeyMapDB
        @param str \c store_name Name of Secrets Store to Add
        @param str \c keyset_name Name of KeySet Secrets Store will use
        @param str \c store_type Secrets Store Type Name
        @retval None Nothing
        """
        if store_name in self._store_names:
            return
        if keyset_name not in self._keysets.keys():
            self._keysets[keyset_name] = []
        if store_type not in self._store_types.keys():
            self._store_types[store_type] = []
        self._store_names.append(store_name)
        self._store_types[store_type].append(store_name)
        self._keysets[keyset_name].append(store_name)

    def remove_store(self,store_name:str) -> bool:
        """Remove Secrets Store from KeyMapDB
        @param str \c store_name Secrets Store Name to Remove
        @retval bool Success/Failure
        """
        if store_name not in self._store_names:
            return False
        # pylint: disable=unnecessary-dict-index-lookup
        for k,v in self._keysets.items():
            if store_name in v:
                self._keysets[k].pop(self._keysets[k].index(store_name))
                break
        for k,v in self._store_types.items():
            if store_name in v:
                self._store_types[k].pop(self._store_types[k].index(store_name))
        self._store_names.pop(self._store_names.index(store_name))
        # pylint: enable=unnecessary-dict-index-lookup
        return True

    def remove_keyset(self,keyset_name:str) -> bool:
        """Remove KeySet from KeyMapDB
        @param str \c keyset_name KeySet Name to Remove
        @retval bool Success/Failure
        """
        if keyset_name not in self.keysets:
            return False
        self._keysets.pop(keyset_name)
        return True

    def data(self) -> dict[str,typing.Any]:
        """KeyMapDB Data Output for Writing
        @retval dict[str,Any] KeyMapDB Data
        """
        result:dict[str,typing.Any] = { "keymap": {}, "keysets": [] }
        for store_name in self._store_names:
            result["keymap"][store_name] = {
                "keyset": self.get_store_keyset_name(store_name),
                "store_type": self.get_store_type(store_name)
            }
        result["keysets"] = self.keysets
        return result
