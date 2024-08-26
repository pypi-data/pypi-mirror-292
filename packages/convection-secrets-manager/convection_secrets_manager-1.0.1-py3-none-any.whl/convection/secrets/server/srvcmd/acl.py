# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
import ssl

from convection.shared.functions import access_mode_to_access_str, access_str_to_access_mode
from convection.secrets.server.authdb import ConvectionSecretsAuthDB
from convection.secrets.server.srvcmd.core import ConvectionServerCommandCore
from convection.secrets.server.uacl import ACLObject

class ConvectionServerACLCommands(ConvectionServerCommandCore):
    """Convection Secrets Server Commands for ACL things"""

    # pylint: disable=duplicate-code
    # pylint: disable=unused-argument
    def audit_acl(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Show ACL
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                acl_data:dict[str,typing.Any] = self.manager.authdb_command("acl_audit",[request_data["acl_name"]])
                acl_data["mode"] = "allow" if acl_data["mode"] == ACLObject.MODE_ALLOW else "deny"
                acl_data["access_mode"] = access_mode_to_access_str(acl_data["access_mode"])
                self._send(conn,self._build_result(True,data={ request_data["acl_name"]: acl_data}))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))



    def list_acls(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; List of registered ACLs
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        try:
            acl_list:list[str] = self.manager.authdb_command("acl_list")
            self._send(conn,self._build_result(True,data={ "acls": acl_list }))
        except BaseException as e:
            self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
            self.logger.error(e,exc_info=True)
            # conn.read()


    def create_acl(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Create User/Group ACL
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                aclargs:dict[str,typing.Any] = {}
                if request_data["mode"] == "allow":
                    request_data["mode"] = ACLObject.MODE_ALLOW
                elif request_data["mode"] == "deny":
                    request_data["mode"] = ACLObject.MODE_DENY
                else:
                    raise ValueError("'mode' is invalid, must be `allow` or `deny`")
                request_data["access_mode"] = access_str_to_access_mode(request_data["access_mode"])
                for k,v in request_data.items():
                    if v is None:
                        continue
                    if k not in [ "acl_name", "acl_type" ]:
                        aclargs[k] = v
                result:bool = self.manager.authdb_command("acl_create",[request_data["acl_name"],request_data["acl_type"],aclargs])
                self._send(conn,self._build_result(result,data={"acl": request_data["acl_name"]}))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def attach_acl(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Attach ACL to User/Group
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            if request_data["attach_type"] == "group":
                request_data["attach_type"] = ConvectionSecretsAuthDB.ATTACH_ACL_GROUP
            elif request_data["attach_type"] == "user":
                request_data["attach_type"] = ConvectionSecretsAuthDB.ATTACH_ACL_USER
            else:
                raise ValueError("'attach_to_type' is invalid, must be `group` or `user`")
            try:
                result:bool = self.manager.authdb_command("attach_acl",[request_data["acl_name"],request_data["attach_type"],request_data["attach_name"]])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def detach_acl(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Remove ACL from User/Group
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            if request_data["detach_type"] == "group":
                request_data["detach_type"] = ConvectionSecretsAuthDB.ATTACH_ACL_GROUP
            elif request_data["detach_type"] == "user":
                request_data["detach_type"] = ConvectionSecretsAuthDB.ATTACH_ACL_USER
            else:
                raise ValueError("'detach_type' is invalid, must be `group` or `user`")
            try:
                result:bool = self.manager.authdb_command("detach_acl",[request_data["acl_name"],request_data["detach_type"],request_data["detach_name"]])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def remove_acl(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Remove ACL completely
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            try:
                result:bool = self.manager.authdb_command("acl_destroy",[request_data["acl_name"]])
                self._send(conn,self._build_result(result))
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))
    # pylint: enable=unused-argument
    # pylint: enable=duplicate-code
