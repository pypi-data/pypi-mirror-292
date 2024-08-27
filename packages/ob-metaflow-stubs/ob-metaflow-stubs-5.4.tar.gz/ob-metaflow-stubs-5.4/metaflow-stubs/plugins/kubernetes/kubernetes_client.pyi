##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.16.1+ob(v1)                                                   #
# Generated on 2024-08-26T23:03:56.777373                                        #
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

CLIENT_REFRESH_INTERVAL_SECONDS: int

class KubernetesClientException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class KubernetesClient(object, metaclass=type):
    def __init__(self):
        ...
    def get(self):
        ...
    def job(self, **kwargs):
        ...
    def jobset(self, **kwargs):
        ...
    ...

