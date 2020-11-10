#!/usr/bin/python
#
# @file mcmock.py
#
# @author matthew.denis.conway@gmail.com
#
# @description Run mcmock from the command line.
#

import os
import sys

sys.path.insert( 0, os.path.abspath( os.path.join( os.path.dirname( __file__ ), 'scripts') ) )

import mcmock

mcmock.run_from_cmd_line( sys.argv )
