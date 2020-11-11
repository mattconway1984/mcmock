import os.path
import re

from mcmock.strip_c_header import StripCHeader
from mcmock.pre_parse_c_header import PreParseCHeader
from mcmock.pre_process_c_header import PreProcessCHeader
from mcmock.parse_c_header import CHeaderParser
from mcmock.build_mock_data import MockDataBuilder
from mcmock.generate_mock_source import GenerateMockSource
from mcmock.generate_mock_header import GenerateMockHeader
from mcmock.mcmock_utils import *


class GenerateMock:
    """
    Generate a mock implementation of a header file and also generate

    Args:
        header_to_mock (PathLib.Path): The header to be mocked.
        include_path (list[PathLib.Path]): List of include paths to other headers.
        output_path (PathLib.Path): Output path (where generated mocks will be written).
    """

    # TODO: Modified the init args, no tests to verify so can't know if anything
    # has been broken:
    def __init__(
            self,
            header_to_mock,
            include_paths,
            output_path):
        self._create_mock_names( header_to_mock )
        self.include_mocked_header = header_to_mock
        self._preprocess_and_parse_header_file(header_to_mock, include_paths)
        self.__generate_mock_files()
        if not output_directory.endswith( '/' ):
            output_directory = output_directory + '/'

    def generate(self):
        # TODO: This needs to be fixed
        print(f"Opening header file to mock: {header_to_mock}")
        self.__write_mock_header_file(output_directory + os.path.dirname( header_to_mock ) + '/' )
        self.__write_mock_source_file(output_directory + os.path.dirname( header_to_mock ) + '/' )

    def _create_mock_names(self, header_to_mock):
        header_to_mock = os.path.basename(header_to_mock)
        self.mock_name = header_to_mock.split('.h', 1 )[0].replace("/", "_")
        self.header_file_name = "mock_%s.h"%(self.mock_name)
        self.source_file_name = "mock_%s.c"%(self.mock_name)
        self.mocked_header_name = header_to_mock

    def _strip_empty_lines(self, data: list[str]):
        stripped = []
        for line in data:
            if not (re.match(r'^\s*$', line)):
                stripped.append(line.strip())
        return stripped

    def _strip_comments(self, data: list[str]):
        return \
            re.sub(
                r'(\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*\/+)|(//.*)',
                '',
                "".join(data)).splitlines()

    def _preprocess_and_parse_header_file(self, header_to_mock, include_paths):
        # Creates the following data items:
        #
        # self.pre_parsed_header            # Pre-Parsed instance of the "header to mock" (#includes, #defines & typedefs)
        # self.pre_parsed_included_headers  # Pre-Parsed instances of any (available) headers included by "header to mock"
        # self.parsed_header                # Parsed instance (contains the parsed APIs) of the "header to mock"

        print(f"Opening header file to mock: {header_to_mock}")
        header_file_data = None
        with header_to_mock.open("r") as handle:
            header_file_data = handle.readlines()

        header_file_data = self._strip_empty_lines(header_file_data)
        header_file_data = self._strip_comments(header_file_data)

        self.pre_parsed_header = \
            PreParseCHeader(header_to_mock, header_file_data)

    ######

    # TODO: CONTINUE FROM HERE - note there could well be errors in the
    # refactor above, without tests it's impossible to tell as this code is
    # pretty rotten.

    ######

        # The "header to mock" may include other header files - each of these
        # must be individually parsed to extract key information about any
        # custom data types that may be defined - and used by "header to mock".
        # NOTE: Currently only the application includes are pre-parsed, it may
        # need expanding to also check in the system/library includes and
        # pre-parse them as well.
        self.pre_parsed_included_headers = []

        path_to_included_header = None
        for included_header in self.pre_parsed_header.get_included_application_header_list():
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
        sprint( "Generated mock source file:  ", os.path.realpath( output_directory + self.source_file_name ) )
        mock_source_file_handle = open( output_directory + self.source_file_name, "w+" )
        mock_source_file_handle.write( self.mock_source.get_mock_source_file_contents( self.source_file_name, self.mocked_header_name ) )
        mock_source_file_handle.close()

