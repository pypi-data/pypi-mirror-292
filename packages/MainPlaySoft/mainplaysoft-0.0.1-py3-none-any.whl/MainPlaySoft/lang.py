texts = {}
texts["en"] = {}
texts["ru"] = {}
texts["en"]["core/missing_modules"] = "Modules %s were not found"
texts["en"]["core/unknown_os"] = "Unknown operating system: %s"
texts["ru"]["core/missing_modules"] = "Модули %s не найдены"
texts["ru"]["core/unknown_os"] = "Неизвестная операционная система: %s"


class Lang:
  def __init__(self, lang_code: str):
    """Тексты MainPlaySoft для разных языков"""
    self._code = None
    self.code = lang_code

  def __contains__(self, k):
    if k in texts[self.code]:
      return True
    return k in texts["ru"]

  def __getitem__(self, k) -> str:
    if k in texts[self.code]:
      return texts[self.code][k]
    return texts["ru"][k]

  def __setitem__(self, k, v):
    texts[self.code][k] = v

  @property
  def code(self) -> str:
    return self._code

  @code.setter
  def code(self, v):
    if not v in texts:
      texts[v] = {}
    self._code = v
