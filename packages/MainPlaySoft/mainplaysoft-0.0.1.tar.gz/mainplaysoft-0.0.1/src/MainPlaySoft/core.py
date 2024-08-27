import os
import sys
from .depends import Depends
from .dir import Dir
from .lang import Lang
from MainShortcuts2 import ms
from MainShortcuts2.core import MS2


class MPSoftError(Exception):
  pass


class MPSoft:
  LINUX = "linux"
  WINDOWS = "windows"

  def __init__(self, author: str, name: str, lang: str = "ru"):
    self.author = author
    self.is_linux = False
    self.is_termux = False
    self.is_windows = False
    self.lang = Lang(lang)
    self.MPSoftError = MPSoftError
    self.name = name
    self.platform = None
    self.depends = Depends(self)
    self.dir = Dir(self)
    if sys.platform == "linux":
      self.is_linux = True
      self.platform = self.LINUX
      if "TERMUX_VERSION" in os.environ:
        self.is_termux = True
    if sys.platform == "win32":
      self.is_windows = True
      self.platform = self.WINDOWS
    if self.platform is None:
      raise MPSoftError(lang["core/unknown_os"] % sys.platform)

  @property
  def ms(self) -> MS2:
    """MainShortcuts2"""
    return ms
