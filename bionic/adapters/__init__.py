"""Read-only adapters: each turns one domain's own records into signals."""

from collections.abc import Callable, Iterator
from pathlib import Path

from ..contract import Signal
from . import cine_toaster, kdp_studio, manual

ADAPTERS: dict[str, Callable[[Path], Iterator[Signal]]] = {
    kdp_studio.DOMAIN: kdp_studio.signals,
    cine_toaster.DOMAIN: cine_toaster.signals,
    manual.DOMAIN: manual.signals,
}

MANIFESTS = {kdp_studio.DOMAIN: kdp_studio.MANIFEST, cine_toaster.DOMAIN: cine_toaster.MANIFEST}
