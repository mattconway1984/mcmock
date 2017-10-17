#!/usr/bin/python
#
# @file mcmock.py
#
# @author mconway@Espial.com
#
# @description Run mcmock from the command line.
#
# Copyright (C) Espial Limited 2017 Company Confidential - All Rights Reserved
#

import os
import sys

sys.path.insert( 0, os.path.abspath( os.path.join( os.path.dirname( __file__ ), 'scripts') ) )

import mcmock

mcmock.run_from_cmd_line( sys.argv )
