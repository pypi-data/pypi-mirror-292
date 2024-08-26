# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
from pathlib import Path

from convection.shared.functions import load_types
from convection.shared.exceptions import AuthDBNotLoadedError
from convection.shared.objects.plugins.secret import ConvectionPlugin_Secret
from convection.shared.objects.plugin_metadata import ConvectionPluginMetadata

from convection.secrets.objects.authdb.user import AuthDBUser
from convection.secrets.objects.authdb.token import AuthDBToken
from convection.secrets.server.uacl import ACLContainer, ACLObject
from convection.secrets.server.authdb.core import ConvectionAuthDBCore
from convection.secrets.server.authdb.acl import ConvectionAuthDBACL
from convection.secrets.server.authdb.auth import ConvectionAuthDBAuth
from convection.secrets.server.authdb.group import ConvectionAuthDBGroup
from convection.secrets.server.authdb.user import ConvectionAuthDBUser

# pylint: disable=abstract-method
class ConvectionSecretsAuthDB(ConvectionAuthDBACL,ConvectionAuthDBGroup,ConvectionAuthDBUser,ConvectionAuthDBAuth,ConvectionAuthDBCore,ConvectionPlugin_Secret):
    """Convection Secrets AuthDB Store
    Stores User/Public Key Maps, UACLs, Groups, Active AuthTokens
    """

    _authdb:typing.Union[None,dict[str,typing.Any]]

    # pylint: disable=unused-argument
    def __init__(self, name: str, keys: list[bytes], storage_path: Path, store_config: typing.Union[dict[str, typing.Any],None] = None) -> None:
        """Initializer
        @param str \c name Store Name (not used)
        @param list[bytes] \c keys Decryption Keys
        @param Path \c storage_path Secrets Storage Root
        """
        self._opened = False
        self.metadata = ConvectionPluginMetadata({
            "version": "1.0.0",
            "author": "AccidentallyTheCable <cableninja@cableninja.net>",
            "updated": 20231204,
            "compatibility": ">=:1.0,<:2.0",
            "plugin": {
                "name": "AuthDB",
                "type": "Secret",
                "description": "Convection Secrets Manager AuthDB Store"
            }
        })
        super().__init__("authdb",keys,storage_path)
        self._acl_types = load_types("convection.secrets.server.uacl",ACLObject)
        self._store_path = storage_path.joinpath("auth.db")
        self._authdb = None
    # pylint: enable=unused-argument

    def info(self) -> dict[str,typing.Any]:
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            acl_container:ACLContainer = self._authdb["acls"]
            active_tokens:int = 0
            userobj:AuthDBUser
            for userobj in self._authdb["users"]:
                active_tokens += len(userobj.tokens)
            out:dict[str,typing.Any] = {
                "user_count": len(self._authdb["users"]),
                "group_count": len(self._authdb["groups"]),
                "acl_count": len(acl_container.acl_names),
                "active_auth_tokens": active_tokens
            }
        return out

    def initialize(self) -> None:
        with self.tlock:
            self._opened = True
            if self.metadata is None:
                raise AttributeError("AuthDB did not have a Metadata object")
            self._authdb = {
                "metadata": self.metadata.get(),
                "users": {},
                "groups": {},
                "acls": ACLContainer()
            }
            self._write()
            self._close()

    def cleanup(self) -> bool:
        """AuthDB Cleanup; Cleanup Expired Auth Tokens
        @retval bool Whether any Auth Tokens were removed
        @raises AuthDBNotLoaded AuthDB is not Loaded
        """
        total_tokens:int = 0
        cleared_tokens:int = 0
        with self.tlock:
            self._read()
            if not self._opened or self._authdb is None:
                self._close()
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
            userobj:AuthDBUser
            for userobj in self._authdb["users"].values():
                tokens:list[AuthDBToken] = userobj.tokens.copy()
                # Possible bugfix for below bug, going to leave everything just in case.
                tokens.reverse()
                userobj.tokens.reverse()
                for token_idx in range(len(tokens)):
                    token:AuthDBToken = tokens[token_idx]
                    if token.expired or token.force_expire:
                        cleared_tokens += 1
                        # bug: Token Index out of Range on Unlock
                        ## Weird WTF Bug??? Sometimes This loop will go 'index out of range' on unlock.
                        ##  Doing this check and break stops the out of range error. Debug info is there because eventually ill sort this.
                        ##  After a successful unlock, this no longer matters though apparently? Perhaps this was from a crash that did somethin weird?
                        ## After Unlock, the parent block Runs, and will clean some expired tokens, more than there should be, but it eventually settles
                        if token_idx >= len(userobj.tokens):
                            self.logger.warning(f"BUG Hit; - Token Index out of Range on Unlock. Tried idx: {token_idx}, but user userdata['tokens'] len: {len(tokens)}")
                            break
                        userobj.tokens.pop(token_idx)
                        continue
                    total_tokens += 1
                # self.__authdb["users"][user] = userdata
            self._write()
        if cleared_tokens > 0:
            self.logger.info(f"Cleared {str(cleared_tokens)} Expired AuthToken(s); Total Active: {str(total_tokens)}")
        return cleared_tokens > 0
# pylint: enable=abstract-method
