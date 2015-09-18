#!/usr/bin/env python
'''
Python Setup script for blackflow package
'''
import sys
from setuptools import setup, find_packages

# Read version from VERSION file
try:
    with open("VERSION", "r") as fd: 
        VERSION = fd.read().strip()
    print("VERSION: %s" % VERSION)

except:
    sys.stderr.write("Unable to read package version...\n")
    exit(1)

# The Setup definition
setup(name        = 'Blackflow',
      version     = VERSION,
      description = 'Reactive apps execution runtime environment',
      author      = 'Aleksandrs Livincovs',
      author_email= 'aleksandrs.livincovs@gmail.com',
      packages    = find_packages(exclude=['apps*','tests']),
      scripts     = ['blackflow/blackflow_service.py'],
      package_data = {'':['*.json']}
     )