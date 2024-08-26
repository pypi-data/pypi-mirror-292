# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.shared.objects.plugins.secret import ConvectionPlugin_Secret
from convection.shared.exceptions import KeyMapDBNotLoadedError, ProtectedKeySetError, ProtectedStoreError, SystemLockedWarning, StoreNotLoadedError

from convection.secrets.server.mgrcmd.core import ConvectionManagerCommandCore


class ConvectionManagerStoreCommands(ConvectionManagerCommandCore):
    """Secrets Manager Secrets Store Management Commands"""

    _store_types:dict[str,typing.Type[ConvectionPlugin_Secret]]
    _secrets_stores:typing.Union[dict[str,ConvectionPlugin_Secret],None]

    # pylint: disable=duplicate-code
    def new_store(self,store_name:str,keyset_name:str,store_type_name:str,store_args:typing.Union[dict[str,typing.Any],None]) -> bool:
        """Create new Secrets Storage
        @param str \c store_name Secrets Store Path / Name (EX: `mystore` or `mystores/store1`)
        @param str \c keyset_name KeySet Name to use for Securing Secrets Store
        @param str \c store_type_name Type of Secrets Storage instance to create, See Plugin Map Documentation
        @retval None Nothing
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises FileExistsError Secrets Store already exists
        @raises SystemLocked System is in Locked State, has not been Unlocked
        @raises SystemError Root Encryptor failed to load or is not loaded
        @raises KeyMapDBNotLoadedError KeyMapDB Was not Loaded, so cannot load
        @raises ProtectedKeySetError KeySet name is Protected/Restricted
        @retval bool Success/Failure
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Create Secrets Store, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        with self._rotation_lock:
            if self._keymapdb is None:
                self._load_keymap_db()
                if self._keymapdb is None:
                    raise KeyMapDBNotLoadedError()
            if keyset_name in self._protected_keyset_names:
                if not (keyset_name == "authdb" and store_name == "authdb"):
                    raise ProtectedKeySetError(f"'{keyset_name}' is a protected KeySet name and cannot be used")
            if keyset_name not in self._keymapdb.keysets:
                raise FileNotFoundError(f"KeySet Name {keyset_name} does not exist, so cannot be used")
            if store_name in self._keymapdb.store_names:
                raise FileExistsError(f"Cannot Create Secrets Store {store_name}, already exists")
            if store_type_name not in self._store_types.keys():
                raise ImportError(f"No Such Store Type {store_type_name}")
            store_type:typing.Type[ConvectionPlugin_Secret] = self._store_types[store_type_name]
            self.logger.debug(self._store_types)
            self.logger.debug(f"Store Type: {store_type.__qualname__}")
            store:"store_type" = store_type(store_name,self._get_keys(keyset_name),self._storage_path,store_args) # type: ignore[override,valid-type]
            store.initialize() # type: ignore[attr-defined]
            self._keymapdb.add_store(store_name,keyset_name,store_type_name)
            self.logger.info(f"Created Secrets Store {store_name} ({store_type_name}) using KeySet {keyset_name}")
            self._write_keymap_db()
        return True

    def list_stores(self) -> list[str]:
        """Get List of Secrets Stores
        @retval list[str] Secrets Store Names
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot List Secrets Stores, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        stores:list[str] = self._keymapdb.store_names.copy()
        for s in self._protected_store_names:
            if s in stores:
                stores.pop(stores.index(s))
        return stores

    def destroy_store(self,store_name:str) -> bool:
        """Destroy / Delete a Secrets Store
        @param str \c store_name Secrets Store Name to Delete
        @retval bool Success/Failure
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Create Secrets Store, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        with self._rotation_lock:
            if self._keymapdb is None:
                self._load_keymap_db()
                if self._keymapdb is None:
                    raise KeyMapDBNotLoadedError()
            if store_name in self._protected_store_names:
                raise ProtectedStoreError(f"'{store_name}' is a protected Secrets Store name and cannot be deleted")
            if store_name not in self._keymapdb.store_names:
                raise FileNotFoundError(f"Secrets Store {store_name} does not exist, so cannot be deleted")
            store_type_name:str = self._keymapdb.get_store_type(store_name)
            store_type:typing.Type[ConvectionPlugin_Secret] = self._store_types[store_type_name]
            obj:"store_type" # type: ignore[override,valid-type]
            if self._secrets_stores is not None:
                if store_name in self._secrets_stores.keys():
                    obj = self._secrets_stores.pop(store_name)
                else:
                    obj = self.load_store(store_name)
            else:
                obj = self.load_store(store_name)
            result:bool = True
            try:
                obj.marked_for_delete() # type: ignore[attr-defined]
            except NotImplementedError:
                self.logger.warning(f"Secrets Store type '{store_type_name}' does not implement `marked_for_delete`, you will probably need to cleanup {store_name} by hand")
                result = False
            self._keymapdb.remove_store(store_name)
            self.logger.info(f"Destroyed Secrets Store {store_name} ({store_type_name})")
            self._write_keymap_db()
        return result

    def configure_store(self,store_name:str,config_args:dict[str,typing.Any]) -> typing.Any:
        """View/Set Secrets Store Config data
        @param str \c store_name Secrets Store to configure
        @param dict[str,Any] \c config_args Store-Specific Configuration Args. See Secrets Store Documentation
        @retval Any Depends on Secrets Store
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Configure Store, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        with self._rotation_lock:
            if self._secrets_stores is None:
                self.logger.warning("Loaded Stores was None, but should not have been")
                self._secrets_stores = {}
            if not self.store_loaded(store_name):
                self.load_store(store_name)
            if store_name not in self._secrets_stores.keys():
                raise StoreNotLoadedError(f"Failed to load Secrets Store {store_name}")
            store:ConvectionPlugin_Secret = self._secrets_stores[store_name]
            return store.configure(**config_args)

    def get_store_info(self,store_name:str) -> dict[str,typing.Any]:
        """Get Secrets Store Stats and Information
        @param str \c store_name Secrets Store Name
        @retval dict[str,Any] Store Information. If Store does not provide any info (by not implementing the `info` function), the 'empty' key will be set
        Keyset information is included whether or not the Store provides an `info` function.
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Configure Store, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        with self._rotation_lock:
            if self._secrets_stores is None:
                self.logger.warning("Loaded Stores was None, but should not have been")
                self._secrets_stores = {}
            if not self.store_loaded(store_name):
                self.load_store(store_name)
            if store_name not in self._secrets_stores.keys():
                raise StoreNotLoadedError(f"Failed to load Secrets Store {store_name}")
            store:ConvectionPlugin_Secret = self._secrets_stores[store_name]
            info:dict[str,typing.Any] = {}
            try:
                info = store.info()
            except NotImplementedError:
                info["empty"] = "No Stats or Information Provided By Store Type"
            info["keyset"] = self._keymapdb.get_store_keyset_name(store_name)
        return info
    # pylint: enable=duplicate-code
