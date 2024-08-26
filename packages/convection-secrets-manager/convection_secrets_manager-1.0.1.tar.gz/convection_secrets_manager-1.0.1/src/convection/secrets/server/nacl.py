# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import ipaddress
import logging
import typing

from atckit.utilfuncs import UtilFuncs

from convection.secrets.objects.nacl import NACLObject

class NetworkACL:
    """Network ACL Overseer
    NACLs are built containing the following pieces:
     - Type (mode): Allow/Deny flag
     - IP Address: List of IP Addresses for ACL
     - Commands: List of Commands for ACL

    ACLs default to deny (ACLObject.MODE_DENY). At creation, if the mode value is not `allow`, the mode will be MODE_DENY.
    Individual ACLs must each pass Address + Command Check.
    ACL Entry in configuration delegates the order in which they are checked; ACL Checks are AND'd together. Any matchign ACL with
      a deny will result in a deny result.
    IP Address list can contain `0.0.0.0` which will allow or deny all IPs
    Command list can contain `*` which will allow or deny all Commands
    """
    logger:logging.Logger
    _acl_list:list[NACLObject]
    _acl_command_map:dict[str,list[int]]
    _acl_ip_map:dict[ipaddress.IPv4Network,list[int]]

    @property
    def acls(self) -> list[NACLObject]:
        """NACL Object List, As ordered, from configuration
        @retval list[NACLObject] List of active NACLObjects
        """
        return self._acl_list

    def __init__(self,acl_config:list[dict[str,typing.Any]]) -> None:
        """Initializer
        @param list[dict[str,typing.Any]] \c acl_config Raw `service.network.acl` configuration
        """
        self.logger = UtilFuncs.create_object_logger(self)
        self.logger.setLevel(logging.getLogger().getEffectiveLevel())
        self._acl_list = []
        self._acl_command_map = {}
        self._acl_ip_map = {}
        acl_id:int = 0
        for acl_entry in acl_config:
            acl:NACLObject = NACLObject(mode=acl_entry["type"],addresses=acl_entry["ip_address"],commands=acl_entry["commands"])
            self._acl_list.append(acl)
            for addr in acl.addresses:
                if addr not in self._acl_ip_map.keys():
                    self._acl_ip_map[addr] = []
                self._acl_ip_map[addr].append(acl_id)
            for cmd in acl.commands:
                if cmd not in self._acl_command_map.keys():
                    self._acl_command_map[cmd] = []
                self._acl_command_map[cmd].append(acl_id)
            acl_id += 1

    def locate(self,address:str,command:str) -> list[int]:
        """ACL Locator. Find all ACLs matching address and command
        @param str \c address IP Address to locate ACL for
        @param str \c command Command to locate ACL for
        @retval list[int] List of ACLs that match Command and IP Address
        """
        addr:ipaddress.IPv4Address = ipaddress.IPv4Address(address)
        ip_acls:list[int] = []
        cmd_acls:list[int] = []
        for addr_block, acl_ids in self._acl_ip_map.items():
            if addr in addr_block:
                ip_acls += acl_ids
        for acl_cmd, acl_ids in self._acl_command_map.items():
            if acl_cmd in [ command, "*" ]:
                cmd_acls += acl_ids
        if len(ip_acls) == 0 and len(cmd_acls) == 0:
            return []
        result:list[int] = list(set(cmd_acls) & set(ip_acls))
        matched_ids:str = ', '.join([ str(id) for id in result])
        self.logger.debug(f"Searched NACLs for {address} calling {command}; Found {str(len(result))} NACLs; IDs: {matched_ids}")
        return result

    def check(self,address:str,command:str) -> int:
        """Get Allow/Deny state based on address and command
        @param str \c address IP Address to check
        @param str \c command Command to check
        @retval int NACLObject.MODE_* result
        Check all matching ACLs, AND'ing the result together
        """
        state:int = NACLObject.MODE_INVALID
        matching_acls:list[int] = self.locate(address,command)
        if len(matching_acls) == 0:
            state = NACLObject.MODE_DENY
            return state
        for acl_id in matching_acls:
            acl:NACLObject = self._acl_list[acl_id]
            state &= acl.mode
        state_str:str = "ALLOW" if state else "DENY"
        self.logger.debug(f"NACL Check for {address} calling {command}; Result: {state_str}")
        return state

    def audit(self,address:str,command:str) -> dict[str,typing.Any]:
        """ACL Audit / Info
        Show result, and matching ACLs for IP and Command
        @param str \c address IP Address to Audit
        @param str \c command Command to Audit
        @retval dict[str,typing.Any] Dictionary containing the requested check, result, and matching ACLs
        """
        matching_acls:list[int] = self.locate(address,command)
        check_result:int = -1
        if len(matching_acls) == 0:
            check_result = NACLObject.MODE_DENY
        else:
            check_result = self.check(address,command)
        result:dict[str,typing.Any] = {
            "check": {
                "address": address,
                "command": command
            },
            "result": "allow" if check_result == NACLObject.MODE_ALLOW else "deny",
            "matching_acls": []
        }
        for acl_id in matching_acls:
            acl:NACLObject = self._acl_list[acl_id]
            result["matching_acls"].append(acl.data())
        return result
