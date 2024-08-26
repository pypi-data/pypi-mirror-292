# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import json
import logging
import re
import shutil
import ssl
import socket
import stat
import typing
from time import sleep
from pathlib import Path

import argstruct

from atckit.service import Service
from atckit.utilfuncs import UtilFuncs
from websockets.sync import server as ws
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK, ConnectionClosedError

from convection.shared.config import ConvectionConfigCore
from convection.shared.functions import access_str_to_access_mode
from convection.secrets.server.srvcmd.core import ConvectionServerCommandCore
from convection.secrets.server.manager import ConvectionSecretsManager
from convection.secrets.server.nacl import NetworkACL
from convection.secrets.server.uacl import ACLObject

class ConvectionServerCore(Service,ConvectionServerCommandCore):
    """Server Service Core

     - AF_UNIX socket is always created
     - AF_INET socket is only created if `service.use_network` is True

    Message format:
        `<command> <data>`

    Response:
     - Response should be a dictionary, containing at minimum:
        ```
        {
            "result": {
                "state": bool,
                "messages": list[str]
            }
        }
        ```
     - Additional data should be at the root of the response, and dependent on the COMMAND

    Redefine `_handle_connection(self,conn:ssl.SSLSocket,data:str,addr:typing.Union[tuple[str,int],str]) -> None`
    for connection handling
    """
    _SPECKER_SPEC_ROOT:str ## Should be defined in the extending class. See atckit.service.Service for Additional requirements
    _INET_IN_USE_FREE_TIME:int = 60

    config:ConvectionConfigCore
    _ssl_context:ssl.SSLContext
    _socket_path:Path
    _socket_path_str:str
    _inet_socket:ssl.SSLSocket
    _unix_socket:ssl.SSLSocket
    _websocket:ws.WebSocketServer
    _argstruct:argstruct.ArgStruct

    def __init__(self,call_args:dict[str,typing.Any]) -> None:
        """Initializer
        @param dict[str,Any] \c call_args Commandline Arguments
        """
        if call_args["config"] is not None:
            inbound_config_path:Path = Path(call_args["config"]).resolve()
            UtilFuncs.add_config_search_path(inbound_config_path)
        config_path:typing.Union[Path,None] = UtilFuncs.find_config_file(self._SERVICE_NAME,self._SERVICE_NAME)
        if config_path is None:
            raise FileNotFoundError(f"Unable to Locate Service config for {self._SERVICE_NAME}")
        super().__init__()
        self.logger.setLevel(call_args["loglevel"])
        self.config = ConvectionConfigCore(self._SPECKER_SPEC_ROOT,self._config)
        UtilFuncs.remove_config_search_path(config_path)
        self._socket_path = Path(self.config.get_configuration_value("service.socket_path")).resolve()
        self._socket_path_str = self._socket_path.as_posix()
        if self._socket_path.is_file():
            self.logger.warning(f"Socket {self._socket_path_str} existed, but the old process was not running; cleaning up")
            self._socket_path.unlink()
        tls_pass:typing.Union[str,None]
        try:
            tls_pass = self.config.get_configuration_value("service.tls_password")
            if tls_pass is not None and len(tls_pass) == 0:
                tls_pass = None
        except ValueError:
            tls_pass = None
        tls_cert:Path = Path(self.config.get_configuration_value("service.tls_cert")).resolve()
        tls_key:Path = Path(self.config.get_configuration_value("service.tls_key")).resolve()
        if not tls_cert.is_file() or not tls_key.is_file():
            raise FileNotFoundError("Unable to locate Cert or Key",tls_cert.as_posix(),tls_key.as_posix())
        self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self._ssl_context.load_cert_chain(tls_cert,tls_key,tls_pass)
        self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        self._ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        self.services += self._service_socket
        if bool(self.config.get_configuration_value("service.use_network")):
            self.logger.warning("***** Server has Networking enabled *****")
            self.services += self._service_inet
        if bool(self.config.get_configuration_value("service.use_websocket")):
            self.logger.warning("***** Server has WebSocket / WebUI enabled *****")
            self.services += self._service_websocket

    def _reload_config(self) -> None:
        """Configuration file reloader
        @retval None Nothing
        """
        self._config_file:typing.Union[Path,None] = UtilFuncs.find_config_file(self._SERVICE_NAME,self._SERVICE_NAME)
        if self._config_file is None:
            self.logger.critical("Failed to reload configuration. Unable to locate config")
            return
        self._config = UtilFuncs.load_sfile(self._config_file)
        self.config = ConvectionConfigCore(self._SPECKER_SPEC_ROOT,self._config)

    def _strip_cli_args(self,request_data:dict[str,typing.Any]) -> dict[str,typing.Any]:
        """Remove Console/CLI Args from request data
        @param dict[str,Any] \c request_data Inbound Request Data
        @retval dict[str,Any] Updated request_data with stripped console args
        """
        data:dict[str,typing.Any] = request_data.copy()
        for k in request_data.keys():
            if k in [ "config", "input_type", "specker_debug", "sensitive_debug", "loglevel", "verbose" ]:
                data.pop(k)
        return data

    manager:ConvectionSecretsManager
    nacl:NetworkACL
    _action_map:dict[str,typing.Callable]
    _command_map:dict[str,ConvectionConfigCore]
    _call_args:dict[str,typing.Any]
    _acl:list[dict[str,typing.Any]]

    def _handle_websocket(self,conn:ws.ServerConnection) -> None:
        self.logger.info(f"Connection from {conn.remote_address}")
        while True: ## Connection Level Loop; Read Data, Act, Respond, Repeat; Close on Error
            try:
                data:typing.Union[str,bytes] = conn.recv()
            except OSError:
                break
            except ConnectionClosedError as e:
                self.logger.error(f"WebSocket Close error: {e}")
                break
            except (ConnectionClosed, ConnectionClosedOK):
                break
            if not data:
                break
            if isinstance(data,str):
                data = data.encode("utf-8")
            self._handle_connection(conn=conn,addr=conn.remote_address,data=data)

    def _handle_connection(self,conn:typing.Union[ssl.SSLSocket,ws.ServerConnection],data:bytes,addr:typing.Union[tuple[str,int],str]) -> None:
        """Connection Handler
        @param ssl.SSLSocket \c conn Remote Connection Socket
        @param bytes \c data Data sent from Remote
        @param Union[tuple[str,int],str] \c addr Remote Address
        @retval None Nothing
        """
        result:bytes
        addr_str:str
        data_str:str = data.decode("utf-8")
        command:str = data_str.split(' ')[0]
        if command == "close" or len(command) == 0:
            return
        if command in self._action_map.keys():
            regex:re.Pattern = re.compile(r'^' + command + r' ?')
            cmd_data:typing.Union[dict[str,typing.Any],None] = None
            data_raw:str = regex.sub('',data_str)
            if len(data_raw) > 0 and re.search(r'^(\{|\[)',data_raw):
                cmd_data = json.loads(data_raw)
                cmd_data = self._strip_cli_args(cmd_data) # type: ignore
            if len(addr) >= 1:
                addr_str = addr[0]
                if not self.nacl.check(addr_str,command):
                    result = self._build_result(False,["Permission Denied",f"{addr_str} is not allowed to access {command}"])
                    self.logger.warning(f"Connection attempt from disallowed IP: {addr_str}, targeting command: {command}")
                    self._send(conn,result)
                    return
                self.logger.debug(f"Connection Accepted from {addr_str}, targeting command: {command}")
            else:
                addr_str = "socket"
            data_log:str = ""
            if self._call_args["sensitive_debug"]:
                data_log = f" with data: `{data_raw}`" if len(data_raw) > 0 else ""
            self.logger.debug(f"{addr_str} Sent Command: {command}{data_log}")
            action:typing.Callable = self._action_map[command]

            command_config:argstruct.ArgStructCommand = self._argstruct.commands[command]
            access_key_id:typing.Union[str,None] = None
            cmd_access_mode:str = command_config.get("access_mode")
            if command_config.get("auth_required"):
                authed:bool = self._auth_check(addr_str,command,conn,cmd_data)
                if not authed:
                    return
                access_key_id = cmd_data["access_key_id"] # type: ignore
            else:
                if not self.manager.locked and cmd_data is not None and "access_key_id" in cmd_data.keys():
                    access_key_id = cmd_data["access_key_id"] # type: ignore
                    cmd_data["auth_token"] = None
            if access_key_id is not None:
                proceed:bool = self._acl_check(cmd_access_mode,command,conn,cmd_data)
                if not proceed:
                    return
            try:
                action(conn=conn,remote_addr=addr,request_data=cmd_data,access_key_id=access_key_id)
            except BaseException as e:
                self.logger.error(f"Call of '{command}' failed")
                self.logger.error(e,exc_info=True)
                result = self._build_result(False,["Exception",str(e)])
                self._send(conn,result)
                return
        else:
            result = self._build_result(False,["Invalid Command",f"No Such command: '{command}'"])
            self._send(conn,result)

    def _acl_check(self,requested_access:str,command:str,conn:typing.Union[ssl.SSLSocket,ws.ServerConnection],cmd_data:typing.Union[dict[str,typing.Any],None] = None) -> bool:
        """ACL Check
        @param str \c requested_access CommandMap Command Access Mode to be used
        @param str \c command Command being executed
        @param ssl.SSLSocket \c conn Connection
        @param Union[dict[str,Any],None] Request/Command Data
        @retval bool Success/Failure
        """
        access_mode:int = access_str_to_access_mode(requested_access)
        access_key_id = cmd_data["access_key_id"] # type: ignore
        acl_check:int = self.manager.authdb_command("acl_check",[access_mode, access_key_id, command, cmd_data ])
        if command not in [ "authorize", "deauth" ]:
            cmd_data.pop("access_key_id") # type: ignore
            cmd_data.pop("auth_token") # type: ignore
        if acl_check is not ACLObject.MODE_ALLOW:
            result = self._build_result(False,message=["Auth Token valid, but ACL denies access to specified resource"],data={ "result": acl_check })
            self._send(conn,result)
            return False
        return True

    def _auth_check(self,addr_str:str,command:str,conn:typing.Union[ssl.SSLSocket,ws.ServerConnection], cmd_data:typing.Union[dict[str,typing.Any],None]) -> bool:
        """Authorization Check
        @param str \c addr_str Address String (host,port) or 'socket'
        @param str \c command Command being executed
        @param ssl.SSLSocket \c conn Connection
        @param Union[dict[str,Any],None] Request/Command Data
        @retval bool Success/Failure
        """
        result:bytes
        if cmd_data is None:
            result = self._build_result(False,["Authorization Required","Received No Data"])
            self.logger.warning(f"{addr_str} attempted command: {command}, which requires authorization, but no data was recieved from Client")
            self._send(conn,result)
            return False
        exception_message:str = ""
        try:
            authed:bool = self.manager.authorize(cmd_data["access_key_id"],cmd_data["auth_token"])
        except BaseException as e:
            exception_message = f"{type(e).__qualname__} - {e}"
            authed = False
        if not authed:
            if len(exception_message) == 0:
                exception_message = "(Already Deauthed)"
            result = self._build_result(False,["Authorization Required " + exception_message])
            self.logger.warning(f"{addr_str}, attempted command: {command}, but authorization was invalid {exception_message}")
            self._send(conn,result)
            return False
        return True

    def _wrap_socket(self,ssock:ssl.SSLSocket) -> None:
        """Server Actor, accept connections, handle command delegation
        @param ssl.SSLSocket \c ssock SSL Socket for Connection
        @retval None Nothing
        """
        conn:ssl.SSLSocket
        addr:typing.Any
        while self.should_run: ## Service Level Loop
            try:
                conn,addr = ssock.accept()
                conn.do_handshake(True)
            except OSError:
                continue
            self.logger.info(f"Connection from {addr}")
            while True: ## Connection Level Loop; Read Data, Act, Respond, Repeat; Close on Error
                try:
                    data:bytes = conn.recv()
                except OSError:
                    break
                if not data:
                    break
                self._handle_connection(conn=conn,addr=addr,data=data)

    def _stop_threads(self) -> bool:
        """Socket Shutdown calls
        @retval None Nothing
        """
        self.shutdown = True
        try:
            self._unix_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        except BaseException as e:
            self.logger.debug("UNIX Socket Shutdown during shutdown failed")
            self.logger.debug(e,exc_info=True)
            if self._service_socket in self._service_threads:
                self._service_threads.pop(self._service_socket)
        self._socket_path.unlink(True)
        if hasattr(self,"_inet_socket"):
            try:
                self._inet_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            except BaseException as e:
                self.logger.debug("INET Socket Shutdown during shutdown failed")
                self.logger.debug(e,exc_info=True)
                if self._service_inet in self._service_threads:
                    self._service_threads.pop(self._service_inet)
        if hasattr(self,"_websocket"):
            try:
                self._websocket.shutdown()
            except BaseException as e:
                self.logger.debug("WebSocket Shutdown during shutdown failed")
                self.logger.debug(e,exc_info=True)
                if self._service_websocket in self._service_threads:
                    self._service_threads.pop(self._service_websocket)
        return typing.cast(bool,super()._stop_threads())

    def _service_websocket(self) -> None:
        """WebSocket Socket Setup
        @retval None Nothing
        """
        listen_ip:str = self.config.get_configuration_value("service.websocket.listen_ip")
        listen_port:int = self.config.get_configuration_value("service.websocket.listen_port")
        logger = UtilFuncs.create_static_logger("WebSocket")
        logger.setLevel(logging.DEBUG)
        with ws.serve(self._handle_websocket,listen_ip,listen_port,ssl_context=self._ssl_context,logger=logger) as sock:
            self.logger.info(f"WebSocket Bound to {listen_ip}:{listen_port}")
            self._websocket = sock
            sock.serve_forever()

    def _service_inet(self) -> None:
        """AF_INET Socket Setup
        @retval None Nothing
        """
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            listen_ip:str = self.config.get_configuration_value("service.network.listen_ip")
            listen_port:str = self.config.get_configuration_value("service.network.listen_port")
            attempts:int = 0
            while attempts < self._INET_IN_USE_FREE_TIME:
                try:
                    sock.bind((listen_ip,listen_port))
                    break
                except OSError:
                    attempts += 1
                    sleep(1)
            if attempts >= self._INET_IN_USE_FREE_TIME:
                self.logger.critical(f"Failed to bind to {listen_ip}:{listen_port}")
                self._stop_threads()
                return
            self.logger.info(f"Server Bound to {listen_ip}:{listen_port}")
            sock.listen(10)
            with self._ssl_context.wrap_socket(sock, server_side=True) as self._inet_socket:
                self._wrap_socket(self._inet_socket)

    def _service_socket(self) -> None:
        """AF_UNIX Socket Setup
        @retval None Nothing
        """
        sock_mask:int = stat.S_IRGRP | stat.S_IWGRP | stat.S_IWUSR | stat.S_IRUSR | stat.S_IFSOCK
        service_user:str = self.config.get_configuration_value("service.socket_owner")
        service_group:str = self.config.get_configuration_value("service.socket_group")
        if not self._socket_path.parent.is_dir():
            self._socket_path.parent.mkdir(parents=True)
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
            try:
                sock.bind(self._socket_path_str)
                self.logger.info(f"Server Socket bound at {self._socket_path_str}")
                self._socket_path.chmod(sock_mask)
                try:
                    shutil.chown(self._socket_path,service_user,service_group)
                except PermissionError as e:
                    self.logger.warning(f"Failed to set user/group of socket to {service_user}:{service_group}. {e}")
                sock.listen(10)
            except BaseException as e:
                self.logger.critical(f"Binding to {self._socket_path_str} failed")
                self.logger.critical(e,exc_info=True)
                self._stop_threads()
                return
            with self._ssl_context.wrap_socket(sock, server_side=True) as self._unix_socket:
                self._wrap_socket(self._unix_socket)

    def stop(self) -> None:
        """Stop Service Thread(s)
        @retval None Nothing
        """
        try:
            self._stop_threads()
        except BaseException:
            self.logger.error("Shutdown may have failed. Check Logs")
        try:
            self._socket_path.unlink(True)
        except FileNotFoundError:
            self.logger.debug(f"{self._socket_path_str} was already removed")
        try:
            super().stop()
        except FileNotFoundError:
            self.logger.debug(f"{self._pid_file.as_posix()} was already removed")
