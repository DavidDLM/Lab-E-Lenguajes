# Main.py

from parser_1 import *

filename = "yap3.yalp"
yaparFilename = 'YAPar/' + filename
yapar = Parser(yaparFilename)
yapar.compiler()
