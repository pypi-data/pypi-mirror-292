#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# Copyright (c) 2024, LeXtudio Inc. <support@lextudio.com>
#
# License: https://www.pysnmp.com/pysnmp/license.html
#
import os
import random

try:
    from socket import AF_UNIX
except ImportError:
    AF_UNIX = None

from typing import Tuple
import warnings
from pysnmp.carrier.base import AbstractTransportAddress
from pysnmp.carrier.asyncio.dgram.base import DgramAsyncioProtocol

DOMAIN_NAME: Tuple[int, ...]
SNMP_UDP6_DOMAIN: Tuple[int, ...]
DOMAIN_NAME = SNMP_LOCAL_DOMAIN = (1, 3, 6, 1, 2, 1, 100, 1, 13)

random.seed()


class UnixTransportAddress(str, AbstractTransportAddress):
    pass


class UnixAsyncioTransport(DgramAsyncioProtocol):
    SOCK_FAMILY: "int|None" = AF_UNIX
    ADDRESS_TYPE = UnixTransportAddress
    _iface = ""

    def openClientMode(self, iface=None):
        if iface is None:
            # UNIX domain sockets must be explicitly bound
            iface = ""
            while len(iface) < 8:
                iface += chr(random.randrange(65, 91))
                iface += chr(random.randrange(97, 123))
            iface = os.path.sep + "tmp" + os.path.sep + "pysnmp" + iface
        if os.path.exists(iface):
            os.remove(iface)
        DgramAsyncioProtocol.openClientMode(self, iface)
        self._iface = iface
        return self

    def openServerMode(self, iface):
        DgramAsyncioProtocol.openServerMode(self, iface)
        self._iface = iface
        return self

    def closeTransport(self):
        DgramAsyncioProtocol.closeTransport(self)
        try:
            os.remove(self._iface)
        except OSError:
            pass


UnixTransport = UnixAsyncioTransport

# Old to new attribute mapping
deprecated_attributes = {
    "domainName": "DOMAIN_NAME",
    "snmpLocalDomain": "SNMP_LOCAL_DOMAIN",
}


def __getattr__(attr: str):
    if new_attr := deprecated_attributes.get(attr):
        warnings.warn(
            f"{attr} is deprecated. Please use {new_attr} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new_attr]
    raise AttributeError(f"module '{__name__}' has no attribute '{attr}'")
