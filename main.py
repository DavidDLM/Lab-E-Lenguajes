# Main.py

from parser_1 import *

filename = "yap3.yalp"
yap_filename = 'YAPar/' + filename

yapar = Parser(yap_filename)

yapar.compiler()
