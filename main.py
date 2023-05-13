# Main.py

from parser_1 import *

filename = "yap3.yalp"
yapFilename = 'YAPar/' + filename

yapar = Parser(yapFilename)

yapar.compiler()
