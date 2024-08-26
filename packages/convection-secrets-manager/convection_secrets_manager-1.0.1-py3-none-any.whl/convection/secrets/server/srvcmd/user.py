# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
import ssl

from convection.secrets.server.srvcmd.core import ConvectionServerCommandCore

class ConvectionServerUserCommands(ConvectionServerCommandCore):
    """Convection Secrets Server Commands for User things"""

    # pylint: disable=duplicate-code
    # pylint: disable=unused-argument
    def audit_user(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; User Info / Audit
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                user_data:dict[str,typing.Any] = self.manager.authdb_command("get",[request_data["user_name"]])
                self._send(conn,self._build_result(True,data={ request_data["user_name"]: user_data }))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def create_user(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; User / Access Key ID Creation
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                new_access_key:str = self.manager.authdb_command("create",[request_data["user_name"],request_data["public_key"]])
                self._send(conn,self._build_result(True,data={"access_key_id": new_access_key, "user": request_data["user_name"]}))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def deauth(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Deauth / Logout
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                deauth:bool = self.manager.authdb_command("deauth",[request_data["access_key_id"],request_data["auth_token"]])
                self._send(conn,self._build_result(deauth,["Deauthenticated"]))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def authorize(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Authorize / Log in
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                expire_time:typing.Union[str,None] = None
                if "expire_time" in request_data.keys():
                    expire_time = request_data["expire_time"]
                auth_init:str = self.manager.init_authorize(request_data["access_key_id"],expire_time)
                self._send(conn,self._build_result(True,["Auth Initiated"],{ "response":auth_init }))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
                return
            try:
                auth_token:str = conn.read().decode("utf-8")
                auth_accepted:bool = self.manager.authdb_command("verify_authorize",[request_data["access_key_id"],auth_token])
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
                return
            if auth_accepted:
                self._send(conn,self._build_result(True,["Authorized"]))
            else:
                self._send(conn,self._build_result(False,["Authorization Failed"]))

        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def list_users(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; List of registered Users
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        try:
            user_list:list[str] = self.manager.authdb_command("list")
            self._send(conn,self._build_result(True,data={ "users": user_list }))
        except BaseException as e:
            self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
            self.logger.error(e,exc_info=True)
            # conn.read()

    def remove_access(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; User / Access Key ID Creation
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                remove_user:typing.Union[str,None] = None
                if "user_name" in request_data.keys():
                    remove_user = request_data["user_name"]
                remove_access_key:typing.Union[str,None] = None
                if "remove_access_key_id" in request_data.keys():
                    remove_access_key = request_data["remove_access_key_id"]
                remove_pubkey:typing.Union[str,None] = None
                if "remove_public_key" in request_data.keys():
                    remove_pubkey = request_data["remove_public_key"]
                removed:bool = self.manager.authdb_command("destroy",[remove_user,remove_access_key,remove_pubkey])
                self._send(conn,self._build_result(removed))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))
    # pylint: enable=unused-argument
    # pylint: enable=duplicate-code
