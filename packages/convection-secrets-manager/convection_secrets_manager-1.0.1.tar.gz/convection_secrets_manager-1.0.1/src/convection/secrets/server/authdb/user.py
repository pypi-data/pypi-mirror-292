# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
from uuid import uuid4

from convection.shared.exceptions import AuthDBNotLoadedError, InvalidAccessKeyError, InvalidPubKeyError, InvalidUserError, ProtectedUserError, PubkeyExistsError

from convection.secrets.objects.authdb.group import AuthDBGroup
from convection.secrets.server.authdb.core import ConvectionAuthDBCore
from convection.secrets.objects.authdb.user import AuthDBUser

# pylint: disable=duplicate-code
class ConvectionAuthDBUser(ConvectionAuthDBCore):
    """Convection AuthDB User Management"""

    def get(self,user_name:str) -> dict[str,typing.Any]:
        """Get ACLs, other info, in full, that User is a part of
        @param str \c user_name User Name to get ACLs of
        @retval dict[str,Any] List of ACLs that User has attached (Either directly, or by a Group), Groups User is part of, Number of Access Keys, Number of active Auth Tokens
        """
        result:dict[str,typing.Any] = {}
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            users:dict[str,AuthDBUser] = self._authdb["users"]
            if user_name not in users.keys():
                raise InvalidUserError(user_name)
            user:AuthDBUser = users[user_name]
            result["acls"] = user.acls.acl_names
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            result["groups"] = [ g.name for g in groups.values() if user in g.users ]
            result["access-key-count"] = len(user.keys)
            result["auth-token-count"] = len(user.tokens)
            self._close()
        return result

    def list(self) -> list[str]:
        """List of Users
        @retval list[str] List of User Names
        """
        user_names:list[str] = []
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            users:dict[str,AuthDBUser] = self._authdb["users"]
            user_names = [ u.name for u in users.values() ]
            self._close()
        return user_names

    # pylint: disable=arguments-differ
    def create(self,target:str,pubkey:str) -> str: # type: ignore[override]
        """Create new User and / or Access Key ID
        @param str \c target Username to associate with, or create, if does not exist
        @param str \c pubkey RSA DER formatted Public Key to associate. Must be the key content (obviously)
        @retval str new Access Key ID
        @raises PubkeyExists Attempt to create User/Public Key pair that already exists
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            userobj:AuthDBUser
            if target not in self._authdb["users"].keys():
                self.logger.info(f"Creating New User {target}")
                userobj = AuthDBUser(target,[],[],[])
                self._authdb["users"][target] = userobj
            else:
                userobj = self._authdb["users"][target]
            if not pubkey.startswith("-----"):
                self._close()
                raise InvalidPubKeyError("Invalid PublicKey Format")
            pubkey_fixed:str = '\n'.join([ p for p in pubkey.split('\n') if not p.startswith("-----") ])
            for keypair in userobj.keys:
                if keypair["pubkey"] == pubkey_fixed:
                    self._close()
                    raise PubkeyExistsError("Public Key already exists")
            accesskey:str = uuid4().hex
            new_key:dict[str,str] = {
                "access_key_id": accesskey,
                "pubkey": pubkey_fixed
            }
            userobj.keys.append(new_key)
            self.logger.info(f"Attached new Public Key to User {target} ({accesskey})")
            self._write()
        return accesskey

    def destroy(self,target:typing.Union[str,None] = None,access_key_id:typing.Union[str,None] = None,public_key:typing.Union[str,None] = None) -> bool: # type: ignore[override]
        """Remove a User, and/or Access Key ID (and/or Public Key)
        @param Union[str,None] \c target Username to remove, or operate on if other options defined. Default None
        @param Union[str,None] \c access_key_id Access Key ID to remove. Default None
        @param Union[str,None] \c public_key Public Key to remove. Default None
        @retval bool Success / Failure
        @raises SyntaxError No arguments defined (At least one must be defined)
        @raises InvalidUserError No such user
        @raises ProtectedUserError Attempted to completely remove protected User
        @raises AuthDBNotLoadedError AuthDB was not Loaded
        @raises InvalidAccessKeyError Access Key ID was not found
        @raises InvalidPubKeyError Public Key was not found
        At least one of the arguments must be defined. If User is not specified, it will be derived from the Access Key ID or Public Key
        """
        if all(v is None for v in [ target, access_key_id, public_key]):
            self.logger.warning("Call to Remove Access with no User, Access Key ID or, Public Key")
            raise SyntaxError("At least one argument must be defined")
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            if target is None:
                if access_key_id is not None:
                    target = self._get_user_by_accesskey(access_key_id)
                elif public_key is not None:
                    target = self._get_user_by_publickey(public_key)
            if target is None:
                self._close()
                self.logger.warning("Attempt to remove user that does not exist or the Access Key / Public Key is not in AuthDB at all")
                raise InvalidUserError("Attempt to remove user that does not exist or the Access Key / Public Key is not in AuthDB at all")
            if target in self._protected_users and all(v is None for v in [access_key_id,public_key]):
                self.logger.warning("Attempted to completely remove protected user")
                self._close()
                raise ProtectedUserError("Attempted to completely remove protected user")
            if access_key_id is None and public_key is None:
                self._authdb["users"].pop(target)
                self.logger.info(f"Removed User '{target}' entirely")
            else:
                if not self.__find_and_remove(target,access_key_id,public_key):
                    self.logger.warning("Attempt to remove Access Key ID or Public Key that does not exist")
                    self._close()
                    if access_key_id is not None:
                        raise InvalidAccessKeyError("Access Key ID does not exist")
                    if public_key is not None:
                        raise InvalidPubKeyError("Public Key does not exist")
            self._write()
        return True

    def modify(self,target:str) -> bool: # type: ignore[override]
        """Modify Existing on Target
        @param bool Success/Failure
        @throws NotImplementedError This function should be overwritten, do not use super()
        """
        raise NotImplementedError(f"{type(self).__qualname__} does not implement modify")
    # pylint: enable=arguments-differ

    def __find_and_remove(self,user:str,access_key_id:typing.Union[str,None] = None,public_key:typing.Union[str,None] = None) -> bool:
        """Scan and Remove Access Key ID / Public Key
        @param str \c user Username operate on
        @param Union[str,None] \c access_key_id Access Key ID to remove. Default None
        @param Union[str,None] \c public_key Public Key to remove. Default None
        @retval bool Success / Failure
        @raises AuthDBNotLoadedError AuthDB was not Loaded
        """
        removed:bool = False
        if not self._opened or self._authdb is None:
            self._close()
            raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        userobj:AuthDBUser = self._authdb["users"][user]
        if user in self._protected_users and len(userobj.keys) == 1:
            self.logger.warning("Attempted to Remove the only Access Key ID associated with a protected user")
            self._close()
            raise ProtectedUserError("Attempted to Remove the only Access Key ID associated with a protected user")
        for idx in range(0,len(userobj.keys)):
            if removed:
                break
            key:dict[str,str] = userobj.keys[idx]
            if access_key_id is not None:
                if access_key_id == key["access_key_id"]:
                    self.logger.info("Requested Access Key ID found, removing")
                    userobj.keys.pop(idx)
                    removed = True
                    continue
            if public_key is not None:
                if public_key == key["pubkey"]:
                    self.logger.info("Requested Public Key found, removing")
                    userobj.keys.pop(idx)
                    removed = True
                    continue
        if len(userobj.keys) == 0:
            self.logger.info("User no longer has any Access Keys, removing completely")
            self._authdb.pop(user)
        return removed
# pylint: enable=duplicate-code
