"""Read-only adapters: each turns one domain's own records into signals."""

from collections.abc import Callable, Iterator
from pathlib import Path

from ..contract import Signal
from . import kdp_studio

ADAPTERS: dict[str, Callable[[Path], Iterator[Signal]]] = {
    kdp_studio.DOMAIN: kdp_studio.signals,
}

MANIFESTS = {kdp_studio.DOMAIN: kdp_studio.MANIFEST}
