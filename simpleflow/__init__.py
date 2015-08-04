# -*- coding: utf-8 -*-

__version__ = '0.6.1'
__author__ = 'Greg Leclercq'
__license__ = "MIT"

import logging.config

from .activity import Activity
from .workflow import Workflow

from . import settings


logging.config.dictConfig(settings.base.load()['LOGGING'])