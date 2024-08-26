# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.secrets.server.uacl import ACLContainer,ACLCommand,ACLObject,ACLStore
from convection.secrets.objects.authdb.token import AuthDBToken

class AuthDBUser:
    """AuthDB User Container
    """
    _name:str
    keys:list[dict[str,str]]
    tokens:list[AuthDBToken]
    acls:ACLContainer

    @property
    def name(self) -> str:
        """User Name this object belongs to
        @retval str User Name
        """
        return self._name

    def __init__(self,name:str,keys:list[dict[str,str]],tokens:list[AuthDBToken],acls:typing.Union[ACLContainer,list[typing.Union[ACLObject,ACLCommand,ACLStore]]]) -> None:
        """Initializer
        @param str \c name User Name
        @param list[dict[str,str]] \c keys Access Key ID / Public Key Pairs
        @param list[AuthDBToken] \c tokens Auth Tokens
        @param Union[ACLContainer,list[Union[ACLObject,ACLCommand,ACLStore]]] \c acls ACL Container or List of ACLs to create an ACL Container from
        """
        self._name = name
        self.keys = keys
        if isinstance(acls,ACLContainer):
            self.acls = acls
        else:
            self.acls = ACLContainer(acls)
        self.tokens = tokens

    def data(self) -> dict[str,typing.Any]:
        """Dictionary Dump
        @retval dict[str,Any] User Object as Dictionary
        """
        return {
            "tokens": [ token.data() for token in self.tokens ],
            "keys": self.keys,
            "acls": self.acls.acl_names
        }
