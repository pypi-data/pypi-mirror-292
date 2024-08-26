# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import logging
import threading
import typing

from atckit.utilfuncs import UtilFuncs

from convection.shared.objects.plugin_metadata import ConvectionPluginMetadata
from convection.shared.exceptions import AuthDBNotLoadedError, InvalidAccessKeyError

from convection.secrets.objects.authdb.user import AuthDBUser
from convection.secrets.objects.authdb.group import AuthDBGroup
from convection.secrets.objects.authdb.token import AuthDBToken
from convection.secrets.server.uacl import ACLCommand, ACLContainer, ACLObject, ACLStore

# pylint: disable=no-member
class ConvectionAuthDBCore:
    """Convection AuthDB Core Functionality"""

    logger:logging.Logger

    ATTACH_ACL_USER:int = 0
    ATTACH_ACL_GROUP:int = 1

    tlock:threading.Lock
    _authdb:typing.Union[None,dict[str,typing.Any]]

    _protected_users:list[str] = [ "root", "recovery" ]
    _acl_types:dict[str,typing.Type]
    _opened:bool

    def _accesskey_map(self) -> dict[str,list[str]]:
        """Access Key Map Generation, Generate User:Access Key ID map
        @retval dict[str,list[str]] User, Access Key ID
        @raises AuthDBNotLoaded AuthDB is not Loaded
        """
        if not self._opened or self._authdb is None:
            self.logger.error("AuthDB is not currently opened")
            raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        out:dict[str,list[str]] = {}
        userobj:AuthDBUser
        for u,userobj in self._authdb["users"].items():
            out[u] = []
            for pair in userobj.keys:
                out[u].append(pair["pubkey"])
        return out

    def _publickey_map(self) -> dict[str,list[str]]:
        """Access Key Map Generation, Generate User:Access Key ID map
        @retval dict[str,list[str]] User, Access Key ID
        @raises AuthDBNotLoaded AuthDB is not Loaded
        """
        if not self._opened or self._authdb is None:
            self.logger.error("AuthDB is not currently opened")
            raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        out:dict[str,list[str]] = {}
        userobj:AuthDBUser
        for u,userobj in self._authdb["users"].items():
            out[u] = []
            for pair in userobj.keys:
                out[u].append(pair["access_key_id"])
        return out

    def _get_user_by_accesskey(self,access_key_id:str) -> str:
        """Find Username by Access Key ID
        @param str \c access_key_id Access Key ID
        @retval str User
        @raises AuthDBNotLoaded AuthDB is not Loaded
        @raises InvalidAccessKey Access key does not exist or is invalid format
        """
        if not self._opened or self._authdb is None:
            self.logger.error("AuthDB is not currently opened")
            raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        for u,keys in self._publickey_map().items():
            if access_key_id in keys:
                return u
        raise InvalidAccessKeyError(access_key_id)

    def _get_user_by_publickey(self,public_key:str) -> str:
        """Find Username by PublicKey
        @param str \c public_key PublicKey
        @retval str User
        @raises AuthDBNotLoaded AuthDB is not Loaded
        @raises InvalidAccessKey Access key does not exist or is invalid format
        """
        if not self._opened or self._authdb is None:
            self.logger.error("AuthDB is not currently opened")
            raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        for u,keys in self._accesskey_map().items():
            if public_key in keys:
                return u
        raise InvalidAccessKeyError(public_key)

    def _read(self) -> None:
        if self._opened:
            return
        self._opened = True
        with open(self._store_path,"rb") as f: # type: ignore[attr-defined]
            raw:bytes = self._encryptor.decrypt(f.read()) # type: ignore[attr-defined]
            rawdb:dict[str,typing.Any] = UtilFuncs.load_sstr(raw.decode("utf-8"),"toml")
            # self.logger.debug(json.dumps(rawdb,indent=4))
            if not self._compat_checked: # type: ignore[attr-defined]
                old_metadata:ConvectionPluginMetadata = ConvectionPluginMetadata(rawdb["metadata"])
                self.compat_check(old_metadata)  # type: ignore[attr-defined]
            self._authdb = {
                "users": {},
                "groups": {},
            }
            acls:list[typing.Union[ACLObject,ACLCommand,ACLStore]] = []
            for acl in rawdb["acls"]:
                obj_type_name:str = acl.pop("object")
                obj_type:typing.Type = self._acl_types[obj_type_name]
                acl_obj:typing.Union[ACLObject,ACLCommand,ACLStore] = obj_type(**acl)
                acls.append(acl_obj)
            self._authdb["acls"] = ACLContainer(acls)

            for user,userdata in rawdb["users"].items():
                user_tokens:list[AuthDBToken] = [ AuthDBToken(t) for t in userdata["tokens"] ]
                userdata["tokens"] = user_tokens
                user_acls:list[typing.Union[ACLObject,ACLCommand,ACLStore]] = [ acl for acl in acls if acl.name in userdata["acls"] ]
                userdata["acls"] = user_acls
                self._authdb["users"][user] = AuthDBUser(user,**userdata)

            for group,groupdata in rawdb["groups"].items():
                group_users:list[AuthDBUser] = [ u for u in self._authdb["users"].values() if u.name in groupdata["users"] ]
                group_acls:list[typing.Union[ACLObject,ACLCommand,ACLStore]] = [ acl for acl in acls if acl.name in groupdata["acls"] ]
                self._authdb["groups"][group] = AuthDBGroup(group,group_users,group_acls)

    def _write(self) -> None:
        self._shuffle() # type: ignore[attr-defined]
        if not self._opened or self._authdb is None:
            self.logger.error("AuthDB is not currently opened")
            raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        if self.metadata is None: # type: ignore[attr-defined]
            raise SystemError("AuthDB did not have a Metadata object")
        users:dict[str,AuthDBUser] = self._authdb["users"]
        groups:dict[str,AuthDBGroup] = self._authdb["groups"]
        acls:ACLContainer = self._authdb["acls"]
        outdb:dict[str,typing.Any] = {
            "metadata": self.metadata.get(), # type: ignore[attr-defined]
            "users": { user.name: user.data() for user in users.values() },
            "groups": { group.name: group.data() for group in groups.values() },
            "acls": acls.data()
        }

        with open(self._store_path,"wb") as f: # type: ignore[attr-defined]
            raw:bytes = bytes(UtilFuncs.dump_sstr(outdb,"toml"),"utf-8")
            f.write(self._encryptor.encrypt(raw)) # type: ignore[attr-defined]
        self._store_path.chmod(0o600) # type: ignore[attr-defined]
        self._close()

    def _close(self) -> None:
        if self._authdb is not None:
            self._authdb["users"].clear()
            self._authdb.clear()
        self._opened = False
        self._authdb = None
# pylint: disable=no-member
