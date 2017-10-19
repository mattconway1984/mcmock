#!/usr/bin/python
# @file generate_mock.py
# @author matthew.denis.conway@gmail.com
# @description Generate a mock implementation of a header file and also generate
# unittest APIs that control the mock

import os.path
import re

from strip_c_header import StripCHeader
from pre_parse_c_header import PreParseCHeader
from pre_process_c_header import PreProcessCHeader
from parse_c_header import CHeaderParser
from build_mock_data import MockDataBuilder
from generate_mock_source import GenerateMockSource
from generate_mock_header import GenerateMockHeader

from mcmock_utils import *


class GenerateMock:


    def __remove_comments( self, unparsed_data ):
        # Convert the list of strings (the file data) into a single string
        full_file = ''
        for line in unparsed_data:
            full_file += line
        return re.sub( r'(\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*\/+)|(//.*)', '', full_file).splitlines()


    def __remove_whitespace_lines( self, unparsed_data ):
        stripped = []
        for line in unparsed_data:
            if not ( re.match(r'^\s*$', line) ):
                stripped.append( line.strip() )
        return stripped


    def __init__( self, root_include_directory, output_directory, header_to_mock, additional_include_directories=[] ):
        self.__create_mock_names( header_to_mock )
        self.include_mocked_header = header_to_mock
        self.__preprocess_and_parse_header_file( root_include_directory, header_to_mock, additional_include_directories )
        self.__generate_mock_files()
        if not output_directory.endswith( '/' ):
            output_directory = output_directory + '/'
        self.__write_mock_header_file( output_directory + os.path.dirname( header_to_mock ) + '/' )
        self.__write_mock_source_file( output_directory + os.path.dirname( header_to_mock ) + '/' )


    def __create_mock_names( self, header_to_mock ):
        # Only interested in the filname at this point...
        header_to_mock = os.path.basename( header_to_mock )
        self.mock_name = header_to_mock.split( '.h', 1 )[0].replace( "/", "_" )
        self.header_file_name = "mock_%s.h"%( self.mock_name )
        self.source_file_name = "mock_%s.c"%( self.mock_name )
        self.mocked_header_name = header_to_mock


    def __preprocess_and_parse_header_file( self, root_include_directory, header_to_mock, additional_include_directories ):
        # This is a very important function, it generates some very useful data
        # structures used to generate the mock, these are:
        #
        # self.pre_parsed_header            # Pre-Parsed instance of the "header to mock" (#includes, #defines & typedefs)
        # self.pre_parsed_included_headers  # Pre-Parsed instances of any (available) headers included by "header to mock"
        # self.parsed_header                # Parsed instance (contains the parsed APIs) of the "header to mock"

        # Ensure the path to the root of where the "header to mock" lives is
        # going to be valid before trying to open the file
        header_path = ""
        useful_error_msg = ""
        if os.path.isfile( os.path.join(root_include_directory, header_to_mock) ):
            header_path = os.path.join(root_include_directory, header_to_mock)
        else:
            useful_error_msg = "    Tried: " + os.path.join(root_include_directory, header_to_mock) + "\n"
            for include_dir in additional_include_directories:
                if os.path.isfile( os.path.join(include_dir, header_to_mock) ):
                    header_path = os.path.join(include_dir, header_to_mock)
                    break;
                else:
                    useful_error_msg = "    Tried: " + os.path.join(include_dir, header_to_mock) + "\n"
        if not header_path:
            exit_on_error( "ERROR: Could not find header file to mock: " + header_to_mock + "\n" + useful_error_msg )
        sprint( "Opening header file to mock: ", header_path )
        source_file_handle = open( header_path, "r" );
        header_file_data = source_file_handle.readlines()
        source_file_handle.close()

        working_copy = []
        working_copy = list( self.__remove_comments( header_file_data ) )
        working_copy = list( self.__remove_whitespace_lines( working_copy ) )
        header_file_data = list( working_copy )

        self.pre_parsed_header = PreParseCHeader( os.path.join(root_include_directory, header_to_mock), header_file_data )

        # The "header to mock" may include other header files - each of these
        # must be individually parsed to extract key information about any
        # custom data types that may be defined - and used by "header to mock".
        # NOTE: Currently only the application includes are pre-parsed, it may
        # need expanding to also check in the system/library includes and
        # pre-parse them as well.
        self.pre_parsed_included_headers = []
        for included_header in self.pre_parsed_header.get_included_application_header_list():
            path_to_included_header = None
            # Start by checking if the included header exists in the same
            # directory as the "header to mock". If it doesn't, check each
            # path supplied to MCMOCK in the list of additional include paths
            if os.path.isfile( os.path.join( root_include_directory, included_header ) ):
                path_to_included_header = included_header
            else:
                for inc_dir in additional_include_directories:
                    if not inc_dir.endswith('/'):
                        inc_dir += '/'
                    if os.path.isfile( inc_dir + included_header ):
                        path_to_included_header = inc_dir + included_header
                        break
            if path_to_included_header:
                included_header_handle = open( path_to_included_header, "r" );
                sprint("Pre-parsing included header: ", path_to_included_header)
                self.pre_parsed_included_headers.append( PreParseCHeader( path_to_included_header, included_header_handle.readlines() ) )
                included_header_handle.close()
            else:
                sprint( "WARNING: Could not find the included header[", included_header, "] for pre-parsing (without this, generating the mock may fail)" )
        pre_processed_header = PreProcessCHeader( self.pre_parsed_header, self.pre_parsed_included_headers )
        self.pre_parsed_header = PreParseCHeader( path_to_included_header, pre_processed_header.get_pre_processed() )
        temp_stripped = StripCHeader( self.pre_parsed_header, self.pre_parsed_included_headers )
        self.parsed_header = CHeaderParser( temp_stripped.get_stripped_data(), self.pre_parsed_header, self.pre_parsed_included_headers )



    def __generate_mock_files( self ):
        mock_data_builder = MockDataBuilder( self.parsed_header, self.pre_parsed_included_headers )
        self.mock_source = GenerateMockSource( self.pre_parsed_header, self.parsed_header, mock_data_builder, self.mock_name, self.include_mocked_header )
        self.mock_header = GenerateMockHeader( self.pre_parsed_header, mock_data_builder, self.mock_name, self.include_mocked_header )


    def __write_mock_header_file( self, output_directory ):
        sprint( "Generated mock header file:  ", os.path.realpath( output_directory + self.header_file_name ) )
        mock_header_file_handle = open( output_directory + self.header_file_name, "w+" )
        mock_header_file_handle.write( self.mock_header.get_mock_header_file_contents( self.header_file_name, self.mocked_header_name ) )
        mock_header_file_handle.close()


    def __write_mock_source_file( self, output_directory ):
        mock_source_file_handle = open( output_directory + self.source_file_name, "w+" )
        mock_source_file_handle.write( self.mock_source.get_mock_source_file_contents( self.source_file_name, self.mocked_header_name ) )
        mock_source_file_handle.close()

