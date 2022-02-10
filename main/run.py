from os import system
from os import path
from sys import argv

MATH_PATH = path.dirname(path.realpath(argv[0]))
system(MATH_PATH + "\\translate\\translate.exe")
