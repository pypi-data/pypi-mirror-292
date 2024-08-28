"""Top-level package for pygeoapi plugin: Nldi Flowtools."""

__author__ = "Anders Hopkins"
__email__ = "ahopkins@usgs.gov"
__version__ = "0.3.1"

import logging

# Set up a package-wide logger
logger = logging.getLogger(__name__)

from nldi_flowtools.nldi_flowtools import splitcatchment, flowtrace  # noqa F401
