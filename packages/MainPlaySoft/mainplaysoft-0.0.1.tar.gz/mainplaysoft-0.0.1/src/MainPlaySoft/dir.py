import os
from .lang import Lang
from MainShortcuts2 import ms


class Dir:
  def __init__(self, core):
    self._author = core.author
    self._core = core
    self._data = None
    self._globaldata = None
    self._lang: Lang = core.lang
    self._localdata = None
    self._name = core.name
    self._rm_temp = True
    self._temp = None
    self.force_mkdir = True

  @property
  def author(self) -> str:
    return self._author

  @property
  def data(self) -> str:
    """Основная папка данных"""
    if self._data is None:
      if self._core.is_linux:
        self._data = os.path.expanduser("~/.config/%s/%s" % (self.author, self.name))
      if self._core.is_windows:
        self._data = os.path.expanduser("~/AppData/Roaming/%s/%s" % (self.author, self.name))
      self._data = os.path.abspath(self._data).replace("\\", "/")
      ms.dir.create(self._data, force=self.force_mkdir)
    return self._data

  @property
  def globaldata(self) -> str:
    """Глобальная папка данных (нужен `root`)"""
    if self._globaldata is None:
      if self._core.is_linux:
        if not "PREFIX" in os.environ:
          os.environ["PREFIX"] = "/"
        self._globaldata = "%setc/%s/%s" % (os.environ["PREFIX"], self.author, self.name)
      if self._core.is_windows:
        self._data = "C:/ProgramData/%s/%s" % (self.author, self.name)
      self._globaldata = os.path.abspath(self._globaldata).replace("\\", "/")
      ms.dir.create(self._globaldata, force=self.force_mkdir)
    return self._globaldata

  @property
  def localdata(self) -> str:
    """Локальная папка данных"""
    if self._localdata is None:
      if self._core.is_linux:
        self._localdata = os.path.expanduser("~/.local/etc/%s/%s" % (self.author, self.name))
      if self._core.is_windows:
        self._localdata = os.path.expanduser("~/AppData/Local/%s/%s" % (self.author, self.name))
      self._localdata = os.path.abspath(self._localdata).replace("\\", "/")
      ms.dir.create(self._localdata, force=self.force_mkdir)
    return self._localdata

  @property
  def name(self) -> str:
    return self._name

  @property
  def rm_temp(self) -> bool:
    """Нужно ли удалять временную папку при закрытии программы?"""
    return self._rm_temp

  @rm_temp.setter
  def rm_temp(self, v: bool):
    """Нужно ли удалять временную папку при закрытии программы?"""
    if type(v) != bool:
      raise TypeError("Need a type of %s, not %s" % (bool, type(v)))
    self._rm_temp = v

  @property
  def temp(self):
    """Папка для временных файлов"""
    if self._temp is None:
      import atexit
      if self._core.is_linux:
        if not "PREFIX" in os.environ:
          os.environ["PREFIX"] = "/"
        tempdir = "%stmp" % os.environ["PREFIX"]
      if self._core.is_windows:
        tempdir = os.path.expanduser("~/AppData/Local/Temp")
      dir = os.path.abspath(tempdir).replace("\\", "/")
      while True:
        name = "tmp" + ms.utils.randstr(16)
        if not ms.path.exists("%s/%s" % (dir, name)):
          break
      self._temp = "%s/%s" % (dir, name)
      ms.dir.create(self._temp)

      @atexit.register
      def rm_temp():
        if self.rm_temp:
          ms.dir.rm(self._temp)
    return self._temp
