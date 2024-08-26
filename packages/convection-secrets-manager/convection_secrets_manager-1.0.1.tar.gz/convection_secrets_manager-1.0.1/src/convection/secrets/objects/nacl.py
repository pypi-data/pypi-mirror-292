# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import ipaddress
import re
import typing

class NACLObject:
    """Network ACL Data Object
    Check defaults to deny. Check is based on address in list and command in list
    Address List Check will also check if `0.0.0.0` is in the ACL
    Command List Check will also check if `*` is in the ACL
    """

    MODE_ALLOW:int = 1
    MODE_DENY:int = 0
    MODE_INVALID:int = -1

    _ADDR_ANY:ipaddress.IPv4Network

    _mode:int
    _commands:list[str]
    _addresses:list[ipaddress.IPv4Network]
    _raw_data:dict[str,typing.Union[list[str],str]]

    @property
    def mode(self) -> int:
        """ACL Mode
        See ACLObject.MODE_*
        @retval int ACL Type/Mode
        """
        return self._mode

    @property
    def addresses(self) -> list[ipaddress.IPv4Network]:
        """ACL Address List
        @retval list[ipaddress.IPv4Address] List of Addresses in ACL
        """
        return self._addresses

    @property
    def commands(self) -> list[str]:
        """ACL Command List
        @retval list[str] List of Commands in ACL
        """
        return self._commands

    def __init__(self,mode:str,addresses:list[str],commands:list[str]) -> None:
        """Initializer
        @param str \c mode ACL Mode; Anything other than "allow" becomes a deny
        @param list[str] \c addresses List of Addresses to use for ACL
        @param list[str] \c commands List of Commands to use for ACL
        """
        self._ADDR_ANY = ipaddress.IPv4Network("0.0.0.0/0")
        self._mode = NACLObject.MODE_DENY
        if mode == "allow":
            self._mode = NACLObject.MODE_ALLOW
        self._addresses = []
        for addr in addresses:
            if re.search(r'\/\d{1,2}$',addr):
                self._addresses.append(ipaddress.IPv4Network(addr))
            else:
                self._addresses.append(ipaddress.IPv4Network(f"{addr}/32"))
        self._commands = commands
        self._raw_data = { "type": mode, "ip_address": addresses, "commands": commands }

    def have_address(self,address:ipaddress.IPv4Address) -> bool:
        """Check if Address in ACL Address List
        @param ipaddress.IPv4Address \c address IP Address to check if in ACL
        @retval bool Whether Address in list
        """
        for addr_block in self._addresses:
            if address in addr_block:
                return True
        return False

    def have_command(self,command:str) -> bool:
        """Check if Command in ACL Command List
        @param str \c command Command to check if in ACL.
        @retval bool Whether Command in list
        """
        return (command in self._commands) or ("*" in self._commands)

    def check(self,address:ipaddress.IPv4Address,command:str) -> int:
        """Perform ACL Check against Address and Command
        @param ipaddress.IPv4Address \c address IP Address to Check
        @param str \c command Command to Check
        @retval int ACLObject.MODE_* result. Default deny
        """
        if self.have_address(address) and self.have_command(command):
            return self.mode
        return NACLObject.MODE_DENY

    def data(self) -> dict[str,typing.Union[list[str],str]]:
        """ACL Raw Data
        @retval dict[str,Union[list[str],str]] Original ACL Entry as dictionary
        """
        return self._raw_data
