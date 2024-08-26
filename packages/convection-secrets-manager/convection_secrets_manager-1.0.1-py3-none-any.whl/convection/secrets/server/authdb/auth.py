# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import base64
import datetime
import typing
from uuid import UUID, uuid4


from cryptography.hazmat.backends import default_backend
# Older Cryptography libraries less than v42.0 had RSAPublicKey hidden behind the backends
# Newer versions (v42.0+) now have it available in the asymmetric.rsa module
# pylint: disable=import-error
# pylint: disable=no-name-in-module
try:
    from cryptography.hazmat.backends.openssl.rsa import RSAPublicKey as PublicKey
except ModuleNotFoundError:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey as PublicKey
# pylint: enable=import-error
# pylint: enable=no-name-in-module

from cryptography.hazmat.primitives.serialization import load_der_public_key,load_pem_public_key
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.asymmetric.padding import OAEP,MGF1

from convection.shared.exceptions import AuthDBNotLoadedError, InvalidAccessKeyError, InvalidAuthTokenError, InvalidPubKeyError

from convection.secrets.server.authdb.core import ConvectionAuthDBCore
from convection.secrets.objects.authdb.user import AuthDBUser
from convection.secrets.objects.authdb.token import AuthDBToken

# pylint: disable=duplicate-code
class ConvectionAuthDBAuth(ConvectionAuthDBCore):
    """Convection AuthDB Authorization / Access Commands"""

    def deauth(self,access_key_id:str,auth_token:str) -> bool:
        """Deauth / Logout
        @param str \c access_key_id Access Key ID
        @param str \c auth_token Auth Token
        @retval bool Deauth Success/Failure (already deauthed)
        @raises AuthDBNotLoaded AuthDB is not Loaded
        @raises InvalidAccessKey Access key does not exist or is invalid format
        @raises InvalidAuthToken Auth Token does not exist or is invalid / expired
        """
        if not self.verify_authorize(access_key_id,auth_token):
            self.logger.warning(f"Attempted deauth for Access Key ID {access_key_id} with a token that was not valid")
            return False
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
            userobj:AuthDBUser = self._authdb["users"][user]
            in_token:bytes = UUID(hex=auth_token).bytes
            discovered_token:bool = False
            for token_obj in userobj.tokens:
                if token_obj.token == in_token:
                    discovered_token = True
                    token_obj.force_expire = True
                    break
            if not discovered_token:
                raise InvalidAuthTokenError("No such token")
            if discovered_token:
                self.logger.debug(f"Successfully Deauthed {access_key_id}")
                self._write()
            self._close()
        return True

    def verify_authorize(self,access_key_id:str,auth_token:str) -> bool:
        """Authorization Check / Login Stage 2
        @param str \c access_key_id Access Key ID
        @param str \c auth_token Auth Token
        @retval bool Valid Token
        @raises AuthDBNotLoaded AuthDB is not Loaded
        @raises InvalidAccessKey Access key does not exist or is invalid format
        Used for Second half of `authorize` command, and for verification of auth-required commands
        """
        self.logger.debug(f"Verifying Authentication for ID: {access_key_id}")
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
            userobj:AuthDBUser = self._authdb["users"][user]
            valid_token:bool = False
            discovered_token:typing.Union[AuthDBToken,None] = None
            try:
                in_token:bytes = UUID(hex=auth_token).bytes
            except ValueError as e:
                self.logger.warning(f"Authentication Failed for {user}@{access_key_id}, AuthToken that was sent was not a valid token")
                self._close()
                raise InvalidAuthTokenError("Invalid Authentication Token") from e
            for token_obj in userobj.tokens:
                if token_obj.token == in_token:
                    discovered_token = token_obj
                    valid_token = True
                    break
            if not valid_token or discovered_token is None:
                self.logger.warning(f"Authentication Failed for {user}@{access_key_id}, AuthToken that was sent was not a valid token")
                self._close()
                return False
            self._close()
        if discovered_token.expired or discovered_token.force_expire:
            self.logger.warning(f"Authentication Attempt with expired AuthToken for {user}@{access_key_id}")
            return False
        expiration_date_str:str = discovered_token.expiration_date.strftime("%Y/%m/%d@%H:%M:%S %z")
        self.logger.info(f"Successfully Authenticated {user}@{access_key_id}, Expires: {expiration_date_str}")
        return True

    def init_authorize(self,access_key_id:str,expire_time:datetime.timedelta) -> str:
        """Authorization Start / Login Stage 1
        @param str \c access_key_id Access Key ID
        @param datetime.timedelta expire_time Expiration Time
        @retval str Auth Token Encrypted and Base64 Encoded
        @raises AuthDBNotLoaded AuthDB is not Loaded
        @raises InvalidAccessKey Access key does not exist or is invalid format
        @raises InvalidPubKey Public Key format in AuthDB is invalid or failed to load
        Response is the Auth Token which has been Encrypted with the Public Key stored
         in the AuthDB for the Access Key provided. The Auth Token must then be Decoded
         and Decrypted by the Client using the associated Private Key
        """
        self.logger.debug(f"Attempting Authentication with ID: {access_key_id}")
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
            userobj:AuthDBUser = self._authdb["users"][user]
            discovered_pubkey:str = ""
            for pair in userobj.keys:
                if pair["access_key_id"] == access_key_id:
                    discovered_pubkey = pair["pubkey"]
                    break
            if len(discovered_pubkey) == 0:
                raise InvalidAccessKeyError("Access Key was in DB, but could not locate a matching PubKey")
            self.logger.debug("Valid Access Key discovered")
            pubkey_obj:PublicKey
            try:
                pubkey_obj = load_der_public_key(base64.b64decode(discovered_pubkey),backend=default_backend()) # type: ignore
            except ValueError:
                self.logger.debug("Public Key was not a DER format, attempting PEM")
                try:
                    pubkey_obj = load_pem_public_key(base64.b64decode(discovered_pubkey),backend=default_backend()) # type: ignore
                except ValueError as e:
                    self.logger.debug("Public Key was not a PEM format either, bailing out")
                    self.logger.error(f"Unable to load Public Key, {e}")
                    self._close()
                    raise InvalidPubKeyError("Public Key format invalid, must be DER or PEM") from e
            self.logger.debug("PubKey loaded successfully, generating and sending AuthToken")
            token:bytes = uuid4().bytes
            auth_token:str = UUID(bytes=token).hex
            token_obj:AuthDBToken = AuthDBToken({
                "token": auth_token,
                "access_key_id": access_key_id,
                "creation": datetime.datetime.now().timestamp(),
                "expiration": (datetime.datetime.now() + expire_time).timestamp(),
                "force_expire": False
            })
            expiration_date_str:str = token_obj.expiration_date.strftime("%Y/%m/%d@%H:%M:%S %z")
            now_date_str:str = datetime.datetime.now().strftime("%Y/%m/%d@%H:%M:%S %z")
            self.logger.debug(f"Token Created, Expires: {expiration_date_str}; Currently: {now_date_str}")
            userobj.tokens.append(token_obj)
            try:
                resp:bytes = pubkey_obj.encrypt(token,
                    OAEP(
                        mgf=MGF1(algorithm=SHA512()),
                        algorithm=SHA512(),
                        label=None
                    )
                )
            except BaseException as e:
                self._close()
                raise InvalidPubKeyError(f"Failed to Encrypt Token, {e}") from e
            self._write()
        return base64.b64encode(resp).decode("utf-8")
# pylint: enable=duplicate-code
