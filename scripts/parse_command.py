#!/usr/bin/python
# @file command_parser.py
# @author mconway@Espial.com
# @description Parse the command issued to run mcmock
# Copyright (C) Espial Limited 2017 Company Confidential - All Rights Reserved


import sys
import re
from os import path, getcwd


help_string = \
"""mcmock Version 1.0
Tool for auto-generating mock files for C headers

EXAMPLES:
    generate_mock.py header_to_mock.h
    generate_mock.py -o /tmp/mocks/ -r /usr/include -m header_one.h header_two.h
    generate_mock.py -o /tmp/mocks/ -r /usr/include -i /usr/custom_include -m header_one.h header_two.h

OPTIONS:
    -h  display mcmock help
    -o  path where to put generated mock files (if not supplied, cwd will be used)
    -r  path to the root directory where include files live
    -i  (space separated) list of additional include directories
    -m  (space separated) list of header files to mock
"""


arg_options = [ '-o', '-m', '-r', '-i' ]


class ParseCommand:


    def get_command_data( self ):
        return self.command_data

    def get_command_errors( self ):
        return self.command_data['errors']

    def show_help_message( self ):
        return self.command_data['show_help']

    def get_help_message( self ):
        return help_string

    def get_headers_to_mock( self ):
        return self.command_data['headers_to_mock']

    def get_root_include_directory( self ):
        return self.command_data['root_include_directory']

    def get_output_directory( self ):
        return self.command_data['output_directory']

    def get_additional_includes( self ):
        return self.command_data['additional_includes']


    def __init__( self, command_args ):
        self.command_data = {}
        self.command_data['headers_to_mock'] = []
        self.command_data['additional_includes'] = []
        self.command_data['root_include_directory'] = ''
        self.command_data['output_directory'] = getcwd()
        self.command_data['errors'] = ''
        self.command_data['show_help'] = False
        if self.__check_command_length( command_args ):
            self.command_data['errors'] = self.__parse_command( command_args )


    def __check_command_length( self, command_args ):
        result = False
        if ( len( command_args ) <= 1 ):
            self.command_data['errors'] = "ERROR: No header files supplied; mcmock can't mock thin air.\nUse -h for more help"
        else:
            if ( len( command_args ) == 2 and ( command_args[1] == '-h' or command_args[1] == '--help') ):
                self.command_data['show_help'] = True
            else:
                result = True
        return result


    def __parse_command( self, command_args ):
        errors = ''
        i = 1
        while ( i < len( command_args ) and not errors):
            arg = command_args[i]
            if ( arg == '-o' ):
                if ( len( command_args ) >= i + 1 ):
                    output_directory = command_args[i+1]
                    if ( not path.exists( output_directory ) or not path.isdir( output_directory ) ):
                        errors = "ERROR: Output directory %s does not exist. Please create it before running this mcmock."%( output_directory )
                    else:
                        if ( output_directory[len(output_directory)-1] != '/' ):
                            output_directory += '/'
                    self.command_data['output_directory'] = output_directory
                else:
                    errors = "ERROR: found -o option with no output directory specified\nTry -h for usage"
                i+=2
            elif ( arg == '-m' ):
                if ( len( command_args ) >= i + 1 ):
                    j = i + 1
                    while ( j < len( command_args ) and not errors ):
                        arg = command_args[j]
                        if arg in arg_options:
                            break;
                        matched = re.match( r'([\/A-Za-z0-9_-]+)(.h)', arg )
                        if matched:
                            self.command_data['headers_to_mock'].append( arg )
                        else:
                            errors = "ERROR: Expected C header file, but got [%s]\nTry -h for usage"%( arg )
                        j+=1
                    i=j
                else:
                    errors = "ERROR: found -m option with no files to mock specified\nTry -h for usage"
            elif ( arg == '-r' ):
                if ( len( command_args ) >= i + 1 ):
                    root_include_directory = command_args[i+1]
                    if ( not path.exists( root_include_directory ) or not path.isdir( root_include_directory ) ):
                        errors = "ERROR: The includes root directory %s does not exist."%( root_include_directory )
                    else:
                        if ( root_include_directory[len( root_include_directory ) - 1] != '/' ):
                            root_include_directory += '/'
                    self.command_data['root_include_directory'] = root_include_directory
                else:
                    errors = "ERROR: found -r option with no root include directory specified\nTry -h for usage"
                i+=2
            elif ( arg == '-i' ):
                if ( len( command_args ) > i + 1 ):
                    j = i + 1
                    while ( j < len( command_args ) and not errors ):
                        arg = command_args[j]
                        if arg in arg_options:
                            break;
                        if ( not path.exists( arg ) or not path.isdir( arg ) ):
                            errors = "ERROR: The additional include directory %s does not exist."%( arg )
                        else:
                            if ( arg[len(arg)-1] != '/' ):
                                arg += '/'
                        self.command_data['additional_includes'].append( command_args[j] )
                        j+=1
                    i=j
                else:
                    errors = "ERROR: found -i option with no additional includes specified\nTry -h for usage"
            else:
                errors = "ERROR: Unknown arg %s\nTry -h for usage"%(arg)
        if not errors and not self.command_data['headers_to_mock']:
            errors = "ERROR: No header(s) to be mocked were specified\nTry -h for usage"
        return errors

