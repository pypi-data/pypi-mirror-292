# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import threading
import logging
import typing
from pathlib import Path

from atckit.utilfuncs import UtilFuncs

from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet,InvalidToken

from convection.shared.config import ConvectionConfigCore
from convection.shared.exceptions import SystemLockedWarning,KeyMapDBNotLoadedError
from convection.shared.functions import get_actions
from convection.shared.objects.plugins.secret import ConvectionPlugin_Secret
from convection.secrets.server.authdb import ConvectionSecretsAuthDB
from convection.secrets.objects.keymapdb import KeyMapDB

class ConvectionManagerCommandCore:
    """Core Class and support functionality for Convection Manager Class"""

    logger:logging.Logger
    config:ConvectionConfigCore
    _root_encryptor:typing.Union[Fernet,None]
    _storage_path:Path
    _locked:bool
    _store_types:dict[str,typing.Type[ConvectionPlugin_Secret]]
    _authdb_action_map:dict[str,typing.Callable]
    _authdb:typing.Union[ConvectionSecretsAuthDB,None]
    _authdb_lock:threading.Lock
    _secrets_stores:typing.Union[dict[str,ConvectionPlugin_Secret],None]
    _keymapdb:typing.Union[KeyMapDB,None]
    _rotation_lock:threading.Lock
    _protected_keyset_names:list[str] = [ "authdb", "root" ]
    _protected_store_names:list[str] = [ "authdb", "root" ]

    @property
    def locked(self) -> bool:
        """Lock Check
        @retval Whether or not System is Unlocked
        """
        return self._locked

    @property
    def initialized(self) -> bool:
        """Initialization Check
        @retval bool Whether Root Key Exists
        """
        return self._storage_path.joinpath("root.key").exists()

    @property
    def store_type_names(self) -> list[str]:
        """List of Secrets Store Type Names
        @retval list[str] List of Secrets Store Type Names
        """
        return list(self._store_types.keys())

    # pylint: disable=duplicate-code
    def lock(self) -> None:
        """Lockdown; De-init KeyMapDB, Secrets Stores, AuthDB, Root Encryptor.
        @retval None Nothing
        An Unlock command must be sent to continue use after calling this
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises SystemLocked System is in Locked State, has not been Unlocked
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Lock, Not Initialized.")
        if self.locked:
            raise SystemError("Secrets Stores Locked")
        with self._authdb_lock:
            with self._rotation_lock:
                self._locked = True
                self._keymapdb = None
                if self._secrets_stores is not None:
                    self._secrets_stores.clear()
                del self._authdb
                self._authdb = None
                self._authdb_action_map.clear()
                self._secrets_stores = None
                del self._root_encryptor
                self._root_encryptor = None

    def unlock(self,key:str) -> bool:
        """Unlock System for Use.
        @param str \c key Unlock Key to unlock Root Key
        @retval bool Success/Failure
        Loads KeyMapDB on success
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises SystemError System is in Unlocked State already
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Unlock, Not Initialized.")
        if not self.locked:
            raise SystemError("Secrets Stores already Unlocked")
        with self._authdb_lock:
            with self._rotation_lock:
                root_keys:list[bytes] = []
                with open(self._storage_path.joinpath("root.key"),"rb") as f:
                    root_keys = f.read().split(b'\n')
                unlocker:Fernet = Fernet(key)
                result:typing.Union[None,bytes] = None
                for k in root_keys:
                    try:
                        result = unlocker.decrypt(k)
                    except (InvalidToken,InvalidSignature):
                        continue
                if result is None:
                    raise InvalidToken("Cannot Unlock, Key did not unlock any Root Key")
                self._root_encryptor = Fernet(result)
                self._secrets_stores = {}
                self._locked = False
                self._load_keymap_db()
        return True

    def store_loaded(self,store_name:str) -> bool:
        """Check Whether or not Secrets Store has already been loaded.
        @param str \c store_name Secrets Store Name
        @retval bool Whether Store is Loaded or Not
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Create Secrets Store, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        if self._secrets_stores is None:
            self.logger.warning("Loaded Stores was None, but should not have been")
            self._secrets_stores = {}
        return store_name in self._secrets_stores.keys()

    def load_store(self,store_name:str) -> ConvectionPlugin_Secret:
        """Load Secrets Storage
        @param str \c store_name Secrets Store Path / Name (EX: `mystore` or `mystores/store1`)
        @retval ConvectionPlugin_Secret Returns an instance of `store_type_name`
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises SystemLocked System is in Locked State, has not been Unlocked
        @raises SystemError Root Encryptor failed to load or is not loaded
        @raises KeyMapDBNotLoaded KeyMapDB Was not Loaded, so cannot load
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Load Secrets Store, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        if store_name not in self._keymapdb.store_names:
            raise ImportError(f"No Such Store {store_name}")
        store_type_name:str = self._keymapdb.get_store_type(store_name)
        keyset_name:str = self._keymapdb.get_store_keyset_name(store_name)
        if store_type_name not in self._store_types.keys():
            raise ImportError(f"No Such Store Type {store_type_name}")
        store_type:typing.Type = self._store_types[store_type_name]
        obj:"store_type" = store_type(store_name,self._get_keys(keyset_name),self._storage_path) # type: ignore[override,valid-type]
        if self._secrets_stores is None:
            self._secrets_stores = {}
        self._secrets_stores[store_name] = obj
        self.logger.debug(f"Loaded Secrets Store {store_name} ({store_type_name})")
        return obj

    def _get_keys(self,keyset_name:str) -> list[bytes]:
        """Get KeySet by Name
        @param str \c keyset_name KeySet Name to load Keys for
        @retval list[bytes] List of Decrypted KeySet Keys
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises FileNotFoundError Requested KeySet does not exist
        @raises SystemLocked System is in Locked State, has not been Unlocked
        @raises SystemError Root Encryptor failed to load or is not loaded
        @raises ImportError KeySet Loading Errors
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Load KeySet, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        keyset_file:Path = self._storage_path.joinpath(f"{keyset_name}.key")
        if not keyset_file.is_file():
            raise FileNotFoundError(f"Cannot Locate KeySet {keyset_name} in Storage Path")
        keyset_keys:list[bytes] = []
        with open(keyset_file,"rb") as f:
            keyset_keys = self._root_encryptor.decrypt(f.read()).split(b'\n')
        if len(keyset_keys) == 0:
            raise ImportError("KeySet File Opened, but no keys were loaded?")
        return keyset_keys

    def _load_keymap_db(self) -> None:
        """Load KeyMapDB
        @raises SystemError Root Encryptor failed to load or is not loaded
        @retval None Nothing
        """
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        with open(self._storage_path.joinpath("keymap.db"),"rb") as f:
            raw:str = self._root_encryptor.decrypt(f.read()).decode("utf-8")
            data:dict[str,typing.Any] = UtilFuncs.load_sstr(raw,"toml")
            self._keymapdb = KeyMapDB(data)
        self.logger.debug("KeyMapDB Loaded")

    def _write_keymap_db(self,force:bool = True) -> None:
        """Write KeyMapDB
        @param bool \c force Force Write (only for use when keymap is empty), default False
        @retval None Nothing
        @raises SystemError Root Encryptor failed to load or is not loaded
        @raises KeyMapDBNotLoaded KeyMapDB Was not Loaded, so cannot write
        """
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        if self._keymapdb is None:
            raise KeyMapDBNotLoadedError()
        data:dict[str,typing.Any] = self._keymapdb.data()
        if len(data) == 0 and not force:
            raise KeyMapDBNotLoadedError()
        keymap_file:Path = self._storage_path.joinpath("keymap.db")
        with open(keymap_file,"wb") as f:
            raw:bytes = bytes(UtilFuncs.dump_sstr(data,"toml"),"utf-8")
            f.write(self._root_encryptor.encrypt(raw))
        keymap_file.chmod(0o600)
        self.logger.info("KeyMapDB Written")

    def _load_authdb(self) -> None:
        """Load AuthDB
        @retval None Nothing
        """
        self._authdb = ConvectionSecretsAuthDB("authdb",self._get_keys("authdb"),self._storage_path)
        self._authdb_action_map = get_actions(self._authdb)
        self._authdb.tlock = self._authdb_lock
    # pylint: enable=duplicate-code
