# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import shutil
import typing
from pathlib import Path

from cryptography.fernet import MultiFernet,Fernet

from convection.shared.objects.plugins.secret import ConvectionPlugin_Secret
from convection.shared.exceptions import CriticalRotationError, InvalidKeySet, KeyMapDBNotLoadedError, KeyRotationError, ProtectedKeySetError, SystemLockedWarning
from convection.secrets.objects.keymapdb import KeyMapDB
from convection.secrets.server.mgrcmd.core import ConvectionManagerCommandCore


class ConvectionManagerKeyCommands(ConvectionManagerCommandCore):
    """Secrets Manager Key Management Commands"""
    _store_types:dict[str,typing.Type[ConvectionPlugin_Secret]]
    _secrets_stores:typing.Union[dict[str,ConvectionPlugin_Secret],None]
    _keyset_key_count:int

    # pylint: disable=duplicate-code
    def destroy_keyset(self,keyset_name:str) -> bool:
        """Destroy / Delete a KeySet
        @param str \c keyset_name KeySet Name to Delete, No Stores may be associated with it.
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
                raise ProtectedKeySetError(f"'{keyset_name}' is a protected keyset name and cannot be deleted")
            if keyset_name not in self._keymapdb.keysets:
                raise FileNotFoundError(f"Secrets Store {keyset_name} does not exist, so cannot be deleted")
            if self._keymapdb.get_store_count(keyset_name) > 0:
                raise ProtectedKeySetError(f"'{keyset_name}' is in use and cannot currently be deleted. Delete associated Secrets Stores first")
            self._keymapdb.remove_keyset(keyset_name)
            target_keyfile:Path = self._storage_path.joinpath(f"{keyset_name}.key")
            target_keyfile.unlink()
            self.logger.info(f"Destroyed KeySet {keyset_name}")
            self._write_keymap_db()
        return True

    def rotate_unlock_keys(self,num_keys:int) -> list[str]:
        """Unlock Key and Root Key Rotation
        @param int \c num_keys Number of Unlock Keys to Generate
        @retval list[str] List of new Unlock Keys
        @warning This touches KeyMapDB, Root Key, Unlock Keys, all KeySets. During this process, Each is backed up, then operated on. Failure will revert all items. This should work, but has the potential to fail.
        @warning you should be sure to create backups before performing a rotation
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises SystemLocked System is in Locked State, has not been Unlocked
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Rotate Unlock Keys, Not Initialized")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        with self._rotation_lock:
            if self._keymapdb is None:
                self._load_keymap_db()
                if self._keymapdb is None:
                    raise KeyMapDBNotLoadedError()
            root_output:typing.Tuple[bytes,list[str],list[bytes]] = self.__generate_root_key(num_keys)
            old_encryptor:Fernet = self._root_encryptor
            new_encryptor:Fernet = Fernet(root_output[0])
            temp_encryptor:MultiFernet = MultiFernet([new_encryptor,old_encryptor])
            for keyset in self._keymapdb.keysets:
                self.logger.info(f"Backing up KeySet: {keyset}")
                keyfile:Path = self._storage_path.joinpath(f"{keyset}.key")
                keyfile_bak:Path = self._storage_path.joinpath(f"{keyset}.key.bak")
                shutil.copy2(keyfile,keyfile_bak)
            success:bool = False
            self._locked = True
            steps:list[str] = []
            self.logger.info("Rotating KeySets")
            success = self.__unlock_key_rotate_keysets(temp_encryptor)
            steps.append("Rotate KeySets")
            if success:
                self.logger.info("Rotating KeyMapDB")
                success = self.__unlock_key_rotate_keymap_db(temp_encryptor)
                steps.append("Rotate KeyMapDB")
            if success:
                self.logger.info("Writing New Root Keys")
                with open(self._storage_path.joinpath("root.key"),"wb") as f:
                    f.write(b'\n'.join(root_output[2]))
                steps.append("Write New Root Keys")
            if not success:
                self.logger.error(f"Rotation Failed during: {steps[-1]}")
                self.__unlock_key_rollback_rotation()
                raise SystemError(f"Rotation Failed; Failed on: {steps[-1]}")
            self.__unlock_key_rotation_cleanup()
            self.logger.info("Rotation Complete")
            self._locked = False
        self.lock()
        return root_output[1]

    def new_root_key(self,num_keys:int) -> list[str]:
        """Initialization / Root Key, KeyMapDB Generation
        @param int \c num_keys Number of Unlock Keys to generate
        @retval list[str] List of Unlock Keys
        @raises FileExistsError Already Initialized / Root Key Exists
        """
        if self.initialized:
            raise FileExistsError("Cannot create new Root Key, already exists")
        root_output:typing.Tuple[bytes,list[str],list[bytes]] = self.__generate_root_key(num_keys)
        root_path:Path = self._storage_path.joinpath("root.key")
        with open(root_path,"wb") as f:
            f.write(b'\n'.join(root_output[2]))
        root_path.chmod(0o600)
        self._root_encryptor = Fernet(root_output[0])
        self._keymapdb = KeyMapDB({ "keysets": [], "keymap": {} })
        self._locked = False
        self._write_keymap_db(True)
        self.lock()
        return root_output[1]

    def new_keyset(self,keyset_name:str,force:bool = False) -> bool:
        """Create new KeySet
        @param str \c keyset_name KeySet Name, cannot already exist.
        @param bool \c force Skip Protected KeySet Name check (only for internal use)
        @retval None Nothing
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises FileExistsError KeySet already exists
        @raises SystemLocked System is in Locked State, has not been Unlocked
        @raises SystemError Root Encryptor failed to load or is not loaded
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Create KeySet, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        if keyset_name in self._protected_keyset_names and not force:
            raise ProtectedKeySetError(f"'{keyset_name}' is a protected KeySet name and cannot be used")
        target_keyfile:Path = self._storage_path.joinpath(f"{keyset_name}.key")
        if target_keyfile.exists() or keyset_name in self._keymapdb.keysets:
            raise FileExistsError("Cannot create KeySet that already exists, use rotate command instead")
        keys:list[bytes] = []
        for _ in range(0,self._keyset_key_count):
            keys.append(Fernet.generate_key())
        self.__write_keyset_keys(keyset_name,keys)
        self._keymapdb.add_keyset(keyset_name)
        self.logger.info(f"Created KeySet {keyset_name}")
        self._write_keymap_db()
        return True

    def rotate_keyset(self,keyset_name:str) -> bool:
        """Rotate Keys within KeySet, and Re-encrypt all Secrets Stores associated with KeySet
        @warning If this function fails, Secrets Stores may be left in an unusable state. Because this relies on plugins functioning correctly, there is no guarantee unfortunately.
        If a Secrets Store fails to rotate, a reversion attempt will be made on all successfully rotated Secrets Stores by calling the `rotate()` command again, with the original keys.
        If a reversion fails, all processes are stopped. The new Keys will be saved to `ROTATED_{keyset_name}`, the old will be at `{keyset_name}`.
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Rotate Unlock Keys, Not Initialized")
        if self.locked:
            raise SystemLockedWarning()
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        with self._rotation_lock:
            if self._keymapdb is None:
                self._load_keymap_db()
                if self._keymapdb is None:
                    raise KeyMapDBNotLoadedError()
            if self._secrets_stores is None:
                self.logger.warning("Loaded Stores was None, but should not have been")
                self._secrets_stores = {}
            if keyset_name not in self._keymapdb.keysets:
                raise InvalidKeySet(keyset_name)
            rotate_stores:list[str] = []
            completed:list[str] = []
            failed:bool = False
            broken:bool = False
            failed_store_name:str = ""
            broken_store_name:str = ""
            for store_name in self._keymapdb.store_names:
                if self._keymapdb.get_store_keyset_name(store_name) == keyset_name:
                    rotate_stores.append(store_name)
            new_keys:list[bytes] = []
            for _ in range(0,self._keyset_key_count):
                new_keys.append(Fernet.generate_key())
            self.logger.info(f"New Keys Generated for KeySet {keyset_name}")
            failed,failed_store_name = self.__rotate_keyset(keyset_name,new_keys,rotate_stores,completed)
            if failed:
                broken,broken_store_name = self.__failed_keyset_rotation(keyset_name,completed)
            if broken:
                self.__write_keyset_keys(f"ROTATED_{keyset_name}",new_keys)
                self._keymapdb.add_keyset(keyset_name)
                self._write_keymap_db()
                raise CriticalRotationError(f"Key Rotation Failed for KeySet {keyset_name} while Rotating Store {failed_store_name}; ADDITIONALLY, REVERSION OF {broken_store_name} FAILED. RESTORE FROM BACKUP IS RECOMMENDED")
            if failed:
                raise KeyRotationError(f"Key Rotation Failed for KeySet {keyset_name} while Rotating Store {failed_store_name}; However, All Stores Reverted Successfully. The original Keys for the KeySet are still able to successfully be used.")
            self.logger.info(f"All Secrets Stores Associated with {keyset_name} have been rotated successfully")
            self.__write_keyset_keys(keyset_name,new_keys)
        return True

    def list_keysets(self) -> list[str]:
        """Get List of KeySet Names
        @retval list[str] KeySet Names
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot List Keysets, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        keysets:list[str] = self._keymapdb.keysets.copy()
        for k in self._protected_keyset_names:
            if k in keysets:
                keysets.pop(keysets.index(k))
        return keysets

    def __generate_root_key(self,num_keys:int) -> typing.Tuple[bytes,list[str],list[bytes]]:
        """Root Key and Unlock Key Generator
        @param int \c num_keys Number of Unlock Keys to Generate
        @retval tuple[bytes,list[str],list[bytes]] Root Key, Unlock Keys, Root Key Encrypted with each Unlock Key
        """
        unlock_keys:list[str] = []
        root_key:bytes = Fernet.generate_key()
        encrypted_roots:list[bytes] = []
        for _ in range(0,num_keys):
            u:bytes = Fernet.generate_key()
            unlock_keys.append(u.decode("utf-8"))
            enc:bytes = Fernet(u).encrypt(root_key)
            encrypted_roots.append(enc)
        return (root_key,unlock_keys,encrypted_roots)

    def __unlock_key_rotation_cleanup(self) -> None:
        """KeySet and KeyMapDB Rotation Cleanup after Success
        @retval None Nothing
        """
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        self.logger.info("Cleaning up")
        self._storage_path.joinpath("keymap.db.bak").unlink()
        for keyset in self._keymapdb.keysets:
            self._storage_path.joinpath(f"{keyset}.key.bak").unlink()

    def __unlock_key_rollback_rotation(self) -> None:
        """KeySet and KeyMapDB Rotation Rollback on Failure
        @retval None Nothing
        """
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        keymap_db:Path = self._storage_path.joinpath("keymap.db")
        keymap_db_bak:Path = self._storage_path.joinpath("keymap.db.bak")
        self.logger.warning("Rotation Failed, Rolling back Changes")
        for keyset in self._keymapdb.keysets:
            self.logger.debug(f"Rolling Back {keyset}")
            keyfile:Path = self._storage_path.joinpath(f"{keyset}.key")
            keyfile_bak:Path = self._storage_path.joinpath(f"{keyset}.key.bak")
            if keyfile_bak.is_file():
                shutil.move(keyfile_bak,keyfile)
        if keymap_db_bak.is_file():
            shutil.move(keymap_db_bak,keymap_db)

    def __unlock_key_rotate_keysets(self,encryptor:MultiFernet) -> bool:
        """KeySet Encryption Rotation
        @param cryptography.fernet.MultiFernet \c encryptor Encryptor/Decryptor, Must include (in order) the new root key, the original root key.
        @retval bool Success/Failure
        """
        if self._keymapdb is None:
            self._load_keymap_db()
            if self._keymapdb is None:
                raise KeyMapDBNotLoadedError()
        result:bool = True
        for keyset in self._keymapdb.keysets:
            self.logger.info(f"Reencrypting KeySet {keyset}")
            try:
                keyfile:Path = self._storage_path.joinpath(f"{keyset}.key")
                with open(keyfile,"r+b") as f:
                    raw:bytes = f.read()
                    f.truncate(0)
                    f.seek(0)
                    f.write(encryptor.rotate(raw))
            except BaseException as e:
                self.logger.error(f" - Failed: {type(e).__qualname__} - {e}")
                result = False
                break
            self.logger.info(" - Success")
        self.logger.info("KeySet Rotation Complete")
        return result

    def __unlock_key_rotate_keymap_db(self,encryptor:MultiFernet) -> bool:
        """KeyMapDB Encryption Rotation
        @param cryptography.fernet.MultiFernet \c encryptor Encryptor/Decryptor, Must include (in order) the new root key, the original root key.
        @retval bool Success/Failure
        """
        result:bool = True
        keymap_db:Path = self._storage_path.joinpath("keymap.db")
        keymap_db_bak:Path = self._storage_path.joinpath("keymap.db.bak")
        self.logger.info("Reencrypting KeyMapDB")
        shutil.copy2(keymap_db,keymap_db_bak)
        try:
            with open(keymap_db,"r+b") as f:
                raw:bytes = f.read()
                f.truncate(0)
                f.seek(0)
                f.write(encryptor.rotate(raw))
        except BaseException as e:
            self.logger.error(f" - Failed: {type(e).__qualname__} - {e}")
            result = False
        self.logger.info(" - Success")
        return result

    def __rotate_keyset(self,keyset_name:str,new_keys:list[bytes],rotate_stores:list[str],completed_stores:list[str]) -> typing.Tuple[bool,str]:
        """KeySet Rotation core functionality. For each store, call rotate with the new keys.
        @param str \c keyset_name Name of KeySet being updated
        @param list[bytes] \c new_keys Raw Keys that will be rotated in
        @param list[str] \c rotate_stores List of Stores to be rotated
        @param list[str] \c completed_stores List defined to hold Stores that were successfully rotated
        @retval Tuple[bool,str] Success/Failure, Secrets Store that failed to rotate and is causing the rollback ("" if successful)
        """
        if self._secrets_stores is None:
            self.logger.warning("Loaded Stores was None, but should not have been")
            self._secrets_stores = {}
        store_obj:ConvectionPlugin_Secret
        failed:bool = False
        result:bool
        failed_store_name:str = ""
        for store_name in rotate_stores:
            self.logger.info(f"Starting Key Rotation for {store_name}")
            if not self.store_loaded(store_name):
                store_obj = self.load_store(store_name)
            else:
                store_obj = self._secrets_stores[store_name]
            result = store_obj.rotate(new_keys)
            if not result:
                self.logger.error(f"Key Rotation Failed for KeySet {keyset_name} while Rotating Store {store_name}. Rolling Back Operation")
                failed_store_name = store_name
                failed = True
                break
            self.logger.info(f"Completed Key Rotation for {store_name}")
            completed_stores.append(store_name)
        return (failed,failed_store_name)

    def __failed_keyset_rotation(self,keyset_name:str,completed_stores:list[str]) -> typing.Tuple[bool,str]:
        """KeySet Rotation Revert. On Failure, attempt to re-rotate the original keys. SPOOKY THINGS AHEAD
        @param str \c keyset_name Name of KeySet being updated
        @param list[str] \c completed_stores List of Secrets Stores that were successfully rotated before the failure
        @retval Tuple[bool,str] Success/Failure, Secrets Store that failed to re-rotate and is causing the abort ("" if successful)
        @warning If a rollback fails for a store that already succeeded, we assume that everything is about to go horribly wrong
        @warning The New Keys will be saved as `ROTATED_{keyset_name}`, the original as `{keyset_name}` will still exist.
        @warning No Further rollback attempts on any other stores will be performed. This will mean that there may be Secrets Stores
        @warning that are utilizing the `ROTATED_` KeySet, while some are still using the original. the `ROTATED_` KeySet will be registered
        @warning so that it may still be possible to utilize that KeySet for decryption methods (However the KeySet name for the Store will
        @warning still reference the original name (not the `ROTATED_` name)). Manual Recovery Steps will be neccessary in order to restore
        @warning functionality. The Server should be shutdown after this happens, to prevent modification of data and cause more problems.
        """
        if self._secrets_stores is None:
            self.logger.warning("Loaded Stores was None, but should not have been")
            self._secrets_stores = {}
        broken:bool = False
        store_obj:ConvectionPlugin_Secret
        broken_store_name:str = ""
        for store_name in completed_stores:
            self.logger.warning(f"Reverting Key Rotation for {store_name}")
            if not self.store_loaded(store_name):
                store_obj = self.load_store(store_name)
            else:
                store_obj = self._secrets_stores[store_name]
            if not store_obj.rotate(self._get_keys(store_name)):
                self.logger.critical(f"Reversion Failed for KeySet {keyset_name} while Reverting Store {store_name}. Completely Stopping All Tasks")
                self.logger.critical(f"YOUR SECRETS ARE IN DANGER. IT IS POSSIBLE THAT THE SECRET STORE '{store_name}' WAS LOST. OTHERS MAY BE IN AN UNUSABLE STATE")
                self.logger.critical(f"YOU WILL LIKELY NEED TO REVERT BACKUPS FOR ALL STORES ASSOCIATED WITH THE KEYSET '{keyset_name}'")
                self.logger.critical(f"THE KEYS BEING ROTATED IN HAVE BEEN SAVED AS 'ROTATED_{keyset_name}' IN AN ATTEMPT TO MAKE RECOVERY OF OTHER STORES MORE PROBABLE")
                broken = True
                broken_store_name = store_name
                break
            self.logger.info(f"Completed Key Reversion for {store_name}")
        return (broken,broken_store_name)

    def __write_keyset_keys(self,keyset_name:str,keys:list[bytes]) -> bool:
        """Create KeySet File
        @param str \c keyset_name Name of KeySet
        @param list[bytes] \c keys Raw Keys for KeySet
        @retval bool Success/Failure
        """
        target_keyfile:Path = self._storage_path.joinpath(f"{keyset_name}.key")
        if self._root_encryptor is None:
            raise SystemError("Root Encryptor was NoneType")
        keyset:bytes = b'\n'.join(keys)
        with open(target_keyfile, "wb") as f:
            f.write(self._root_encryptor.encrypt(keyset))
        target_keyfile.chmod(0o600)
        return True
    # pylint: enable=duplicate-code
