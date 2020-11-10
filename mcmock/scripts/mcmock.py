#!/usr/bin/python
# @file mcmock.py
# @author matthew.denis.conway@gmail.com
# @description Public API for the mcmock application

from parse_command import ParseCommand
from generate_mock import GenerateMock
from mcmock_utils import sprint, eprint, exit_on_error

import os


def generate_mocks( command_data ):
    for header in command_data.get_headers_to_mock():
        sprint( "Generating Mock for %s"%( header ) )
        mock_generator = \
            GenerateMock( \
                command_data.get_root_include_directory(), \
                command_data.get_output_directory(), \
                header, \
                command_data.get_additional_includes() )


def run_from_cmd_line( argv ):
    command_data = ParseCommand( argv )
    if command_data.get_command_errors():
        exit_on_error( command_data.get_command_errors() )
    elif not command_data.get_headers_to_mock():
        exit_on_error( command_data.get_help_message() )
    elif command_data.show_help_message():
        sprint( command_data.get_help_message() )
    else:
        generate_mocks( command_data )
