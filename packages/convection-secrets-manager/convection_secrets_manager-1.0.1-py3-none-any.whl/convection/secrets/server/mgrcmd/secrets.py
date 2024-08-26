# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.shared.objects.plugins.secret import ConvectionPlugin_Secret
from convection.shared.exceptions import StoreNotLoadedError, SystemLockedWarning

from convection.secrets.server.mgrcmd.core import ConvectionManagerCommandCore


class ConvectionManagerSecretCommands(ConvectionManagerCommandCore):
    """Secrets Manager Secrets Management Commands"""
    _store_types:dict[str,typing.Type[ConvectionPlugin_Secret]]
    _secrets_stores:typing.Union[dict[str,ConvectionPlugin_Secret],None]

    # pylint: disable=duplicate-code
    def new_secret(self,store_name:str,secrets_args:dict[str,typing.Any]) -> bool:
        """Create New Secret in Existing Secrets STore
        @param str \c store_name Secrets Store Name
        @param dict[str,Any] \c secrets_args Secrets Store-Specific Args. See Secrets Store Documentation
        @retval bool Success/Failure
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Create Secret, Not Initialized.")
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
            result:bool = store.create(**secrets_args)
        return result

    def update_secret(self,store_name:str,secrets_args:dict[str,typing.Any]) -> bool:
        """Modify Existing Secret in Existing Secrets Store
        @param str \c store_name Secrets Store Name
        @param dict[str,Any] \c secrets_args Secrets Store-Specific Args. See Secrets Store Documentation
        @retval bool Success/Failure
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Modify Secret, Not Initialized.")
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
            result:bool = store.modify(**secrets_args)
        return result

    def remove_secret(self,store_name:str,secrets_args:dict[str,typing.Any]) -> bool:
        """Remove Secret from Secret Store
        @param str \c store_name Secrets Store Name
        @param dict[str,Any] \c secrets_args Secrets Store-Specific Args. See Secrets Store Documentation
        @retval bool Success/Failure
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Destroy Secret, Not Initialized.")
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
            result:bool = store.destroy(**secrets_args)
        return result

    def get_secret(self,store_name:str,secrets_args:dict[str,typing.Any]) -> typing.Any:
        """Get Raw Secret Data (Decrypted Secret)
        @param str \c store_name Secrets Store Name
        @param dict[str,Any] \c secrets_args Secrets Store-Specific Args. See Secrets Store Documentation
        @retval Any Decrypted Secret
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Get Secret, Not Initialized.")
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
            return store.get(**secrets_args)

    def list_secrets(self,store_name:str,secrets_args:dict[str,typing.Any]) -> list[str]:
        """List Secrets in Secret Store
        @param str \c store_name Secrets Store Name
        @param dict[str,Any] \c secrets_args Secrets Store-Specific Args. See Secrets Store Documentation
        @retval list[str] List of Secrets
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot List Secrets, Not Initialized.")
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
            result:list[str] = store.list(**secrets_args)
        return result
    # pylint: enable=duplicate-code
