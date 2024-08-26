# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Manager,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import logging
import ssl
import typing
import json

from websockets.sync import server as ws

from convection.secrets.server.manager import ConvectionSecretsManager

class ConvectionServerCommandCore:
    """Convection Secrets Server Support functions for Commands"""

    manager:ConvectionSecretsManager
    logger:logging.Logger

    def _build_result(self,result:bool,message:typing.Union[list[str],str,None] = None,data:typing.Union[None,dict[str,typing.Any]] = None) -> bytes:
        """Result output builder
        @param bool \c result Success/Failure flag
        @param Union[list[str],str,None] Message Output. Default None
        @param Union[dict[str,Any],None] Result Data. Default None
        @retval bytes Data + Result block as json in bytes
        """
        if data is None:
            data = {}
        message_list:list[str]
        if message is not None:
            if isinstance(message,list):
                message_list = message
            else:
                message_list = [message]
        else:
            message_list = []
        data["result"] = {
            "state": result,
            "messages": message_list
        }
        return bytes(json.dumps(data),"utf-8")

    def _send(self,conn:typing.Union[ssl.SSLSocket,ws.ServerConnection],data:bytes) -> None:
        """ssl.SSLSocket.send wrapper to catch problematic connections
        @param ssl.SSLSocket \c conn Connected Client Socket
        @param bytes \c data Raw Data to attempt send
        @retval None Nothing
        Catches Broken Pipe Error and prevents explosions. probably a better way for
         this, but because of how many `conn.send` there are, this seemed to be the
         easiest way to handle this.
        """
        try:
            if isinstance(conn,ws.ServerConnection):
                conn.send(data.decode("utf-8"))
            else:
                conn.send(data)
        except BrokenPipeError:
            self.logger.error("Tried to send data to client, but client was closed")
