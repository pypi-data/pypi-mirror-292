# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import logging
import re
import typing

from atckit.utilfuncs import UtilFuncs
from convection.shared.functions import access_mode_to_access_str

class ACLObject:
    """General ACL Object
    Parameters: Name, Allow/Deny, Access Mode
    """
    _name:str
    _mode:int
    _access_mode:int

    MODE_ALLOW:int = 1
    MODE_DENY:int = 0
    MODE_INVALID:int = -1

    ACCESS_INVALID:int = 224
    ACCESS_NONE:int = 0
    ACCESS_READ:int = 2
    ACCESS_WRITE:int = 4
    ACCESS_MODIFY:int = 8
    ACCESS_DELETE:int = 16

    @property
    def name(self) -> str:
        """ACL Name
        @retval str ACL Name
        """
        return self._name

    @property
    def mode(self) -> int:
        """ACL Mode
        See ACLObject.MODE_*
        @retval int ACL Type/Mode
        """
        return self._mode

    @property
    def access_mode(self) -> int:
        """Access Mode
        See ACLObject.ACCESS_*
        @retval int Access Mode
        """
        return self._access_mode

    def __init__(self,name:str,mode:int,access_mode:int) -> None:
        """Initializer
        @param str \c name Name of ACL
        @param int \c mode ACL Mode (ACLObject.MODE_*)
        @param int \c access_mode Access Mode (ACLObject.ACCESS_*)
        """
        if mode not in [ 1, 0, -1 ]:
            raise ValueError(f"Invalid ACL Mode {str(mode)}")
        if mode >= 255:
            raise ValueError(f"Invlaid Access Mode {str(access_mode)}")
        self._mode = mode
        self._name = name
        self._access_mode = access_mode

    def check(self,**kwargs:typing.Any) -> int:
        """ACL Check/Verify
        @param dict[str,Any] \c **kwargs Args
        @retval int ACL Result (ACLObject.MODE_*)
        Function should be overridden for each ACLObject Type.

        Available Arguments:
         - command `str`: Requested Command (EX: create_store)
         - store_path `str`: Path of Secret Store being requested
         - secret_name `str`: Name of Secret being requested
         - access_mode `int`: Access Mode (Read/Write/Modify/Delete)
        """
        if not self.access_mode_check(kwargs["access_mode"]):
            return ACLObject.MODE_DENY
        return self.mode

    def access_mode_check(self,request_mode:int) -> bool:
        """Check if specified Request Mode is flagged
        @param int \c request_mode Inbound Access Mode
        @retval bool Access Mode is flagged
        """
        return (self._access_mode & request_mode) == request_mode

    # pylint: disable=unused-argument
    def have(self,**kwargs:typing.Any) -> bool:
        """Matching ACL evaluator; Check if ACL is a matching ACL
        @param dict[str,Any] \c **kwargs Args
        @retval bool ACL has matching value(s)
        Function should be overridden for each ACLObject Type.

        Available Arguments:
         - command `str`: Requested Command (EX: create_store)
         - store_path `str`: Path of Secret Store being requested
         - secret_name `str`: Name of Secret being requested
         - access_mode `int`: Access Mode (Read/Write/Modify/Delete)
        """
        return True # self.access_mode_check(kwargs["access_mode"])
    # pylint: enable=unused-argument

    def data(self) -> dict[str,typing.Any]:
        """Get ACL Data as dict
        @retval dict[str,Any] ACL Data
        """
        out:dict[str,typing.Any] = {}
        for k,v in self.__dict__.items():
            if re.match(r'_[a-z].*$',k):
                key:str = re.sub(r'_(\w+)$',r'\1',k)
                out[key] = v
        return out

class ACLCommand(ACLObject):
    """Command Specific ACL Object
    """

    __commands_re:list[re.Pattern]
    _commands:list[str]

    @property
    def commands(self) -> list[str]:
        """List of Defined Commands
        @retval list[str] List of Commands
        """
        return self._commands

    def __init__(self, name: str, mode:int, access_mode:int, commands:list[str]) -> None:
        """Initializer
        @param str \c name Name of ACL
        @param int \c mode ACL Mode (ACLObject.MODE_*)
        @param int \c access_mode Access Mode (ACLObject.ACCESS_*)
        @param list[str] \c commands List of Commands ACL applies to
        """
        self.__commands_re = [ re.compile(p) for p in commands ]
        self._commands = commands
        super().__init__(name,mode,access_mode)

    def check(self,**kwargs:typing.Any) -> int:
        if "command" not in kwargs.keys():
            return ACLObject.MODE_INVALID
        up_check:int = super().check(**kwargs)
        if up_check == ACLObject.MODE_DENY:
            return ACLObject.MODE_DENY
        if not self.have_command(kwargs['command']):
            return ACLObject.MODE_INVALID
        return self.mode

    def have(self,**kwargs:typing.Any) -> bool:
        if "command" not in kwargs.keys():
            return False
        return self.have_command(kwargs['command'])

    def have_command(self,command:str) -> bool:
        """Check if Command in ACL Command List
        @param str \c command Command to check if in ACL.
        @retval bool Whether Command in list
        """
        for c in self.__commands_re:
            if c.search(command) is not None:
                return True
        return False

class ACLStore(ACLObject):
    """Secret Storage Specific ACL Object
    """
    __store_paths_re:list[re.Pattern]
    _store_paths:list[str]
    __secret_names_re:list[re.Pattern]
    _secret_names:list[str]

    @property
    def store_paths(self) -> list[re.Pattern]:
        """Regex Pattern Secrets Store Paths
        @retval list[re.Pattern] Regex Patterns for Secrets Storage Paths that ACL applies to
        """
        return self.__store_paths_re

    @property
    def store_paths_raw(self) -> list[str]:
        """Secrets Store Paths (Raw)
        @retval list[str] Raw Patterns for Secrets Storage Paths that ACL applies to
        """
        return self._store_paths

    @property
    def secret_names(self) -> list[re.Pattern]:
        """Regex Pattern Secrets Names
        @retval list[re.Pattern] Regex Patterns for Secrets Storage Secrets that ACL applies to
        """
        return self.__secret_names_re

    @property
    def secret_names_raw(self) -> list[str]:
        """Secrets Names (Raw)
        @retval list[str] Raw Patterns for Secrets Storage Secrets that ACL applies to
        """
        return self._secret_names

    def __init__(self, name: str, mode: int, access_mode:int, store_paths:list[str], secret_names:list[str]) -> None:
        """Initializer
        @param str \c name Name of ACL
        @param int \c mode ACL Mode (ACLObject.MODE_*)
        @param int \c access_mode Access Mode (ACLObject.ACCESS_*)
        @param list[str] \c store_paths Patterns for re.compile of Secrets Storage Paths that ACL will apply to
        @param list[str] \c secret_names Patterns for re.compile of Secrets Names that ACL will apply to
        """
        self.__store_paths_re = [ re.compile(p) for p in store_paths ]
        self._store_paths = store_paths
        self.__secret_names_re = [ re.compile(n) for n in secret_names ]
        self._secret_names = secret_names
        super().__init__(name, mode,access_mode)

    def check(self, **kwargs:typing.Any) -> int:
        kwarg_keys = kwargs.keys()
        if "store_path" not in kwarg_keys and "secret_name" not in kwarg_keys:
            return ACLObject.MODE_INVALID
        up_check:int = super().check(**kwargs)
        if up_check == ACLObject.MODE_DENY:
            return ACLObject.MODE_DENY
        check_labels:list[str] = [ "store_name", "store_path", "secret_name" ]
        check_funcs:list[typing.Callable] = [ self.have_store, self.have_store, self.have_secret ]
        for i in range(0,len(check_labels)):
            label:str = check_labels[i]
            func:typing.Callable = check_funcs[i]
            if label in kwarg_keys:
                if kwargs[label] == "":
                    return ACLObject.MODE_INVALID
                if not func(kwargs[label]):
                    return ACLObject.MODE_INVALID
        return self.mode

    def have(self,**kwargs:typing.Any) -> bool:
        kwarg_keys = kwargs.keys()
        if "store_path" not in kwarg_keys and "secret_name" not in kwarg_keys:
            return False
        # I dont like this, but.... idk what do
        result_name:bool = True
        result_path:bool = True
        if "store_path" in kwarg_keys:
            if kwargs["store_path"] == "":
                result_path = False
            else:
                result_path = self.have_store(kwargs["store_path"])
        if "secret_name" in kwarg_keys:
            if kwargs["secret_name"] == "":
                result_name = False
            else:
                result_name = self.have_secret(kwargs["secret_name"])
        return result_name and result_path

    def have_store(self,store:str) -> bool:
        """Check if Specified Secrets Store is in this ACL
        @param str \c store Secrets Storage Path to check
        @retval bool Is / Is not in ACL
        """
        for p in self.__store_paths_re:
            if p.search(store) is not None:
                return True
        return False

    def have_secret(self,secret_name:str) -> bool:
        """Check if Specified Secrets Name is in this ACL
        @param str \c store Secrets Name to check
        @retval bool Is / Is not in ACL
        """
        for s in self.__secret_names_re:
            if s.search(secret_name) is not None:
                return True
        return False

class ACLContainer:
    """UACL / GACL Container / ACL Storage
    """
    logger:logging.Logger
    _acl_list:list[typing.Union[ACLObject,ACLCommand,ACLStore]]

    @property
    def acls(self) -> list[ACLObject]:
        """ACL Object List, As ordered, from configuration
        @retval list[ACLObject] List of active ACLObjects
        """
        return self._acl_list

    @property
    def acl_names(self) -> list[str]:
        """Associated ACL Name list
        @retval list[str] List of ACL Names attached
        """
        return [ a.name for a in self._acl_list ]

    def __init__(self,acls:typing.Union[list[typing.Union[ACLObject,ACLCommand,ACLStore]],None] = None) -> None:
        """Initializer
        @param list[Union[ACLObject,ACLCommand,ACLStore]] ACLs to Attach, default empty
        """
        self.logger = UtilFuncs.create_object_logger(self)
        self.logger.setLevel(logging.getLogger().getEffectiveLevel())
        if acls is not None:
            self._acl_list = acls.copy()
        else:
            self._acl_list = []

    def merge(self,other:"ACLContainer") -> None:
        """Combine another ACLContainer with this one
        @param ACLContainer \c other Other ACL Container to get ACLs from
        @retval None Nothing
        """
        for acl in other.acls:
            if acl.name not in self.acl_names:
                self._acl_list.append(acl)

    def add_acl(self,acl_obj:typing.Union[ACLObject,ACLCommand,ACLStore]) -> None:
        """Add ACL to Container
        @param Union[ACLObject,ACLCommand,ACLStore] \c acl_obj An ACL Object
        @retval None Nothing
        """
        if acl_obj.name not in self.acl_names:
            self._acl_list.append(acl_obj)

    def remove_acl(self,acl_name:str) -> bool:
        """Remove ACL from Container
        @param str acl_name Name of ACL to remove
        @retval bool Success/Failure
        """
        if acl_name not in self.acl_names:
            return False
        acl_obj:typing.Union[ACLObject,ACLCommand,ACLStore,None] = self.get_by_name(acl_name)
        if acl_obj is None:
            raise KeyError("BUG BUG BUG; Remove ACL, Get By Name, should never hit this")
        acl_idx:int = self._acl_list.index(acl_obj)
        self._acl_list.pop(acl_idx)
        return True

    def get_by_name(self,acl_name:str) -> typing.Union[ACLObject,ACLCommand,ACLStore,None]:
        """Get ACL by Name
        @param str \c name ACL Name
        @retval Union[ACLObject,ACLCommand,ACLStore,None] ACL Object if found, None if not found
        """
        if acl_name not in self.acl_names:
            return None
        for acl in self.acls:
            if acl_name == acl.name:
                return acl
        raise KeyError("BUG BUG BUG; Get By Name, should never hit this")

    def locate(self,access_mode:int, command:typing.Union[str,None] = None, store_path:typing.Union[str,None] = None, secret_name:typing.Union[str,None] = None) -> list[int]:
        """ACL Locator. Find all ACLs matching address and command
        @param int \c access_mode Access Mode (ACLObject.ACCESS_*)
        @param str \c command Command to locate ACL for
        @param str \c store_path Secrets Storage Paths to locate ACL for
        @param str \c secret_name Secrets Name to locate ACL for
        @retval list[int] List of ACLs that match parameters
        """
        action_data:dict[str,typing.Any] = { k: v for k,v in locals().items() if k != "self" and v is not None }
        result:list[int] = []
        for a_idx in range(0,len(self._acl_list)):
            acl:typing.Union[ACLObject,ACLCommand,ACLStore] = self._acl_list[a_idx]
            have:bool = acl.have(**action_data)
            self.logger.debug(f"Checked ACL ID {str(a_idx)} ({acl.name}), {action_data}; Result: {have}")
            if have:
                result.append(a_idx)
        matched_ids:str = ', '.join([ str(id) for id in result])
        access_mode_str:str = access_mode_to_access_str(access_mode)
        self.logger.debug(f"Searched User ACLs for Command '{command}' with Acesss Mode '{access_mode_str}' targeting '{store_path}/{secret_name}'; Found {str(len(result))} ACLs; IDs: {matched_ids}")
        return result

    def check(self,access_mode:int, command:typing.Union[str,None] = None, store_path:typing.Union[str,None] = None, secret_name:typing.Union[str,None] = None) -> int:
        """Get Allow/Deny state based on parameters
        @param int \c access_mode Access Mode (ACLObject.ACCESS_*)
        @param str \c command Command to check
        @param str \c store_path Secrets Storage Paths to check
        @param str \c secret_name Secrets Name to check
        @retval int ACLObject.MODE_* result
        Check all matching ACLs, AND'ing the result together
        """
        access_mode_str:str = access_mode_to_access_str(access_mode)
        dbg_msg:str = f"ACL Check for Command '{command}' with Acesss Mode '{access_mode_str}' targeting '{store_path}/{secret_name}'; Result: "
        action_data:dict[str,typing.Any] = { k: v for k,v in locals().items() if k != "self" and v is not None }
        matching_acls:list[int] = self.locate(access_mode,command,store_path,secret_name)
        if len(matching_acls) == 0:
            self.logger.debug(f"{dbg_msg} DENY")
            return ACLObject.MODE_DENY
        state:int = ACLObject.MODE_INVALID
        for acl_id in matching_acls:
            acl:typing.Union[ACLObject,ACLCommand,ACLStore] = self._acl_list[acl_id]
            result_state:int = acl.check(**action_data)
            state &= result_state
        state_str:str = "ALLOW" if state else "DENY"
        self.logger.debug(f"{dbg_msg} {state_str}")
        return state

    def data(self) -> list[dict[str,typing.Any]]:
        """Get ACLs as Dictionaries
        """
        result:list[dict[str,typing.Any]] = []
        for acl in self._acl_list:
            a:dict[str,typing.Any] = acl.data()
            obj_type:str = type(acl).__qualname__
            a["object"] = obj_type
            result.append(a)
        return result
