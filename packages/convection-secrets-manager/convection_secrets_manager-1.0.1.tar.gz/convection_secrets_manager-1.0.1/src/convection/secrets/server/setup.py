# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import grp
import json
import os
import pwd
import re
import argparse
import logging
import subprocess
import sys
from time import sleep
import typing
from pathlib import Path
from sys import exit as sys_exit

from tabulate import tabulate

from atckit.utilfuncs import UtilFuncs

from convection.shared.config import ConvectionConfiguration
from convection.shared.functions import get_config_types,print_console_initialization_data
from convection.secrets.client import ConvectionSecretsClient

sm_config_initialized:bool = False
sm_client_global:typing.Union[ConvectionSecretsClient,None] = None

def secrets_client(config_file:Path) -> ConvectionSecretsClient:
    """Initialize Convection Secrets Client object
    Will not initialize if already exists.
    @param Path \c config_file Path to Client config file
    @retval ConvectionSecretsClient Convection Secrets Client Instance
    """
    # pylint: disable=global-statement
    global sm_config_initialized
    global sm_client_global
    # pylint: enable=global-statement
    if not sm_config_initialized:
        client_args:dict[str,typing.Any] = {
            "config": config_file,
            "input_type": "toml",
            "verbose": False
        }
        sm_config_initialized = True
        ConvectionConfiguration(client_args)
    if sm_client_global is None:
        sm_client_global = ConvectionSecretsClient()
    return sm_client_global

def initialize(answers:dict[str,typing.Any]) -> dict[str,typing.Any]:
    """Perform Initialization Command
    @param dict[str,Any] \c answers Setup Answers data
    @retval dict[str,Any] Initialization Data from initialize command
    """
    with open(Path(answers["root_public_key"]).expanduser().resolve(),"r", encoding="utf-8") as f:
        pubkey_data:str = f.read()
    init_data:dict[str,typing.Any] = {
        "num_keys": answers["num_unlock_keys"],
        "root_public_key": pubkey_data
    }
    sm_client:ConvectionSecretsClient = secrets_client(Path(answers["client_config_file"]))
    sm_client.connect()
    status:dict[str,bool] = sm_client.status()
    if status["initialized"]:
        logging.error("Already Initialized")
        raise FileExistsError("Cannot Initialize, Already Initialized")
    resp:typing.Union[dict[str,typing.Any],None] = sm_client.command("initialize",init_data)
    if resp is None:
        logging.critical("Initialize Returned Empty Response")
        raise SystemError("Initialize Returned No Data")
    if not resp["result"]["state"]:
        logging.error("Initialization Failed")
        for m in resp["result"]["messages"]:
            logging.error(m)
        raise SystemError("Initialization Failed")
    resp.pop("result")
    logging.info("Initialization Completed")
    return resp

def unlock(answers:dict[str,typing.Any]) -> bool:
    """Server Unlock Command
    @param dict[str,Any] \c answers Setup Answers data
    @retval bool Lock Success/Failure
    """
    sm_client:ConvectionSecretsClient = secrets_client(Path(answers["client_config_file"]))
    sm_client.connect()
    resp:typing.Union[dict[str,typing.Any],None] = sm_client.command("unlock",{"unlock_key": answers["unlock_key"]})
    if resp is None:
        logging.critical("Unlock Returned Empty Response")
        raise SystemError("Unlock Returned No Data")
    if not resp["result"]["state"]:
        logging.error("Unlock Failed")
        for m in resp["result"]["messages"]:
            logging.error(m)
        raise SystemError("Unlock Failed")
    logging.info("Unlock Completed")
    return True

def authorize(answers:dict[str,typing.Any]) -> bool:
    """Client Authorization Step
    @param dict[str,Any] \c answers Setup Answers data
    @retval bool Auth Success/Failure
    Note that Auth is only valid for 5m here
    """
    sm_client:ConvectionSecretsClient = secrets_client(Path(answers["client_config_file"]))
    sm_client.connect()
    authed:bool = sm_client.authorize(answers["root_access_key_id"],Path(answers["root_private_key"]),answers["root_key_password"],"5m")
    if not authed:
        logging.error("Authorization Failed, See other log messages")
        return False
    logging.info("Authentication Completed")
    return True

def deauth(answers:dict[str,typing.Any]) -> bool:
    """Client Deauth / Logout Step
    @param dict[str,Any] \c answers Setup Answers data
    @retval bool Logout Success/Failure
    """
    sm_client:ConvectionSecretsClient = secrets_client(Path(answers["client_config_file"]))
    sm_client.connect()
    result:bool = sm_client.deauth()
    return result

def lock(answers:dict[str,typing.Any]) -> None:
    """Re-Lock Server
    @param dict[str,Any] \c answers Setup Answers data
    @retval bool Logout Success/Failure
    """
    sm_client:ConvectionSecretsClient = secrets_client(Path(answers["client_config_file"]))
    sm_client.connect()
    resp:typing.Union[dict[str,typing.Any],None] = sm_client.command("lock")
    if resp is None:
        logging.critical("Lock Returned Empty Response")
        raise SystemError("Lock Returned No Data")
    if not resp["result"]["state"]:
        logging.error("Lock Failed")
        for m in resp["result"]["messages"]:
            logging.error(m)
        raise SystemError("Lock Failed")
    logging.info("Lock Completed")

def create_recovery_user(answers:dict[str,typing.Any]) -> dict[str,typing.Any]:
    """Create User named 'recovery', Group named 'recovery', Attach root_* acls to Group, Attach Group to User
    @param dict[str,Any] \c answers Setup Answers data
    @retval dict[str,Any] Recovery User Access Key ID and Path to Private Key
    """
    logging.info("Creating Recovery User named 'recovery', and Group 'recovery'")
    sm_client:ConvectionSecretsClient = secrets_client(Path(answers["client_config_file"]))
    sm_client.connect()
    with open(Path(answers["recovery_public_key"]).expanduser().resolve(),"r", encoding="utf-8") as f:
        pubkey_data:str = f.read()
    recovery_access_key_id:str = sm_client.create_user("recovery",pubkey_data)
    sm_client.create_group("recovery")
    sm_client.attach_acl("root_any_command","group","recovery")
    sm_client.attach_acl("root_any_secret","group","recovery")
    sm_client.attach_group("recovery","recovery")
    return {
        "recovery_access_key_id": recovery_access_key_id,
        "private_key": answers["recovery_private_key"]
    }

def _generate_key(priv_path:Path,pub_path:Path,keysize:int) -> None:
    """RSA Keypair Generation by directly calling `openssl` binary
    @param Path \c priv_path Path of Private Key to create
    @param Path \c pub_path Path of Public Key to create
    @param int \c keysize RSA Key Size
    @retval None Nothing
    """
    pub_path_str:str = pub_path.as_posix()
    priv_path_str:str = priv_path.as_posix()

    if pub_path.is_file() and priv_path.is_file():
        logging.warning(f"Root Key Generation was requested, but the key at {pub_path_str} already exists, refusing to create")
        return
    logging.info("Generating RSA Key Pair")
    logging.info(f"Public: {pub_path_str}")
    logging.info(f"Private: {priv_path_str}")
    subprocess.run(["openssl","genrsa","-out",priv_path_str,str(keysize)],check=True)
    subprocess.run(["openssl","rsa","-in",priv_path_str,"-pubout","-out",pub_path_str],check=True)
    priv_path.chmod(0o600)
    pub_path.chmod(0o640)

def generate_tls(answers:dict[str,typing.Any]) -> None:
    """Generate Self-signed TLS Cert and Key, ensure Cert/Key/CA exists if not generated
    @param dict[str,Any] \c answers Setup Answers data
    @retval None Nothing
    """
    tls_cert:Path = Path(answers["tls_cert"]).expanduser().resolve()
    tls_key:Path = Path(answers["tls_key"]).expanduser().resolve()
    tls_key_str:str = tls_key.as_posix()
    tls_cert_str:str = tls_cert.as_posix()
    tls_ca:Path = Path(answers["tls_ca"]).expanduser().resolve()
    tls_ca_str:str = tls_ca.as_posix()
    uid:int = pwd.getpwnam(answers["server_user_name"]).pw_uid
    gid:int = grp.getgrnam(answers["server_group_name"]).gr_gid
    if answers["generate_tls"]:
        logging.info("Generating TLS Self-signed Certificate and Key")
        key_size:str = str(answers["generated_key_size"])
        tls_subject:str = "/C=US/ST=CA/L=Los Angeles/O=AccidentallyTheCable/OU=Convection Secrets Manager/CN=convection_sm.local"
        subprocess.run(["openssl","req","-x509","-outform","PEM","-out",tls_cert_str,"-newkey",f"rsa:{key_size}","-keyout",tls_key_str,"-subj",tls_subject,"-days","365","-batch","-nodes"],check=True)
        tls_key.chmod(0o600)
        tls_cert.chmod(0o640)
        os.chown(tls_key,uid,gid)
        os.chown(tls_cert,uid,gid)
    else:
        logging.info("Using Existing TLS Certificates")
        if not tls_key.is_file() or not tls_cert.is_file():
            logging.error(f"TLS Cert Generation was not specified, and either {tls_key_str} or {tls_cert_str} does not exist. Further setup steps will probably fail")
            return
        if tls_ca.is_file():
            logging.info(f"TLS CA was configured, and exists at {tls_ca_str}")
    if not tls_ca.is_file():
        logging.warning("===============================================================")
        logging.warning(" NO TLS CA WAS CONFIGURED. THIS IS SUBOPTIMAL")
        logging.warning(" You should configure service.tls_ca and global.secrets.client.tls_ca")
        logging.warning("===============================================================")

def generate_keys(answers:dict[str,typing.Any]) -> None:
    """Generate Keys for Root and Recovery User (if specified)
    @param dict[str,Any] \c answers Setup Answers data
    @retval None Nothing
    """
    root_pub:Path = Path(answers["root_public_key"]).resolve()
    root_priv:Path = Path(answers["root_private_key"]).resolve()
    root_pub_str:str = root_pub.as_posix()
    root_priv_str:str = root_priv.as_posix()
    recovery_pub:Path = Path(answers["recovery_public_key"]).resolve()
    recovery_priv:Path = Path(answers["recovery_private_key"]).resolve()
    recovery_pub_str:str = recovery_pub.as_posix()
    recovery_priv_str:str = recovery_priv.as_posix()
    if answers["generate_root_key"]:
        _generate_key(root_priv,root_pub,answers["generated_key_size"])
    else:
        if not root_pub.is_file() or not root_priv.is_file():
            logging.error(f"Root Key Generation was not Specified, and the key at {root_pub_str} or {root_priv_str} does not exist, further setup steps will probably fail")
    if answers["generate_recovery_key"] and answers["use_recovery"]:
        _generate_key(recovery_priv,recovery_pub,answers["generated_key_size"])
    elif answers["use_recovery"] and not answers["generate_recovery_key"]:
        if not recovery_pub.is_file() or not recovery_priv.is_file():
            logging.error(f"Recovery Key Generation was not Specified, and the key at {recovery_pub_str} or {recovery_priv_str} does not exist, further setup steps will probably fail")
    else:
        logging.warning("Not generating or creating a Recovery User, this can be done on your own later if you wish")

def start_server(answers:dict[str,typing.Any]) -> bool:
    """Start Convection Secrets Manager Server
    @param dict[str,Any] \c answers Setup Answers data
    @retval bool Success/Failure
    Utilizes systemctl if Service was installed, otherwise starts it directly.
    """
    command_str:str = ""
    if answers["install_service"]:
        command:list[str] = ["/usr/bin/systemctl","start","convection-secrets"]
        command_str = ' '.join(command)
        logging.info(f"Starting Convection Secrets Manager: {command_str}")
        proc:subprocess.CompletedProcess = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        if proc.returncode != 0:
            logging.error("Service Start Failed")
            logging.error("Errors:")
            logging.error(proc.stderr)
            logging.info("Output:")
            logging.info(proc.stdout)
            raise SystemError("Service Start Failed, See Logs")
        logging.info(f"Systemctl Result: {str(proc.returncode)}")
        stderr:list[str] = proc.stderr.decode("utf-8").split("\n")
        stdout:list[str] = proc.stdout.decode("utf-8").split("\n")
        for s in stderr:
            logging.error(s)
        for s in stdout:
            logging.debug(s)
        logging.info("Waiting for Server to be fully up")
    else:
        exec_path:str = Path(sys.executable).parent.joinpath("convection-secrets-manager").as_posix()
        command_str = ' '.join([exec_path,"-c",answers["server_config_root"]])
        logging.warning(f"Service was not installed, you will need to manually start the service by calling: {command_str}")
        logging.info("Waiting for service to be started")
    sm_client:ConvectionSecretsClient = secrets_client(Path(answers["client_config_file"]))
    wait_timeout:int = 60 # (wait_timeout * 5s = 300s (5m))
    check_count:int = 0
    while check_count < wait_timeout:
        try:
            sm_client.connect()
            status:dict[str,bool] = sm_client.status()
            initialized:str = "Yes" if status["initialized"] else "No"
            unlocked:str = "Yes" if status["initialized"] else "No"
            logging.info(f"Service Started. Initialized: {initialized}, Unlocked: {unlocked}")
            return True
        except ConnectionError as e:
            logging.debug(f"Connection Error; {e}")
            check_count += 1
            sleep(5)
        except BaseException as e:
            logging.error(f"Client exception: {type(e).__qualname__} - {e}")
    if check_count >= wait_timeout:
        target:str
        if answers["use_network"]:
            listen_ip:str = answers["listen_ip"]
            listen_port:str = answers["listen_port"]
            target = f"{listen_ip}:{listen_port}"
        else:
            target = Path(answers["socket_path"]).as_posix()
        logging.error(f"Timed out attempting to connect to {target} after {wait_timeout} attempts")
        return False
    return True

def install_service(answers:dict[str,typing.Any],default_root:str) -> None:
    """Install .service file
    @param dict[str,Any] \c answers Setup Answers data
    @param str \c default_root Default value for server_config_root
    @retval None Nothing
    """
    if answers["install_service"]:
        service_file:Path = Path(__file__).parent.joinpath("convection-secrets.service")
        target:Path = Path("/etc/systemd/system/convection-secrets.service")
        with open(service_file,"r",encoding="utf-8") as f:
            raw_file:str = f.read()
        exec_path:str = Path(sys.executable).parent.as_posix()
        server_config_root:str = answers["server_config_root"]
        replacements:dict[str,str] = {
            "%CONFIG%": " " if server_config_root == default_root else f" -c {server_config_root} ",
            "%USER%": answers["server_user_name"],
            "%GROUP%": answers["server_group_name"],
            "%PIDPATH%": answers["pid_dir"],
            "%EXECPATH%": exec_path
        }
        for s,r in replacements.items():
            regex:re.Pattern = re.compile(s)
            raw_file = regex.sub(r,raw_file)
        with open(target,"w",encoding="utf-8") as f:
            f.write(raw_file)
        subprocess.call(["/usr/bin/systemctl","daemon-reload"])
        subprocess.call(["/usr/bin/systemctl","enable","convection-secrets"])

def write_client_config(answers:dict[str,typing.Any]) -> None:
    """Create Client Configuration File
    @param dict[str,Any] \c answers Setup Answers data
    @retval None Nothing
    """
    client_config:dict[str,typing.Any] = {
        "global": {
            "secrets": {
                "client": {
                    "use_network": False,
                    "socket_path": answers["socket_path"],
                    "network": {
                        "target_ip": answers["listen_ip"],
                        "target_port": int(answers["listen_port"])
                    },
                    "log_file": answers["client_log_file"]
                }
            }
        }
    }
    client_config_file:Path = Path(answers["client_config_file"]).expanduser().resolve()
    client_config_file_str:str = client_config_file.as_posix()
    if answers["use_network"]:
        logging.warning("Client Configuration has Networking Disabled, even though it was requested to be enabled.")
        logging.warning("This ensures that the local client can access Convection Secrets Manager while no NACLs are configured")
        logging.warning(f"To enable Networking for the Client, set `global.secrets.client.use_network` to True in {client_config_file_str}")
        logging.warning("\tonce you have configured NACLs")
    if answers["tls_ca"] != "":
        client_config["global"]["secrets"]["client"]["tls_ca"] = Path(answers["tls_ca"]).as_posix()
    logging.info(f"Creating Client Config File {client_config_file_str}")
    with open(client_config_file,"w",encoding="utf-8") as f:
        f.write(UtilFuncs.dump_sstr(client_config,"toml"))
    client_config_file.chmod(0o644)

def write_server_config(answers:dict[str,typing.Any]) -> None:
    """Create Server Configuration File
    @param dict[str,Any] \c answers Setup Answers data
    @retval None Nothing
    """
    server_config:dict[str,typing.Any] = {
        "pid_dir": Path(answers["pid_dir"]).as_posix(),
        "service": {
            "log_file": answers["server_log_file"],
            "socket_owner": answers["server_user_name"],
            "socket_group": answers["server_group_name"],
            "socket_path": Path(answers["socket_path"]).as_posix(),
            "use_network": answers["use_network"],
            "use_websocket": answers["use_websocket"],
            "tls_cert": Path(answers["tls_cert"]).as_posix(),
            "tls_key": Path(answers["tls_key"]).as_posix(),
            "network": {
                "acl": [],
                "listen_ip": answers["listen_ip"],
                "listen_port": int(answers["listen_port"])
            },
            "websocket": {
                "listen_ip": answers["listen_ip"],
                "listen_port": int(answers["websocket_port"])
            }
        },
        "config": {
            "path": Path(answers["secrets_dir"]).as_posix(),
            "manager": {
                "keydb_key_count": answers["keydb_key_count"],
                "authentication": {
                    "token_max_expire": answers["token_max_expire"]
                }
            }
        }
    }
    if answers["tls_ca"] != "":
        server_config["service"]["tls_ca"] = Path(answers["tls_ca"]).as_posix()
    server_dir:Path = Path(answers["server_config_root"]).expanduser().resolve()
    server_dir = server_dir.joinpath("convection-secrets/")
    server_config_file:Path = server_dir.joinpath("convection-secrets.toml")
    server_config_file_str:str = server_config_file.as_posix()
    logging.info(f"Creating Server Config File {server_config_file_str}")
    with open(server_config_file,"w",encoding="utf-8") as f:
        f.write(UtilFuncs.dump_sstr(server_config,"toml"))
    server_config_file.chmod(0o644)

def create_dirs(answers:dict[str,typing.Any]) -> None:
    """Create Directories required for operation
    @param dict[str,Any] \c answers Setup Answers data
    @retval None Nothing
    """
    logging.info("Creating Directories")
    uid:int = pwd.getpwnam(answers["server_user_name"]).pw_uid
    gid:int = grp.getgrnam(answers["server_group_name"]).gr_gid
    server_dir:Path = Path(answers["server_config_root"]).expanduser().resolve()
    server_dir = server_dir.joinpath("convection-secrets/")
    server_dir_str:str = server_dir.as_posix()
    client_dir:Path = Path(answers["client_config_file"]).expanduser().resolve().parent
    client_dir_str:str = client_dir.as_posix()
    logging.info(f"Creating {client_dir_str}")
    client_dir.mkdir(parents=True,exist_ok=True)
    logging.info(f"Creating {server_dir_str}")
    server_dir.mkdir(parents=True,exist_ok=True)
    server_dir.chmod(0o750)
    os.chown(server_dir,0,gid)
    secrets_dir:Path = Path(answers["secrets_dir"]).expanduser().resolve()
    secrets_dir_str:str = secrets_dir.as_posix()
    logging.info(f"Creating {secrets_dir_str}")
    secrets_dir.mkdir(parents=True,exist_ok=True)
    secrets_dir.chmod(0o700)
    os.chown(secrets_dir,uid,gid)
    pid_dir:Path = Path(answers["pid_dir"]).expanduser().resolve()
    pid_dir_str:str = pid_dir.as_posix()
    logging.info(f"Creating {pid_dir_str}")
    pid_dir.mkdir(parents=True,exist_ok=True)
    pid_dir.chmod(0o755)
    if Path("/var/run").resolve() not in pid_dir.parents:
        os.chown(pid_dir,uid,gid)
    socket_dir:Path = Path(answers["socket_path"]).parent.resolve()
    socket_dir_str:str = socket_dir.as_posix()
    logging.info(f"Creating {socket_dir_str}")
    socket_dir.mkdir(parents=True,exist_ok=True)
    socket_dir.chmod(0o775)
    for c in [ answers["tls_cert"], answers["tls_key"], answers["tls_ca"] ]:
        if c == "":
            continue
        cert_dir:Path = Path(c).expanduser().resolve().parent
        if not cert_dir.is_dir():
            cert_dir.mkdir(parents=True)
            cert_dir.chmod(0o750)
            os.chown(cert_dir,uid,gid)

def create_server_user(answers:dict[str,typing.Any]) -> None:
    """Create OS User/Group for operation
    @param dict[str,Any] \c answers Setup Answers data
    @retval None Nothing
    """
    if answers["create_server_user"]:
        user_name:str = answers["server_user_name"]
        group_name:str = answers["server_group_name"]
        logging.info(f"Will Create User:Group '{user_name}:{group_name}'")
        user_exist:bool = False
        group_exist:bool = False
        try:
            pwd.getpwnam(user_name)
            user_exist = True
        except KeyError:
            user_exist = False
        group_users:list[str] = []
        try:
            group:grp.struct_group = grp.getgrnam(group_name)
            group_users = group.gr_mem
            group_exist = True
        except KeyError:
            group_exist = False
        if not group_exist:
            logging.info(f"Creating Group {group_name}")
            subprocess.run(["/sbin/groupadd","-r",group_name],check=True)
        if not user_exist:
            logging.info(f"Creating User {user_name}")
            subprocess.run(["/sbin/useradd","-M","-N","-r","-s","/sbin/nologin/","-g",group_name,user_name],check=True)
            group_users.append(user_name)
        else:
            logging.info(f"User '{user_name}' already exists")
        if user_name not in group_users:
            logging.info(f"User was not in Group '{group_name}'")
            subprocess.run(["/sbin/usermod","-aG",group_name,user_name],check=True)

def print_console_recovery_data(data:dict[str,typing.Any]) -> None:
    """Print Recovery User data to Console
    @param dict[str,Any] \c data Recovery User data (Access Key ID, Private Key Path)
    @retval None Nothing
    """
    cols:list[str] = [ "Purpose", "Data" ]
    rows:list[list[str]] = [cols]
    rows.append(["Access Key ID",data["recovery_access_key_id"]])
    rows.append(["Private Key",data["private_key"]])
    print(tabulate([["THIS IS YOUR RECOVERY USER ACCESS KEY ID AND PRIVATE KEY"],["STORE THESE AWAY SOMEWHERE SAFE"]],tablefmt="outline"))
    print(tabulate(rows,headers="firstrow",tablefmt="outline"))

def prompt_questions(questions:dict[str,str],defaults:dict[str,typing.Any],answers:dict[str,typing.Any]) -> None:
    """Ask and Setup Questions that dont already have Answers
    @param dict[str,Any] \c questions Setup Questions
    @param dict[str,Any] \c defaults Default Answers
    @param dict[str,Any] \c answers Already Answered Questions / Resulting Answer Data
    @retval None Nothing
    """
    question_count:int = len(questions)
    filled_answers:int = len(answers)
    remaining_questions:int = question_count - filled_answers
    logging.info(f"{str(filled_answers)} Question(s) already prefilled by answer file")
    logging.info(f"{str(remaining_questions)} / {str(question_count)} Questions need to be answered")
    for qname,qstr in questions.items():
        if qname not in answers.keys():
            answer:typing.Any = input(f"{qstr}[{defaults[qname]}]: ")
            answers[qname] = answer

def process_answers(defaults:dict[str,typing.Any], answers:dict[str,typing.Any]) -> None:
    """Process Answers, ensure Default is set if the Answer was empty
    @param dict[str,Any] \c defaults Default Answers
    @param dict[str,Any] \c answers Answered Questions / Fixed Answer Data
    @retval None Nothing
    """
    answers_out:dict[str,typing.Any] = {}
    answer:typing.Any
    for qname,answer in answers.items():
        if answer == "":
            answers[qname] = defaults[qname]
            answer = defaults[qname]
        if answer == "":
            continue
        if defaults[qname] in [ "Yes", "No" ]:
            if not isinstance(answer,bool):
                if re.match(r'[Yy](es)?',answer) is not None:
                    answers[qname] = True
                elif re.match(r'[Nn]o?',answer) is not None:
                    answers[qname] = False
                else:
                    print(f"Error: {qname} requires '[Yy]es' / '[Nn]o' Answer, got something else; {answer}")
                    sys_exit(1)
        elif isinstance(defaults[qname],str) and defaults[qname].startswith in [ "/", "~" ]:
            answers[qname] = Path(answer).expanduser().resolve()
        elif isinstance(answers[qname],Path):
            answers_out[qname] = Path(answers[qname]).as_posix()
        else:
            answers_out[qname] = answers[qname]
    logging.info("Answer Data:")
    logging.info(json.dumps(answers_out))
    del answers_out

def secrets_manager_setup() -> None:
    """Secrets Manager Setup Process. Install Service, Configure Server, Client, etc."""
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="Convection SM - Convection Secrets Manager SETUP")
    parser.add_argument("-v","--verbose",help="Turn on Debugging",action="store_true")
    parser.add_argument("-d","--data",help="Pre-filled configuration to skip questions during setup")
    parser.add_argument("-t","--input-type",help="Force override of input type for --data",choices=get_config_types(True),default="auto")

    args:argparse.Namespace = parser.parse_args()

    loglevel:int = logging.INFO
    input_args:dict[typing.Any,typing.Any] = vars(args)
    if input_args["verbose"]:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel,format="%(levelname)s\t%(module)s\t%(message)s")
    input_args["loglevel"] = loglevel
    answers:dict[str,typing.Any] = {}
    if input_args["data"] is not None:
        answer_file:Path = Path(input_args["data"]).expanduser().resolve()
        answers = UtilFuncs.load_sfile(answer_file,input_args["input_type"])
    defaults:dict[str,typing.Any] = {
        "server_user_name": "convection_sm",
        "server_group_name": "convection_sm",
        "create_server_user": "Yes",
        "server_config_root": "/etc/",
        "server_log_file": "/var/log/convection-secrets.log",
        "client_config_file": "~/.local/convection-secrets.client.toml",
        "client_log_file": "~/convection-secrets-client.log",
        "secrets_dir": "/var/secrets/",
        "pid_dir": "/var/run/",
        "generated_key_size": 4096,
        "socket_path": "/var/run/convection.secrets.sock",
        "generate_tls": "No",
        "tls_cert": "/etc/convection-secrets/certs/cert.pem",
        "tls_key": "/etc/convection-secrets/certs/key.pem",
        "tls_ca": "",
        "use_network": "No",
        "use_websocket": "No",
        "listen_ip": "127.0.0.1",
        "listen_port": 9670,
        "websocket_port": 9671,
        "keydb_key_count": 5,
        "token_max_expire": "1h",
        "install_service": "Yes",
        "initialize": "Yes",
        "num_unlock_keys": 5,
        "generate_root_key": "Yes",
        "root_private_key": "~/convection_sm.root.key",
        "root_public_key": "~/convection_sm.root.pub",
        "use_recovery": "Yes",
        "generate_recovery_key": "Yes",
        "recovery_private_key": "~/convection_sm.recovery.key",
        "recovery_public_key": "~/convection_sm.recovery.pub",
    }
    token_time_format:str = '\n\t'.join([ r'Format: ^(\d+Y)?(\d+M)?(\d+w)?(\d+d)?(\d+h)?(\d+m)?(\d+s)?(\d+ms)?$', "Examples: '4w10h', '1M', '10Y'" ])
    questions:dict[str,str] = {
        "server_user_name": "User that will be running Convection Secrets Manager?",
        "server_group_name": "Group that will be running Convection Secrets Manager?",
        "create_server_user": "Create Server User/Group (from Above)?",
        "server_config_root": "Server Configuration Directory",
        "server_log_file": "Server Log File Path",
        "client_config_file": "Client Configuration File Path",
        "client_log_file": "Client Log File Path",
        "secrets_dir": "Secrets Directory Root",
        "pid_dir": "PID Dir",
        "generated_key_size": "Key Size for any Generated RSA/TLS Keys",
        "socket_path": "Socket Path",
        "generate_tls": "Generate TLS Certificate?",
        "tls_cert": "TLS Certificate Path",
        "tls_key": "TLS Certificate Key Path",
        "tls_ca": "TLS CA Certificate Path",
        "use_network": "Enable Networking?",
        "use_websocket": "Enable WebSocket (for WebUI)?",
        "listen_ip": "IP Address to Listen on",
        "listen_port": "TCP Port to Listen on",
        "websocket_port": "WebSocket Port to Listen on",
        "keydb_key_count": "Number of Keys to create for each KeySet?",
        "token_max_expire": f"Maximum Expire Time of any AuthToken\n{token_time_format}\n",
        "install_service": "Install as Service?",
        "initialize": "Initialize the Server?",
        "num_unlock_keys": "Number of Unlock Keys?",
        "generate_root_key": "Generate Root Key Pair?",
        "root_private_key": "Root Private Key Path",
        "root_public_key": "Root Public Key Path",
        "use_recovery": "Create Recovery User?",
        "generate_recovery_key": "Generate Recovery Key Pair?",
        "recovery_private_key": "Recovery Private Key Path",
        "recovery_public_key": "Recovery Public Key Path"
    }
    prompt_questions(questions,defaults,answers)
    process_answers(defaults,answers)
    logging.info("-------- Start of Installation --------")
    create_server_user(answers)
    create_dirs(answers)
    generate_keys(answers)
    generate_tls(answers)
    write_server_config(answers)
    write_client_config(answers)
    install_service(answers,defaults["server_config_root"])
    started:bool = start_server(answers)
    if not started:
        logging.error("Service was not started, cannot continue with setup")
        sys_exit(3)
    logging.info("Service Started")
    initialization_data:dict[str,typing.Any] = initialize(answers)
    answers["root_access_key_id"] = initialization_data["root_access_key_id"]
    answers["root_key_password"] = None
    answers["unlock_key"] = initialization_data["keys"][0]
    unlock(answers)
    auth_success:bool = authorize(answers)
    if not auth_success:
        sys_exit(4)
    recovery_data:dict[str,typing.Any] = {}
    if answers["use_recovery"]:
        recovery_data = create_recovery_user(answers)
    lock(answers)
    logging.info("-------- Installation Finished --------")
    print_console_initialization_data(initialization_data)
    if answers["use_recovery"]:
        print_console_recovery_data(recovery_data)
