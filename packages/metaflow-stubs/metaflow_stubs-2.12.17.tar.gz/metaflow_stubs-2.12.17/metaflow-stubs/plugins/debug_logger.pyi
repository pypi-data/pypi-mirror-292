##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.17                                                            #
# Generated on 2024-08-27T00:52:58.109092                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.event_logger

class DebugEventLogger(metaflow.event_logger.NullEventLogger, metaclass=type):
    @classmethod
    def get_worker(cls):
        ...
    ...

class DebugEventLoggerSidecar(object, metaclass=type):
    def __init__(self):
        ...
    def process_message(self, msg):
        ...
    ...

