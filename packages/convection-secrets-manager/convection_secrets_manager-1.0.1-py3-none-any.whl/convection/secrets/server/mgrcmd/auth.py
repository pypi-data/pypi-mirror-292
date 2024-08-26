# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
from datetime import timedelta

from atckit.utilfuncs import UtilFuncs

from convection.shared.exceptions import SystemLockedWarning, AuthDBNotLoadedError

from convection.secrets.server.mgrcmd.core import ConvectionManagerCommandCore


class ConvectionManagerAuthCommands(ConvectionManagerCommandCore):
    """Secrets Manager Auth Management Commands"""

    # pylint: disable=duplicate-code
    def init_authorize(self,access_key_id:str,expire_time:typing.Union[str,None] = None) -> str:
        """Authorization / Login Start
        @param str \c access_key_id User's Access Key ID
        @param Union[str,None] \c expire_time Expiration Time, See API for format. Default None. Cannot exceed `manager.authentication.token_max_expire`
        @retval str Encrypted AuthToken
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises SystemLocked System is in Locked State, has not been Unlocked
        @raises AuthDBNotLoaded AuthDB is not Loaded
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Lock, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._authdb is None:
            self._load_authdb()
            if self._authdb is None:
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        max_expire:str = self.config.get_configuration_value("manager.authentication.token_max_expire")
        max_expire_time:timedelta = UtilFuncs.deltatime_str(max_expire)
        token_expire_time:timedelta
        if expire_time is None:
            self.logger.debug(f"Client did not specify expire time, defaulting to max {max_expire_time}")
            token_expire_time = max_expire_time
        else:
            requested_expire_time:timedelta = UtilFuncs.deltatime_str(expire_time)
            if requested_expire_time > max_expire_time:
                self.logger.warning("Requested Token Expire time is longer than configured Max Expire")
                token_expire_time = max_expire_time
            else:
                token_expire_time = requested_expire_time
        self.logger.debug(f"Setting Token Expire time to {token_expire_time}")
        return str(self._authdb.init_authorize(access_key_id,token_expire_time))

    def authorize(self,access_key_id:str,auth_token:str) -> bool:
        """Authorization Verification / Complete; Shortcut for calling authdb_comannd
        @param str \c access_key_id User's Access Key ID
        @param str \c auth_token Decrypted AuthToken
        @retval bool Authorized/Not Authorized
        """
        result:bool = self.authdb_command("verify_authorize",[access_key_id,auth_token])
        return result

    def deauth(self,access_key_id:str,auth_token:str) -> bool:
        """Deauth / Logout; Shortcut for calling authdb_comannd
        @param str \c access_key_id User's Access Key ID
        @param str \c auth_token Decrypted AuthToken
        @retval Deauth Success/Failure (Already Deauthed)
        """
        result:bool = self.authdb_command("deauth",[access_key_id,auth_token])
        return result

    def authdb_command(self,command:str,args:typing.Union[list[typing.Any],None] = None) -> typing.Any:
        """Command Passthrough for AuthDB activities
        @param str \c command Command to Run, must be a valid method from ConvectionSecretsAuthDB
        @param Union[list[Any],None] \c args Arguments for Command, default is None
        @retval Any Return data of executed Command
        @raises FileNotFoundError Root Key doesnt exist, so not initialized
        @raises SystemLocked System is in Locked State, has not been Unlocked
        @raises AuthDBNotLoaded AuthDB is not Loaded
        """
        if not self.initialized:
            raise FileNotFoundError("Cannot Cleanup AuthDB, Not Initialized.")
        if self.locked:
            raise SystemLockedWarning()
        if self._authdb is None:
            self._load_authdb()
            if self._authdb is None:
                self.logger.error("AuthDB is not currently opened")
                raise AuthDBNotLoadedError("AuthDB is Not Loaded")
        if command not in self._authdb_action_map:
            raise NameError(f"No such Command {command}")
        action:typing.Callable = self._authdb_action_map[command]
        if args is None:
            return action()
        return action(*args)
    # pylint: enable=duplicate-code
