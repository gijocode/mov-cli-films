from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .vidsrcme import *
from .vidsrcto import *

plugin: PluginHookData = {
    "version": 1, 
    "scrapers": {
        "DEFAULT": VidSrcMeScraper,
        "vidsrcme": VidSrcMeScraper
    }
}

__version__ = "1.3.3"

# NOTE: I will leave vidsrcto in, if no fix is found we'll remove it ~ Ananas