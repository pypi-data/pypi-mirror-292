# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
import threading
import logging
from pathlib import Path

from atckit.utilfuncs import UtilFuncs

from convection.shared.functions import load_plugins
from convection.shared.config import ConvectionConfigCore
from convection.shared.objects.plugins.secret import ConvectionPlugin_Secret
from convection.secrets.server.authdb import ConvectionSecretsAuthDB

from convection.secrets.server.mgrcmd.keys import ConvectionManagerKeyCommands
from convection.secrets.server.mgrcmd.secrets import ConvectionManagerSecretCommands
from convection.secrets.server.mgrcmd.store import ConvectionManagerStoreCommands
from convection.secrets.server.mgrcmd.auth import ConvectionManagerAuthCommands
from convection.secrets.server.mgrcmd.core import ConvectionManagerCommandCore

class ConvectionSecretsManager(
    ConvectionManagerKeyCommands,ConvectionManagerSecretCommands,
    ConvectionManagerStoreCommands,ConvectionManagerAuthCommands,
    ConvectionManagerCommandCore):
    """Secrets Manager Container. All functions exist in the defined subclasses
    """

    _authdb_action_map:dict[str,typing.Callable]

    def __init__(self,config:ConvectionConfigCore) -> None:
        """Initializer
        @param ConvectionConfigCore \c config Configuration Object
        """
        self._locked = True
        self._root_encryptor = None
        self._secrets_stores = None
        self._keymapdb = None
        self._authdb = None
        self._authdb_lock = threading.Lock()
        self._rotation_lock = threading.Lock()
        self._authdb_action_map = {}
        self.config = config
        self.logger = UtilFuncs.create_object_logger(self)
        self.logger.setLevel(logging.getLogger().getEffectiveLevel())
        self._keyset_key_count = int(self.config.get_configuration_value("manager.keydb_key_count"))
        self._storage_path = Path(self.config.get_configuration_value("path")).resolve()
        storage_path_str:str = self._storage_path.as_posix()
        if not self._storage_path.is_dir():
            self.logger.warning(f"{storage_path_str} does not exist, creating")
            self._storage_path.mkdir(parents=True)
        self.logger.debug(f"Secrets Store Path: {storage_path_str}")
        self._storage_path.chmod(0o0700)
        self._store_types = load_plugins("convection.plugins.secrets",ConvectionPlugin_Secret)
        if len(self._store_types) == 0:
            self.logger.warning("THERE ARE NO AVAILABLE SECRETS STORES. YOU WILL BE UNABLE TO CREATE NEW SECRETS OR MANAGE EXISTING ONES UNTIL AT LEAST ONE SECRET STORE PLUGIN IS AVAILABLE")
            self.logger.warning("See Plugin Documentation for more information")
        self._store_types["authdb"] = ConvectionSecretsAuthDB
