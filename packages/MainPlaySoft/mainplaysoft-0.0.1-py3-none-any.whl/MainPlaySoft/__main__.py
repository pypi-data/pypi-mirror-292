import sys
from . import MPSoft


def __main__():
  mpscore = MPSoft("MainPlaySoft", "MPSoftCore")
  print("Import example:", file=sys.stderr)
  print("from MainPlaySoft import MPSoft")
  print("mpscore=MPSoft('your name','name of the program')")


if __name__ == "__main__":
  exit(__main__())
