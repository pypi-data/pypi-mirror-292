##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.16.1+ob(v1)                                                   #
# Generated on 2024-08-26T23:03:56.861141                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

class MetaflowGSPackageError(metaflow.exception.MetaflowException, metaclass=type):
    ...

