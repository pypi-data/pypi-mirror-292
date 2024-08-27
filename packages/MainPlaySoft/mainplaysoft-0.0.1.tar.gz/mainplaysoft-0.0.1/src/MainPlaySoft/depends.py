import sys
from .lang import Lang
try:
  import pkg_resources
except ImportError:
  from pip._vendor import pkg_resources


class Depends:
  """Проверка наличия модулей"""

  def __init__(self, core):
    self.depends: list[str]
    self.existing_modules: list[str]
    self.lang: Lang = core.lang
    self.missing_modules: list[str]

  def add(self, *names: str):
    """Добавить модуль в список зависимостей. Название модуля должно быть указано как в PIP"""
    for i in names:
      self.depends.append(i)

  def check(self, give_error: bool = True, recursive: bool = True) -> bool:
    """Проверить наличие модулей"""
    for i in self.depends:
      if not i in self.existing_modules:
        if not i in self.missing_modules:
          try:
            dist = pkg_resources.get_distribution(i)
            self.existing_modules.append(dist.egg_name())
            if recursive:
              recursive_check(dist)
          except Exception:
            self.missing_modules.append(i)
    if len(self.missing_modules) == 0:
      return True
    text = self.lang["core/missing_modules"] % ", ".join(self.missing_modules)
    if give_error:
      raise ImportError(text)
    print(text, file=sys.stderr)
    return False


def recursive_check(self: Depends, dist: pkg_resources.Distribution):
  for k in dist.requires():
    if not k in self.existing_modules:
      if not k in self.missing_modules:
        try:
          v = pkg_resources.get_distribution(k)
          self.existing_modules.append(v.egg_name)
          recursive_check(self, v)
        except Exception:
          self.missing_modules.append(k.name)
