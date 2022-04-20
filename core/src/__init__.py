"""
Python Env: Py2.7 & Py3.8
"""
import os
import sys

cwd = os.getcwd()
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)
