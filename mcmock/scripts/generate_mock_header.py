#!/usr/bin/python
# @file generate_mock_header.py
# @author matthew.denis.conway@gmail.com
# @description Generate a mock header file


from mock_templates import *
from mcmock_utils import *
from datetime import datetime


class GenerateMockHeader:


    # API to get the generated file content of the mock header
    def get_mock_header_file_contents( self, filename, mocked_header_name ):
        retval = self.file_source
        retval = retval.replace( '<filename>', filename )
        retval = retval.replace( '<mocked_header_name>', mocked_header_name )
        return retval


    def __init__( self, pre_parsed_header, mock_data_builder, component_to_mock_name, mocked_header_name ):
        generation_date = "%02d/%02d/%04d"%( datetime.now().day, datetime.now().month, datetime.now().year )
        mock_file_banner = mocked_file_banner_template.replace( "<generation_date>", generation_date )
        file_data = self.__add_application_included_headers( pre_parsed_header.get_included_application_header_list(), mocked_header_name )
        file_data += self.__add_system_included_headers( pre_parsed_header.get_included_system_header_list() )
        file_data += self.__add_mock_type_definitions( mock_data_builder.get_mock_typedefs() )
        file_data += self.__create_mock_api_definitions( mock_data_builder.get_build_mock_data() )
        self.file_source = file_data
        self.file_source = mock_header_include_guard_template.replace( "<header_file_banner>", mock_file_banner )
        self.file_source = self.file_source.replace( "<source_code>", file_data )
        self.file_source = self.file_source.replace( "<mock_name>", component_to_mock_name )
        self.file_source = self.file_source.replace( "<mock_name_upper>", component_to_mock_name.upper() )


    def __add_application_included_headers( self, included_application_headers, mocked_header_name ):
        headers = '#include \"%s\"\n'%( mocked_header_name )
        if included_application_headers:
            for header in included_application_headers:
                headers += template_included_application_header.replace( '<include_name>', header )
        headers += "\n"
        return headers


    def __add_system_included_headers( self, included_system_headers ):
        headers = ''
        if included_system_headers:
            for header in included_system_headers:
                headers += template_included_system_header.replace( '<include_name>', header ) + "\n"
        headers += "\n"
        return headers


    def __add_mock_type_definitions( self, mock_typedefs ):
        typedefs = ''
        for t in mock_typedefs:
            typedefs += template_create_callback_typedef.replace( '<typedef_name>', t.typedef_name() ).replace( '<callback_type>', t.callback_type() ).replace( '<callback_name>', t.callback_name() )
        typedefs += '\n'
        return typedefs


    def __create_mock_api_definitions( self, mock_apis ):
        mock_definitions = ""
        adding_for_api_name = ''
        for mock in mock_apis:
            api_definition = ''
            if adding_for_api_name != mock.mocked_api_name():
                adding_for_api_name = mock.mocked_api_name()
                if ( adding_for_api_name != 'mockcontrol' ):
                    api_definition = '\n/* UnitTest APIs for %s() */\n'%( adding_for_api_name )
                else:
                    api_definition == '\n'
            api_definition += '%s %s('%( mock.return_type(), mock.name() )
            params_string = mcmock_utils_convert_params_list_to_string( mock.parameters() )
            api_definition += "%s)"%(params_string)
            mock_definitions += "%s;\n"%( api_definition )
        return mock_definitions

