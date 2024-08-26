# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
import ssl

from atckit.utilfuncs import UtilFuncs

from convection.shared.exceptions import CriticalRotationError
from convection.secrets.server.srvcmd.core import ConvectionServerCommandCore

class ConvectionServerKeyCommands(ConvectionServerCommandCore):
    """Convection Secrets Server Commands for Key things"""

    # pylint: disable=duplicate-code
    # pylint: disable=unused-argument
    def rotate_root_keys(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Unlock Keys and Root Key Rotation
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                keys_output:list[str] = self.manager.rotate_unlock_keys(request_data["num_keys"])
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
                return
            self.logger.warning("===============================")
            self.logger.warning(" UNLOCK KEYS HAVE BEEN ROTATED")
            self.logger.warning("===============================")
            self._send(conn,self._build_result(True,["KeyDB Keys Rotated"],{ "keys":keys_output }))
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def create_keyset(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; List Secrets Stores
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.new_keyset(request_data["keyset_name"])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def list_keysets(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; List KeySet Names
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        try:
            self._send(conn,self._build_result(True,data={ "keysets": self.manager.list_keysets() }))
        except BaseException as e:
            self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
            self.logger.error(e,exc_info=True)
            # conn.read()

    def remove_keyset(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Remove KeySet
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.destroy_keyset(request_data["keyset_name"])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def rotate_keyset(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Rotate KeySet and the Stores associated
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            keyset_name:str = request_data["keyset_name"]
            try:
                result:bool = self.manager.rotate_keyset(keyset_name)
                keymsg:str = f"Keys for KeySet {keyset_name} Rotated"
                if not result:
                    keymsg = f"KeySet Rotation for {keyset_name} Failed"
                self._send(conn,self._build_result(result,[keymsg]))
            except CriticalRotationError as e:
                messages:list[str] = [
                    "KEYSET ROTATION FAILED."
                    "DURING REVERSION OF KEYSET, A SECRETS STORE FAILED ITS REVERSION.",
                    "YOUR SECRETS ARE IN DANGER. IT IS POSSIBLE THAT ONE OR MORE SECRETS STORES ARE NOW LOST. OTHERS MAY BE IN AN UNUSABLE STATE",
                    f"YOU WILL LIKELY NEED TO REVERT BACKUPS FOR ALL STORES ASSOCIATED WITH THE KEYSET '{keyset_name}'",
                    f"THE KEYS BEING ROTATED IN HAVE BEEN SAVED AS 'ROTATED_{keyset_name}' IN AN ATTEMPT TO MAKE RECOVERY OF OTHER STORES MORE PROBABLE",
                    "THE SERVER WILL NOW SHUTDOWN TO PREVENT FURTHER DAMAGE",
                    type(e).__qualname__,
                    str(e)
                ]
                self._send(conn,self._build_result(False,messages))
                self.logger.critical("KEYSET ROTATION FAILED, AND KEYSET REVERSION FAILED TOO. FORCING SHUT DOWN TO PREVENT FURTHER DAMAGE")
                conn.close()
                UtilFuncs.shutdown = True
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
                return
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))
    # pylint: enable=unused-argument
    # pylint: enable=duplicate-code
