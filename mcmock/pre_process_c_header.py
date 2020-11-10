#!/usr/bin/python
# @file pre_process_c_header.py
# @author matthew.denis.conway@gmail.com
# @description PreProcess a C header file, duplicating some functions of the
# Real C Pre-Processor.


import re

from mcmock.mcmock_types import ParameterType, Parameter, Function, TypedefType, Typedef, DefinedSymbol
from mcmock.mcmock_utils import *


class PreProcessCHeader:

    def get_pre_processed( self ):
        return self.pre_processed

    # API to pre process macros in the header file; this function will try to
    # replicate what the C Pre-Processor does by expanding macros in the header
    # file.
    # NOTE: This will probably not work for all macros, as it's very difficult
    # to replicate the C Pre-Processor!
    def __init__( self, pre_parsed_header, pre_parsed_included_headers ):
        self.pre_processed = []

        known_symbols_list = list( pre_parsed_header.get_defined_symbols())
        for header in pre_parsed_included_headers:
            for sym in header.get_defined_symbols():
                known_symbols_list.append( sym )
        # Go through each line of the source file replacing any macros
        working_copy = []
        for line in pre_parsed_header.get_unparsed_content():
            temp = ''
            for known_symbol in known_symbols_list:
                # Is the name of the known symbol the first word on current line?
                regexp_str = r'^\s*' + known_symbol.name() + '\s*\(\s*(.+)\s*\)'
                matched = re.match( regexp_str, line )
                if matched:
                    # Get the text that needs to be replaced
                    replace_this = matched.group(1).strip()
                    # Look at the known symbol and split it into two groups:
                    # Example: #define DO_SOMETHING( with ) with * 5
                    # group(1) = "with"
                    # group(2) = "with * 5"
                    value_matched = re.match( r'^\s*\(\s*(.+)\s*\)(.+)', known_symbol.value() )
                    if value_matched:
                        # Replace the macro name on the line with the macro
                        # i.e. "DO_SOMETHING( this )" becomes "this * 5"
                        temp = value_matched.group(2).replace( value_matched.group(1).strip(), replace_this ).strip()
                        # Copy the C Pre-Processor: Replace instances of #foo with "foo"
                        regexp_str = r'((\b|\s*)(?<!#)#'+replace_this+')'
                        temp = re.sub( regexp_str, '"'+replace_this+'"', temp )
                        # Copy the C Pre-Processor: Replace instances of foo##bar with foobar
                        temp = re.sub( r'\s*##\s*', '', temp )
            if temp == '':
                working_copy.append( line.strip() )
            else:
                working_copy.append( temp.strip() )
        self.pre_processed = list( working_copy )

