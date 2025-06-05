import os
import sys

excel = ''
for _, _, filenames in os.walk('sample-nuruominoboards'):
    for file in filenames:
        if file.endswith('.txt') and not file.endswith('.out.txt'):
            excel += file
            excel += ','
            sys.system()