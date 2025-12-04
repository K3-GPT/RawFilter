"""
图溜溜——RAW筛选器
"""

__version__ = "2.0.0"
__author__ = "@不说爱你到永久"
__description__ = "RAW格式图片筛选和管理工具"

from .constants import *
from .file_handler import FileHandler
from .gui import RawFilterGUI

__all__ = ['FileHandler', 'RawFilterGUI']