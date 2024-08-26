# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import datetime
import typing
from uuid import UUID

class AuthDBToken:
    """AuthDB Token Object; Container for Individual Token"""
    _expiration:datetime.datetime
    _creation:datetime.datetime
    _token:bytes
    _access_key_id:bytes

    force_expire:bool

    @property
    def expired(self) -> bool:
        """Expiration Check
        @retval bool Whether Token should be expired
        """
        now:datetime.datetime = datetime.datetime.now()
        return now >= self._expiration

    @property
    def access_key_id(self) -> bytes:
        """Access Key ID, as bytes
        @retval bytes Access Key ID, in bytes, for UUID(bytes=..)
        """
        return self._access_key_id

    @property
    def token(self) -> bytes:
        """Auth Token, as bytes
        @retval bytes Auth Token, in bytes, for UUID(bytes=..)
        """
        return self._token

    @property
    def created_date(self) -> datetime.datetime:
        """Token Creation Date
        @retval datetime.datetime Creation Timestamp
        """
        return self._creation

    @property
    def expiration_date(self) -> datetime.datetime:
        """Token Expiration Date
        @retval datetime.datetime Expiration Timestamp
        """
        return self._expiration

    def __init__(self,token_data:dict[str,typing.Any]) -> None:
        """Initializer
        @param dict[str,Any] \c token_data Token Data

        Token Data format:
        {
            "force_expire": <bool>,
            "token": <uuid.hex>,
            "access_key_id": <uuid.hex>,
            "creation": <posix_timestamp>,
            "expiration": <posix_timestamp>
        }
        """
        self.force_expire = token_data["force_expire"]
        self._token = UUID(hex=token_data["token"]).bytes
        self._access_key_id = UUID(hex=token_data["access_key_id"]).bytes
        self._creation = datetime.datetime.fromtimestamp(token_data["creation"])
        self._expiration = datetime.datetime.fromtimestamp(token_data["expiration"])

    def data(self) -> dict[str,typing.Any]:
        """Output Token Object to dictionary for writing
        @retval dict[str,Any] Token Object as Dictionary
        """
        return {
            "token": UUID(bytes=self._token).hex,
            "access_key_id": UUID(bytes=self._access_key_id).hex,
            "creation": self._creation.timestamp(),
            "expiration": self._expiration.timestamp(),
            "force_expire": self.force_expire
        }
