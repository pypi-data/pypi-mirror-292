# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.shared.exceptions import AuthDBNotLoadedError, GroupExistsError, GroupNotExistError, InvalidUserError

from convection.secrets.objects.authdb.group import AuthDBGroup
from convection.secrets.objects.authdb.user import AuthDBUser
from convection.secrets.server.authdb.core import ConvectionAuthDBCore

# pylint: disable=duplicate-code
class ConvectionAuthDBGroup(ConvectionAuthDBCore):
    """Convection AuthDB Group Management"""

    def group_audit(self,group_name:str) -> dict[str,typing.Any]:
        """Get ACLs, in full, that Group contains, Users in Group
        @param str \c group_name Name of Group to get ACLs of
        @retval dict[str,Any] List of ACLs that Group has attached, Users in Group
        """
        result:dict[str,typing.Any] = {}
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            if group_name not in groups.keys():
                raise GroupNotExistError(group_name)
            group:AuthDBGroup = groups[group_name]
            result["acls"] = group.acls.acl_names
            result["users"] = [ u.name for u in group.users ]
            self._close()
        return result

    def group_list(self) -> list[str]:
        """List of Groups
        @retval list[str] List of Group Names
        """
        group_names:list[str] = []
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            group_names = [ u.name for u in groups.values() ]
            self._close()
        return group_names

    def group_create(self,name:str) -> bool:
        """Create Group, must be unique name
        @param str \c name Group Name
        @retval bool Creation Success / Failure
        @raises AuthDBNotLoadedError AuthDB not loaded
        @raises GroupExistsError Group Name already exists
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            if name in groups.keys():
                self._close()
                self.logger.error(f"Group {name} already exists")
                raise GroupExistsError(f"Group {name} exists")
            groups[name] = AuthDBGroup(name,[],[])
            self._authdb["groups"] = groups
            self.logger.info(f"Created Group '{name}'")
            self._write()
            self._close()
        return True

    def group_destroy(self,group_name:str) -> bool:
        """Destroy/Remove a Group
        @param str \c group_name Name of Group to Remove
        @retval bool Success/Failure
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            if group_name not in groups.keys():
                self._close()
                self.logger.error(f"Group '{group_name}' does not exist")
                return False
            group:AuthDBGroup = groups[group_name]
            self._authdb["groups"].pop(group.name)
            self.logger.info(f"Removing Group '{group_name}' Completely")
            self._write()
            self._close()
        return True

    def detach_group(self,group_name:str,user_name:str) -> bool:
        """Remove Group from User
        @param str \c group_name Group Name to detach
        @param str \c user_name User name to Remove from Group
        @retval bool Success / Failure
        @raises AuthDBNotLoadedError AuthDB not loaded
        @raises GroupNotExistsError Group Name does not exist
        @raises InvalidUserError No Such User
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            users:dict[str,AuthDBUser] = self._authdb["users"]
            if user_name not in users.keys():
                self._close()
                self.logger.error(f"Invalid User '{user_name}'")
                raise InvalidUserError(f"No Such User {user_name}")
            if group_name not in groups.keys():
                self._close()
                self.logger.error(f"Invalid Group '{group_name}'")
                raise GroupNotExistError(f"No Such Group {group_name}")
            if user_name not in groups[group_name].usernames:
                self.logger.debug(groups[group_name].data())
                self._close()
                self.logger.debug(f"User '{user_name}' was not in group '{group_name}'")
                return False
            group:AuthDBGroup = groups[group_name]
            user:AuthDBUser = users[user_name]
            group.users.pop(group.users.index(user))
            self.logger.info(f"Removed user '{user_name}' from group '{group_name}'")
            self._write()
            self._close()
        return True

    def attach_group(self,group_name:str,user_name:str) -> bool:
        """Attach Group to User
        @param str \c group_name Group Name to attach
        @param str \c user_name User Name to attach group to
        @retval bool Success / Failure
        @raises AuthDBNotLoadedError AuthDB not loaded
        @raises GroupNotExistsError Group Name does not exist
        @raises InvalidUserError No Such User
        """
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            groups:dict[str,AuthDBGroup] = self._authdb["groups"]
            users:dict[str,AuthDBUser] = self._authdb["users"]
            if user_name not in users.keys():
                self._close()
                self.logger.error(f"Invalid User '{user_name}'")
                raise InvalidUserError(f"No Such User {user_name}")
            if group_name not in groups.keys():
                self._close()
                self.logger.error(f"Invalid Group '{group_name}'")
                raise GroupNotExistError(f"No Such Group {group_name}")
            groups[group_name].users.append(users[user_name])
            self._authdb["groups"] = groups
            self.logger.info(f"Added user '{user_name}' to group '{group_name}'")
            self._write()
            self._close()
        return True
# pylint: enable=duplicate-code
