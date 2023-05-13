# Main.py

from parser_1 import *

filename = "yap3.yalp"
yap_file = 'YAPar/' + filename

yapar = Parser(yap_file)

yapar.compiler()
