# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
import ssl

from convection.secrets.server.srvcmd.core import ConvectionServerCommandCore

class ConvectionServerSecretsCommands(ConvectionServerCommandCore):
    """Convection Secrets Server Commands for Secrets things"""

    # pylint: disable=duplicate-code
    # pylint: disable=unused-argument
    def create_secret(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Create New Secret
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.new_secret(request_data["store_name"],request_data["store_args"])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def update_secret(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Update Existing Secret
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.update_secret(request_data["store_name"],request_data["store_args"])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def list_secrets(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; List Secrets in Store
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                store_name:str = request_data["store_name"]
                result:list[str] = self.manager.list_secrets(store_name,request_data["store_args"])
                self._send(conn,self._build_result(True,message=[f"{str(len(result))} Secrets in {store_name}"],data={"secrets": result, "store": request_data["store_name"]}))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def get_secret(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Get Secret from Store
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                store_name:str = request_data["store_name"]
                result:typing.Any = self.manager.get_secret(store_name,request_data["store_args"])
                self._send(conn,self._build_result(True,data={"secret": result }))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def destroy_secret(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Destroy Secret
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.remove_secret(request_data["store_name"],request_data["store_args"])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))
    # pylint: enable=unused-argument
    # pylint: enable=duplicate-code
