# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.shared.exceptions import ACLExistsError, ACLNotExistError, AuthDBNotLoadedError, GroupNotExistError, InvalidAccessKeyError, InvalidUserError
from convection.shared.functions import access_mode_to_access_str

from convection.secrets.objects.authdb.user import AuthDBUser
from convection.secrets.objects.authdb.group import AuthDBGroup
from convection.secrets.server.uacl import ACLCommand, ACLContainer, ACLObject, ACLStore
from convection.secrets.server.authdb.core import ConvectionAuthDBCore

# pylint: disable=duplicate-code
class ConvectionAuthDBACL(ConvectionAuthDBCore):
    """Convection AuthDB ACL Management"""

    def detach_acl(self,acl_name:str,detach_type:int,detach_name:str) -> bool:
        """Remove ACL from User or Group
        @param str \c acl_name ACL Name to Remove from User/Group
        @param int \c detach_type Type of Removal (ConvectionSecretsAuthDB.ATTACH_ACL_*)
        @param str \c detach_name Name of User or Group to remove ACL from
        @retval bool Success/Failure
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            if acl_name not in self._authdb["acls"].acl_names:
                self._close()
                self.logger.error(f"ACL '{acl_name}' does not exist")
                raise ACLNotExistError(f"{acl_name} does not exist")
            acl:typing.Union[ACLObject,ACLCommand,ACLStore,None] = self._authdb["acls"].get_by_name(acl_name)
            detach_type_str:str = ""
            if acl is None:
                self._close()
                self.logger.critical(f"POSSIBLE BUG; ACL '{acl_name}' should exist, but was not found")
                raise ACLNotExistError(f"ACL '{acl_name}' should exist, but was not found")
            acl_container:ACLContainer
            if detach_type == self.ATTACH_ACL_GROUP:
                detach_type_str = "Group"
                groups:dict[str,AuthDBGroup] = self._authdb["groups"]
                if detach_name not in groups.keys():
                    self._close()
                    self.logger.error(f"Invalid Group '{detach_name}'")
                    raise GroupNotExistError(f"No Such Group {detach_name}")
                acl_container = groups[detach_name].acls
            elif detach_type == self.ATTACH_ACL_USER:
                detach_type_str = "User"
                users:dict[str,AuthDBUser] = self._authdb["users"]
                if detach_name not in users.keys():
                    self._close()
                    self.logger.error(f"Invalid User '{detach_name}'")
                    raise InvalidUserError(f"No Such User {detach_name}")
                acl_container = users[detach_name].acls
            else:
                self._close()
                self.logger.error(f"Invalid Attachment Type '{str(detach_type)}")
                raise ValueError("Invalid Attachment Type")
            acl_container.remove_acl(acl_name)
            self.logger.info(f"Removed ACL '{acl_name}' from {detach_type_str} '{detach_name}'")
            self._write()
            self._close()
        return True

    def attach_acl(self,acl_name:str,attach_type:int,attach_name:str) -> bool:
        """Attach ACL to User or Group
        @param str \c acl_name ACL Name to attach
        @param int \c attach_to_type Attachment Type, a ConvectionSecretsAuthDB.ATTACH_ACL_* value
        @param str \c attach_name Name of User or Group to attach to
        @retval bool Success / Failure
        @raises AuthDBNotLoadedError AuthDB not loaded
        @raises ACLNotExistError No Such ACL
        @raises ACLNotExistError Possible Bug, ACL should exist but was not found
        @raises InvalidUserError No Such User
        @raises GroupNotExistError No Such Group
        @raises ValueError Invalid Attachment Type (not a ConvectionSecretsAuthDB.ATTACH_ACL_* value)
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            acl_container:ACLContainer = self._authdb["acls"]
            if acl_name not in acl_container.acl_names:
                self._close()
                self.logger.error(f"ACL '{acl_name}' does not exist")
                raise ACLNotExistError(f"{acl_name} does not exist")
            acl:typing.Union[ACLObject,ACLCommand,ACLStore,None] = acl_container.get_by_name(acl_name)
            attach_type_str:str = ""
            if acl is None:
                self._close()
                self.logger.critical(f"POSSIBLE BUG; ACL '{acl_name}' should exist, but was not found")
                raise ACLNotExistError(f"ACL '{acl_name}' should exist, but was not found")
            if attach_type == self.ATTACH_ACL_USER:
                users:dict[str,AuthDBUser] = self._authdb["users"]
                if attach_name not in users.keys():
                    self._close()
                    self.logger.error(f"Invalid User '{attach_name}'")
                    raise InvalidUserError(f"No Such User {attach_name}")
                users[attach_name].acls.acls.append(acl)
                self._authdb["users"] = users
                attach_type_str = "User"
            elif attach_type == self.ATTACH_ACL_GROUP:
                groups:dict[str,AuthDBGroup] = self._authdb["groups"]
                if attach_name not in groups.keys():
                    self._close()
                    self.logger.error(f"Invalid Group '{attach_name}'")
                    raise GroupNotExistError(f"No Such Group {attach_name}")
                groups[attach_name].acls.acls.append(acl)
                self._authdb["groups"] = groups
                attach_type_str = "Group"
            else:
                self._close()
                self.logger.error(f"Invalid Attachment Type '{str(attach_type)}")
                raise ValueError("Invalid Attachment Type")
            self.logger.info(f"Attached ACL '{acl_name}' to {attach_type_str} '{attach_name}'")
            self._write()
            self._close()
        return True

    def acl_check(self,command_access_mode:int, access_key_id:str, command:typing.Union[str,None], data:typing.Union[dict[str,typing.Any],None]) -> int:
        """Perform ACL Check against Access Key ID
        @param int \c command_access_mode Access Mode that Command requires
        @param str \c access_key_id Access Key ID to perform check against
        @param str \c command Command being Executed
        @param Union[dict[str,Any],None] \c data Command Data being Executed
        @retval int ACLObject.MODE_* Result
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            try:
                user:str = self._get_user_by_accesskey(access_key_id)
            except InvalidAccessKeyError as e:
                self.logger.warning("Attempt to access with Invalid Access Key")
                self._close()
                raise InvalidAccessKeyError from e
            acl_container:ACLContainer = ACLContainer()
            userobj:AuthDBUser = self._authdb["users"][user]
            acl_container.merge(userobj.acls)
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            for g in groups.values():
                if user in g.usernames:
                    acl_container.merge(g.acls)
            store_path:typing.Union[str,None] = None
            secret_name:typing.Union[str,None] = None
            store_info:str = str("")
            if data is not None:
                if "store_path" in data.keys():
                    store_path = str(data["store_path"])
                    store_info += store_path
                elif "store_name" in data.keys():
                    store_path = str(data["store_name"])
                    store_info += store_path
                if "secret_name" in data.keys():
                    secret_name = str(data["secret_name"])
                    if len(store_info) > 0:
                        store_info += ":"
                    store_info += secret_name
                elif "store_args" in data.keys():
                    if "secret_name" in data["store_args"].keys():
                        secret_name = str(data["store_args"]["secret_name"])
                        if len(store_info) > 0:
                            store_info += ":"
                        store_info += secret_name
            result:int = acl_container.check(command_access_mode,command,store_path,secret_name)
            access_mode_str:str = access_mode_to_access_str(command_access_mode)
            if result != ACLObject.MODE_ALLOW:
                self.logger.warning(f"{user}@{access_key_id} attempted to execute {command}({access_mode_str}){store_info}, ACL disallowed it")
            else:
                self.logger.info(f"Allowing {user}@{access_key_id} to execute {command}({access_mode_str}){store_info}")
            self._close()
        return result

    def acl_create(self,name:str,acl_type:str,acl_args:dict[str,typing.Any]) -> bool:
        """Create ACL
        @param str \c name Name of ACL (must be unique)
        @param str \c acl_type Type of ACL (see Documentation for ACL Types )
        @raises AuthDBNotLoadedError AuthDB not loaded
        @raises ACLExistsError ACL Name already exists
        @raises TypeError Invalid ACL Type
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            acl_container:ACLContainer = self._authdb["acls"]
            if name in acl_container.acl_names:
                self._close()
                self.logger.error(f"ACL {name} already exists")
                raise ACLExistsError(f"ACL {name} exists")
            if acl_type not in self._acl_types.keys():
                self._close()
                self.logger.error(f"'{acl_type}' is not a valid ACL type")
                raise TypeError(f"{acl_type} is not a valid ACL Type")
            acl_obj_type:typing.Type = self._acl_types[acl_type]
            acl_obj:"acl_obj_type" = acl_obj_type(name,**acl_args) # type: ignore[valid-type]
            acl_container.acls.append(acl_obj)
            self.logger.info(f"Created ACL '{name}', type: {acl_type}, args: {acl_args}")
            self._write()
            self._close()
        return True

    def acl_list(self) -> list[str]:
        """List of ACLs
        @retval list[dict[str,Any]] List of ACLs, with their ACL data
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            acls:ACLContainer = self._authdb["acls"]
            acl_names:list[str] = acls.acl_names
            self._close()
        return acl_names

    def acl_destroy(self,acl_name:str) -> bool:
        """Removed/Destroy an ACL Item and associations with it
        @param str \c acl_name Name of ACL to delete
        @retval bool Success/Failure
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            acl_container:ACLContainer = self._authdb["acls"]
            if acl_name not in acl_container.acl_names:
                self._close()
                self.logger.error(f"ACL '{acl_name}' does not exist")
                return False
            acl:typing.Union[ACLObject,ACLCommand,ACLStore,None] = acl_container.get_by_name(acl_name)
            if acl is None:
                self._close()
                self.logger.critical(f"POSSIBLE BUG; ACL '{acl_name}' should exist, but was not found")
                raise ACLNotExistError(f"ACL '{acl_name}' should exist, but was not found")
            users:dict[str,AuthDBUser] = self._authdb["users"]
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            for user in users.values():
                if acl_name in user.acls.acl_names:
                    self.logger.info(f"Removed ACL {acl_name} from User {user.name}")
                    user.acls.remove_acl(acl_name)
            for group in groups.values():
                if acl_name in group.acls.acl_names:
                    self.logger.info(f"Removed ACL {acl_name} from Group {group.name}")
                    group.acls.remove_acl(acl_name)
            self.logger.info(f"Removing ACL '{acl_name}' Completely")
            acl_container.remove_acl(acl_name)
            self._write()
            self._close()
        return True

    def acl_audit(self,acl_name:str) -> dict[str,typing.Any]:
        """Show ACL content
        @param str \c acl_name Name of ACL to show
        @retval dict[str,Any] ACL Data
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            if acl_name not in self._authdb["acls"].acl_names:
                self._close()
                self.logger.error(f"ACL '{acl_name}' does not exist")
                raise ACLNotExistError(f"{acl_name} does not exist")
            acl:typing.Union[ACLObject,ACLCommand,ACLStore,None] = self._authdb["acls"].get_by_name(acl_name)
            if acl is None:
                self._close()
                self.logger.critical(f"POSSIBLE BUG; ACL '{acl_name}' should exist, but was not found")
                raise ACLNotExistError(f"ACL '{acl_name}' should exist, but was not found")
            acl_data:dict[str,typing.Any] = acl.data()
            acl_data["object"] = type(acl).__qualname__
            self._close()
        return acl_data
# pylint: enable=duplicate-code
