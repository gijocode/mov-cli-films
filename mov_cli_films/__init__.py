from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .vidsrcme import *
from .vidsrcto import *
from .vadapav import *

plugin: PluginHookData = {
    "version": 1,

    "package_name": "mov-cli-films", # Required for the plugin update checker.
    "scrapers": {
        "DEFAULT": VidSrcMeScraper,
        "vidsrcme": VidSrcMeScraper,
        "vadapav": VadapavScraper
    }
}

__version__ = "1.3.4"

# NOTE: I will leave vidsrcto in, if no fix is found we'll remove it ~ Ananas

