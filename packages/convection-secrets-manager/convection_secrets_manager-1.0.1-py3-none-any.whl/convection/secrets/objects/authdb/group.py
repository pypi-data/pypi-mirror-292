# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.secrets.objects.authdb.user import AuthDBUser
from convection.secrets.server.uacl import ACLCommand,ACLContainer,ACLObject,ACLStore

class AuthDBGroup:
    """AuthDB Group Container
    """
    _name:str
    _users:list[AuthDBUser]

    acls:ACLContainer

    @property
    def users(self) -> list[AuthDBUser]:
        """Users in Group
        @retval list[AuthDBUser] List of User Objects attached to Group
        """
        return self._users

    @property
    def usernames(self) -> list[str]:
        """Usernames in Group
        @retval list[str] List of Usernames attached to Group
        """
        return [ u.name for u in self._users ]

    @property
    def name(self) -> str:
        """Group Name
        @retval str Group Name
        """
        return self._name

    def __init__(self,name:str,users:list[AuthDBUser],acls:typing.Union[ACLContainer,list[typing.Union[ACLObject,ACLCommand,ACLStore]]]) -> None:
        """Initializer
        @param str \c name Group Name
        @param list[AuthDBUser] \c user List of Users attached to Group
        @param Union[ACLContainer,list[Union[ACLObject,ACLCommand,ACLStore]]] \c acls ACL Container or List of ACLs to create an ACL Container from
        """
        self._name = name
        self._users = users
        if isinstance(acls,ACLContainer):
            self.acls = acls
        else:
            self.acls = ACLContainer(acls)

    def data(self) -> dict[str,typing.Any]:
        """Dictionary Dump
        @retval dict[str,Any] User Object as Dictionary
        """
        return {
            "users": [ user.name for user in self.users ],
            "acls": self.acls.acl_names
        }
