# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
import ssl

from convection.secrets.server.srvcmd.core import ConvectionServerCommandCore

class ConvectionServerGroupCommands(ConvectionServerCommandCore):
    """Convection Secrets Server Commands for Group things"""

    # pylint: disable=duplicate-code
    # pylint: disable=unused-argument
    def attach_group(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Attach Group to User
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.authdb_command("attach_group",[request_data["group_name"],request_data["user_name"]])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def detach_group(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Attach Group to User
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.authdb_command("detach_group",[request_data["group_name"],request_data["user_name"]])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def audit_group(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Group Info / Audit
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                group_data:dict[str,typing.Any] = self.manager.authdb_command("group_audit",[request_data["group_name"]])
                self._send(conn,self._build_result(True,data={ request_data["group_name"]: group_data }))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def create_group(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Create AuthDB Group
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.authdb_command("group_create",[request_data["group_name"]])
                self._send(conn,self._build_result(result,data={"group": request_data["group_name"]}))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def list_groups(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; List of registered Groups
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        try:
            group_list:list[str] = self.manager.authdb_command("group_list")
            self._send(conn,self._build_result(True,data={ "groups": group_list }))
        except BaseException as e:
            self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
            self.logger.error(e,exc_info=True)
            # conn.read()

    def remove_group(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Remove ACL from User/Group
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.authdb_command("group_destroy",[request_data["group_name"]])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))
    # pylint: enable=unused-argument
    # pylint: enable=duplicate-code
