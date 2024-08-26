# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import importlib
import os
import ssl
import threading
import typing
import argparse
import logging
from sys import exit as sys_exit
from time import sleep
from pathlib import Path

from cryptography.fernet import InvalidToken

import argstruct
from atckit.utilfuncs import UtilFuncs

from convection.shared.config import ConvectionConfigCore
from convection.shared.functions import access_str_to_access_mode, get_actions ,get_config_types,exit_invalid_cmd
from convection.shared.specker_static import StaticSpecker

from convection.secrets.objects.nacl import NACLObject
from convection.secrets.server.core import ConvectionServerCore
from convection.secrets.client.console import ConvectionSecretsConsole
from convection.secrets.server.manager import ConvectionSecretsManager
from convection.secrets.server.nacl import NetworkACL
from convection.secrets.server.uacl import ACLObject
from convection.secrets.server.authdb import ConvectionSecretsAuthDB
from convection.secrets.server.srvcmd.acl import ConvectionServerACLCommands
from convection.secrets.server.srvcmd.group import ConvectionServerGroupCommands
from convection.secrets.server.srvcmd.keys import ConvectionServerKeyCommands
from convection.secrets.server.srvcmd.secrets import ConvectionServerSecretsCommands
from convection.secrets.server.srvcmd.store import ConvectionServerStoreCommands
from convection.secrets.server.srvcmd.user import ConvectionServerUserCommands

class ConvectionSecretsServer(
    ConvectionServerCore,ConvectionServerUserCommands,ConvectionServerGroupCommands,
    ConvectionServerACLCommands,ConvectionServerKeyCommands,ConvectionServerStoreCommands,
    ConvectionServerSecretsCommands):
    """Secrets Manager / Controller
    Secrets manager and distributor service. Utilizes TLS + sockets for message passing

    Access Control:
     - Level 1: NACL (Network ACL). This controls which IP addresses are allowed to access which commands. This is a base level limitation
     - Level 2: Authorization. Key + Secret
     - Level 3: RBAC (Role Based Access Control). This controls which roles are allowed to access which secrets

    Communication:
     1. Connect to Server
     2. Send Authorization + COMMAND
     3. Access Checks
     4. COMMAND Execution
     5. RESPONSE
    """
    _SPECKER_SPEC_ROOT = "secrets-controller"
    _SERVICE_NAME = "convection-secrets"
    _SERVICE_CHECK_TIME = 0.1

    __MINIMAL_NACLS:list[dict[str,typing.Any]] = [
        { "type": "allow", "ip_address": ["127.0.0.1"] , "commands": [ "initialize", "status", "unlock", "rotate", "authorize", "deauth" ] },
        { "type": "deny", "ip_address": ["0.0.0.0/0"], "commands": [ "service-stop", "stop", "service-start", "start" ] }
    ]

    def __init__(self,call_args:dict[str,typing.Any]) -> None:
        """Initializer
        @param dict[str,Any] \c call_args Commandline Arguments
        """
        self._call_args = call_args
        StaticSpecker()
        StaticSpecker.instance.specker_instance.load_specs(Path(__file__).resolve().parent.parent.parent.joinpath("convection_core").joinpath("specs"))
        StaticSpecker.instance.specker_instance.load_specs(Path(__file__).resolve().parent.joinpath("specs"))
        try:
            super().__init__(call_args)
        except BaseException as e: ## For First Run, When no Config exists, so that we can run default_config
            self.logger.error(f"__init__ failed, {e}")
            self.config = ConvectionConfigCore(self._SPECKER_SPEC_ROOT,StaticSpecker.instance.specker_instance.defaults(self._SPECKER_SPEC_ROOT))
            return
        logging_fh:logging.FileHandler = logging.FileHandler(self.config.get_configuration_value("service.log_file"))
        logging_fh.formatter = logging.Formatter(fmt="%(asctime)s:%(levelname)s \t%(threadName)s\t%(module)s \t%(message)s")
        logging.getLogger().addHandler(logging_fh)
        self.services += self._authdb_cleanup
        # self.logger.setLevel(logging.INFO)
        if bool(self.config.get_configuration_value("service.use_network")):
            acl_raw:list[dict[str,typing.Any]] = self.config.get_configuration_value("service.network.acl")
            acl_raw += self.__MINIMAL_NACLS
            self.nacl = NetworkACL(acl_raw)

        shared_path:Path = Path(importlib.import_module("convection.shared").__path__[0]).resolve()
        m_path:Path = shared_path.joinpath("convection-sm-commands.toml")
        spec_path:Path = shared_path.joinpath("specs/")
        self._argstruct = argstruct.ArgStruct(m_path,"toml",[spec_path])
        self._action_map = get_actions(self)
        for cmd, command_config in self._argstruct.commands.items():
            # pylint: disable=no-member
            api_hide:bool = command_config.get("api_hidden") # type: ignore
            cli_hide:bool = command_config.get("cli_hidden") # type: ignore
            # pylint: enable=no-member
            if api_hide and cli_hide:
                self._action_map.pop(cmd)
        manager_config:ConvectionConfigCore = ConvectionConfigCore("service.config",self.config.get_configuration_value("config"))
        self.manager = ConvectionSecretsManager(manager_config)

    def _authdb_cleanup(self) -> None:
        """AuthDB Cleanup Daemon; Execute ConvectionSecretsManager.authdb_cleanup every 5 seconds
        """
        while not self.shutdown:
            if (not self.manager.locked) and self.manager.initialized:
                self.manager.authdb_command("cleanup")
                # self.manager.authdb_cleanup()
            sleep(5)

    def default_config(self) -> dict[str,typing.Any]:
        """MANAGEMENT ACTION; Generate Default Configuration
        @retval dict[str,Any] Default Configuration
        """
        return typing.cast(dict[str,typing.Any],self.config.specker_instance.defaults("secrets-controller"))

    # pylint: disable=unused-argument
    def service_stop(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Stop Secrets Manager Service
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        t:threading.Thread = threading.Thread(target=self.stop,name="shutdown-thread")
        self._send(conn,self._build_result(True,"Shutdown attempt in progress"))
        t.start()

    def command_list(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; List of All Commands available via API
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        output_commands:list[str] = []
        access_mode:int = access_str_to_access_mode("rwmd")
        for cmd,command_config in self._argstruct.commands.items():
            # pylint: disable=no-member
            hidden:bool = command_config.get("api_hidden") # type: ignore
            # pylint: enable=no-member
            nacl_check:bool
            if remote_addr is not None:
                if len(remote_addr) >= 1:
                    addr_str:str = remote_addr[0]
                    nacl_check = self.nacl.check(addr_str,cmd) == NACLObject.MODE_ALLOW
                else:
                    nacl_check = True
            else:
                nacl_check = True
            acl_check:bool = self.manager.authdb_command("acl_check",[access_mode, access_key_id, cmd, {} ]) == ACLObject.MODE_ALLOW
            if (acl_check and nacl_check) and not hidden:
                output_commands.append(cmd)
        data:dict[str,typing.Any] = {
            "commands": output_commands
        }
        self._send(conn,self._build_result(True,data=data))
        # conn.read()

    def initialize(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Initialize Secrets Manager
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            num_keys:int = int(request_data["num_keys"])
            try:
                keys_output:list[str] = self.manager.new_root_key(num_keys)
            except FileExistsError:
                self._send(conn,self._build_result(False,["Error: RootKey already exists"]))
                return
            except BaseException as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
                return

            self.logger.warning("===============================")
            self.logger.warning(" NEW RootKey HAS BEEN GENERATED")
            self.logger.warning("===============================")
            try:
                self.manager.unlock(keys_output[0])
            except (FileNotFoundError,InvalidToken) as e:
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
                return
            try:
                self.manager.new_keyset("authdb",True)
                self.manager.new_store("authdb","authdb","authdb",None)
                authdb:ConvectionSecretsAuthDB = typing.cast(ConvectionSecretsAuthDB,self.manager.load_store("authdb"))

                full_perms:int = ACLObject.ACCESS_READ | ACLObject.ACCESS_WRITE | ACLObject.ACCESS_MODIFY | ACLObject.ACCESS_DELETE
                authdb.acl_create("root_any_command", "ACLCommand", { "mode": ACLObject.MODE_ALLOW, "access_mode": full_perms, "commands": ["^.*$"] })
                authdb.acl_create("root_any_secret", "ACLStore", { "mode": ACLObject.MODE_ALLOW, "access_mode": full_perms, "store_paths": [r'^.*$'], "secret_names": [r'^.*$'] })

                root_access_key_id:str = authdb.create("root",request_data["root_public_key"])

                authdb.attach_acl("root_any_command", ConvectionSecretsAuthDB.ATTACH_ACL_USER, "root")
                authdb.attach_acl("root_any_secret", ConvectionSecretsAuthDB.ATTACH_ACL_USER, "root")
            except BaseException as e:
                self.manager.lock()
                self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
                self.logger.error(e,exc_info=True)
                return
            self.manager.lock()
            self._send(conn,self._build_result(True,["New RootKey Generated","New AuthDB Generated","New Root User Created",""],{"keys":keys_output, "root_access_key_id": root_access_key_id }))
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))

    def status(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Status Information
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        self._send(conn,self._build_result(True,data={"initialized": self.manager.initialized, "locked": self.manager.locked }))

    def lock(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Lock / Disregard encryption keys. Must be unlocked after calling
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        try:
            self.manager.lock()
            self._send(conn,self._build_result(True))
        except BaseException as e:
            self._send(conn,self._build_result(False,["Exception",type(e).__qualname__,str(e)]))
            self.logger.error(e,exc_info=True)
            # conn.read()

    def unlock(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
        """COMMAND; Unlock for General Access
        @param ssl.SSLSocket \c conn Active Connection / Communication Socket
        @param Union[tuple[str,int],None,str] \c remote_addr Remote Address (Empty/None for Socket Connections)
        @param Union[dict[str,Any],None] \c request_data Request Data, default None
        @param Union[str,None] \c access_key_id Access Key ID that made the request, default None
        @retval None Nothing
        """
        if request_data is not None:
            if not self.manager.locked:
                self._send(conn,self._build_result(False,["Error: KeyDB Already Unlocked"]))
            else:
                key_data:str = request_data["unlock_key"]
                try:
                    result_state:bool = self.manager.unlock(key_data)
                    result:bytes
                    if not result_state:
                        result = self._build_result(result_state,["Invalid Key or other problem, see server for details"])
                    else:
                        result = self._build_result(result_state)
                    self._send(conn,result)
                except BaseException as e:
                    self._send(conn,self._build_result(False,["Exception",str(e)]))
        else:
            self._send(conn,self._build_result(False,["Error: Empty Request Data"]))
        # conn.read()

    ##### Example Action #####
    # def myaction(self,conn:ssl.SSLSocket, remote_addr:typing.Union[tuple[str,int],None,str], request_data:typing.Union[dict[str,typing.Any],None] = None, access_key_id:typing.Union[str,None] = None) -> None:
    #   self._send(conn,bytes("accepted","utf-8"))
    #   extra_data = conn.read()
    #   result:bytes = self.__build_result(True,["Success",f"{addr} Called myaction with extra_data: '{extra_data}'"])
    #   self._send(conn,result)
    ##########################
    # pylint: enable=unused-argument

def console_secrets_run(input_args:dict[str,typing.Any]) -> None:
    """Secrets Command Processing
    @param dict[str,Any] \c input_args Commandline Input Args
    @retval None Nothing
    """
    if input_args["sub_command"] not in [ "initialize", "service-start", "start", "service-stop", "stop", "default_config" ]:
        print("This command can only be run from the Convection Secrets Remote Client, this is not the Remote Client")
        sys_exit(1)
    secrets_server:ConvectionSecretsServer
    if input_args["sub_command"] == "initialize":
        pubkey_path_raw:str = os.path.expanduser(input_args["public_key"])
        pubkey_path:Path = Path(pubkey_path_raw).resolve()
        pubkey_path_str:str = pubkey_path.as_posix()
        if not pubkey_path.is_file():
            print(f"Cannot locate {pubkey_path_str}")
            sys_exit(1)
        input_args.pop("public_key")
        with open(pubkey_path,"r",encoding="utf-8") as f:
            input_args["root_public_key"] = f.read()
    if input_args["sub_command"] in [ "service-start", "start" ]:
        try:
            secrets_server = ConvectionSecretsServer(input_args)
            secrets_server.run()
            secrets_server.stop()
        except PermissionError as e:
            logging.critical(f"Permission Error, {e}")
            sys_exit(9)
    elif input_args["sub_command"] == "default_config":
        secrets_server = ConvectionSecretsServer(input_args)
        default_config:dict[str,typing.Any] = secrets_server.default_config()
        output_type:str = input_args["output_type"]
        output_dir:Path = Path(input_args["config"]).resolve().joinpath("convection-secrets")
        output_file:Path = output_dir.joinpath(f"convection-secrets.{output_type}")
        output_file_str:str = output_file.as_posix()
        logging.info(f"Writing Convection Secrets Manager configuration to {output_file_str}")
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
        with open (output_file,"w",encoding="utf-8") as f:
            f.write(UtilFuncs.dump_sstr(default_config,output_type))
        sys_exit(0)
    else:
        input_args["config_prefix"] = "service"
        input_args["specker_root"] = "secrets-controller"
        secrets_client:ConvectionSecretsConsole = ConvectionSecretsConsole(input_args)
        command:str = input_args.pop("sub_command")
        valid:bool = secrets_client.command(command,input_args)
        if not valid:
            exit_invalid_cmd()
        sys_exit(0)

def secrets_manager_bin() -> None:
    """Convection Secrets Manager Main Execution
    """
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="Convection SM - Convection Secrets Manager")
    parser.add_argument("-v","--verbose",help="Turn on Debugging",action="store_true")
    parser.add_argument("-c","--config",help="Path to main config file")
    parser.add_argument("-t","--input-type",help="Force override of input type",choices=get_config_types(True),default="auto")
    parser.add_argument("--specker_debug",help="Turn on Debugging for Specker Specs",action="store_true")
    parser.add_argument("--sensitive_debug",help="Enable Sensitve Data Display/Logging for Debugging\n\t\t\tWARNING: DANGEROUS",action="store_true")
    shared_path:Path = Path(importlib.import_module("convection.shared").__path__[0]).resolve()
    m_path:Path = shared_path.joinpath("convection-sm-commands.toml")
    spec_path:Path = shared_path.joinpath("specs/")
    argstruct_obj:argstruct.ArgStruct = argstruct.ArgStruct(m_path,"toml",[spec_path])
    argstruct.console(argstruct_obj,parser,True,{ "dest": "sub_command", "required": True })
    input_args:typing.Union[dict[typing.Any,typing.Any],None] = argstruct.parse(argstruct_obj,parser,"sub_command")
    if input_args is None:
        parser.print_help()
        sys_exit(1)

    # pylint: disable=duplicate-code
    loglevel:int = logging.WARNING
    if input_args["verbose"]:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel,format="%(levelname)s \t%(threadName)s\t%(module)s \t%(message)s")
    input_args["loglevel"] = loglevel
    # pylint: enable=duplicate-code
    console_secrets_run(input_args)
