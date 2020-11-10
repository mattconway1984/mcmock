#!/usr/bin/python
# @file create_mock_source.py
# @author matthew.denis.conway@gmail.com
# @description Generate a mock source file


from datetime import datetime
from mock_templates import *
from mcmock_utils import *
from mcmock_types import *


class GenerateMockSource:


    # API to get the generated file content of the mock source
    def get_mock_source_file_contents( self, filename, mocked_header_name ):
        retval = self.file_source
        retval = retval.replace( '<filename>', filename )
        retval = retval.replace( '<mocked_header_name>', mocked_header_name )
        return retval


    def __init__( self, pre_parsed_header, parsed_header, mock_data_builder, component_to_mock_name, include_mocked_header ):
        self.file_source = self.__add_file_banner( component_to_mock_name )
        self.file_source += self.__add_default_included_headers( component_to_mock_name, include_mocked_header )
        self.file_source += self.__add_application_included_headers( pre_parsed_header.get_included_application_header_list() )
        self.file_source += self.__add_system_included_headers( pre_parsed_header.get_included_system_header_list() )
        self.file_source += self.__add_mocked_api_string_names( parsed_header.get_function_list() )
        self.file_source += self.__add_data_structures_for_api_conditions( parsed_header.get_function_list(), mock_data_builder )
        self.file_source += template_banner_mocked_apis
        self.file_source += self.__build_mocked_apis( parsed_header )
        self.file_source += template_banner_for_unittest_apis
        self.file_source += self.__build_unittest_apis( mock_data_builder.get_build_mock_data() )


    def __add_file_banner( self, component_to_mock_name ):
        generation_date = "%02d/%02d/%04d"%( datetime.now().day, datetime.now().month, datetime.now().year )
        file_banner = mocked_file_banner_template
        file_banner = file_banner.replace( "<generation_date>", generation_date )
        return file_banner


    def __add_default_included_headers( self, component_to_mock_name, include_mocked_header ):
        result = template_default_includes.replace( '<mocked_header_name>', component_to_mock_name )
        result = result.replace( '<mocked_header>', include_mocked_header )
        return result


    def __add_application_included_headers( self, included_application_headers ):
        headers = ''
        if included_application_headers:
            for header in included_application_headers:
                headers += template_included_application_header.replace( '<include_name>', header )
            headers += '\n'
        return headers


    def __add_system_included_headers( self, included_system_headers ):
        headers = ''
        if included_system_headers:
            for header in included_system_headers:
                headers += template_included_system_header.replace( '<include_name>', header )
            headers += '\n'
        return headers


    def __add_mocked_api_string_names( self, function_list ):
        api_names = template_mocked_apis_comment
        for func in function_list:
            api_names += template_mocked_api_string.replace( '<api_name>', func.name() )
        return api_names


    def __build_conditions_list_for_parameters( self, function, mock_data_builder ):
        items_to_add = { 'param_list':[], 'ignore_list':[], 'verify_list':[], 'catch_list':[] }
        # Each parameter must be added to the structure to store it's expected value, and an ignore
        # flag must be added so the mock knows whether it needs to compare the value passed in by
        # the code under test.
        for param in function.parameters():
            if not param.name() == "...":
                if param.type() == ParameterType.PARAMETER_FUNCTION_POINTER:
                    items_to_add['param_list'] += template_mock_conditions_function_pointer_arg.replace( '<function_pointer>', param.data_type() )
                elif param.type() == ParameterType.PARAMETER_VA_LIST:
                    items_to_add['param_list'] += template_mock_conditions_va_list.replace( '<name>', param.name() )
                elif param.type() == ParameterType.PARAMETER_CALLBACK:
                    # TODO : This assumes one callback per function, which may not be the case, so this must be improved.
                    for t in mock_data_builder.get_mock_typedefs():
                        if t.function_name() == function.name():
                            items_to_add['param_list'] += template_mock_conditions_standard_arg.replace( '<type>', t.typedef_name() ).replace( '<name>', t.callback_name() )
                else:
                    # For each IN_POINTER, two APIs are added:
                    #   1. allowing the unittest to make the mock to verify the contents of the input pointer it passed into the mock
                    #   2. allowing the unittest to grab the input pointer passed into the mock by the code under test (through the unit test code registering a callback with the mock)
                    if param.type() == ParameterType.PARAMETER_IN_POINTER:
                        items_to_add['verify_list'] += template_mock_conditions_verify_pointer_arg.replace( '<name>', param.name() )
                        for t in mock_data_builder.get_mock_typedefs():
                            if t.function_name() == function.name() and t.callback_name() == param.name() and t.callback_type() == param.data_type():
                                items_to_add['catch_list'] += template_mock_conditions_catch_parameter_arg.replace( '<type>', t.typedef_name() ).replace( '<name>', param.name() )
                    items_to_add['param_list'] += template_mock_conditions_standard_arg.replace( '<type>', mcmock_utils_strip_constness( param.data_type() ) ).replace( '<name>', param.name() )
                items_to_add['ignore_list'] += template_mock_conditions_ignore_arg.replace( '<name>', param.name() )
        return items_to_add


    def __build_conditions_data_for_api( self, function, mock_data_builder ):
        items_to_add = self.__build_conditions_list_for_parameters( function, mock_data_builder )
        retval = ''
        for param in items_to_add['param_list']:
            retval += param
        for ignore in items_to_add['ignore_list']:
            retval += ignore
        for verify in items_to_add['verify_list']:
            retval += verify
        for verify in items_to_add['catch_list']:
            retval += verify
        if ( function.return_type() != 'void' ):
            retval += template_mock_conditions_return_value.replace( '<type>', function.return_type() )
        return retval


    def __add_data_structures_for_api_conditions( self, function_list, mock_data_builder ):
        all_api_conditions = ''
        for function in function_list:
            api_conditions = self.__build_conditions_data_for_api( function, mock_data_builder )
            current_api = template_mock_conditions_comment.replace( '<mocked_api>', function.name() )
            current_api += template_mock_conditions_structure.replace( '<conditions>', api_conditions ).replace( '<api_name>', function.name() )
            all_api_conditions += current_api
        return all_api_conditions


    #def __generate_mocked_api( self, api_name, parameters, return_type, verify_parameters, catch_parameters, store_callbacks, return_data ):
    def __generate_mocked_api( self, api_name, parameters, return_type, verify_parameters, store_callbacks, return_data ):
        mocked_api = template_mocked_api_skeleton
        mocked_api = mocked_api.replace( '<mocked_api_params_list>', parameters )
        mocked_api = mocked_api.replace( '<mocked_api_return_type>', return_type )
        mocked_api = mocked_api.replace( '<verify_params>', verify_parameters )
        #mocked_api = mocked_api.replace( '<catch_params>', catch_parameters )
        mocked_api = mocked_api.replace( '<mocked_api_name>', api_name )
        mocked_api = mocked_api.replace( '<store_callbacks>', store_callbacks )
        mocked_api = mocked_api.replace( '<return_data>', return_data )
        return mocked_api


    def __generate_verify_parameters_for_mocked_api( self, mocked_function_name, parameters ):
        verify_params = ''
        for param in parameters:
            # Can't ignore or verify callback parameters!
            if not param.type() == ParameterType.PARAMETER_CALLBACK:
                if param.type() == ParameterType.PARAMETER_IN_POINTER:
                    temp_str = template_mocked_api_verify_input_pointer_parameter.replace( '<param_name>', param.name() )
                    temp_str = temp_str.replace( '<mocked_api_name>', mocked_function_name )
                    verify_params += temp_str
                else:
                    verify_params += template_mocked_api_verify_parameter.replace( '<param_name>', param.name() )
        return verify_params


#    def __generate_catch_parameters_for_mocked_api( self, parameters ):
#        catch_params = ''
#        for param in parameters:
#            if param.type() == ParameterType.PARAMETER_IN_POINTER:
#                catch_params += template_mocked_api_catch_input_pointer_parameter.replace( '<param_name>', param.name() )
#        return catch_params


    def __generate_invoke_callback_for_mocked_api( self, parameters ):
        store_callbacks = ''
        for param in parameters:
            if param.type() == ParameterType.PARAMETER_CALLBACK:
                store_callbacks = template_mocked_api_handle_callback_parameter
        return store_callbacks


    def __generate_return_data_for_mocked_api( self, return_type ):
        retval = ''
        if not return_type == 'void':
            retval = template_mocked_api_set_return_data
        return retval;


    def __build_mocked_apis( self, parsed_header ):
        mocked_apis = ''
        for func in parsed_header.get_function_list():
            mocked_apis += \
                self.__generate_mocked_api(
                    func.name(),
                    mcmock_utils_convert_params_list_to_string( func.parameters() ),
                    func.return_type(),
                    self.__generate_verify_parameters_for_mocked_api( func.name(), func.parameters() ),
                    #self.__generate_catch_parameters_for_mocked_api( func.parameters() ),
                    self.__generate_invoke_callback_for_mocked_api( func.parameters() ),
                    self.__generate_return_data_for_mocked_api( func.return_type() ) )
        return mocked_apis


    def __build_unittest_apis( self, unittest_api_list ):
        source_code = ''
        for api in unittest_api_list:
            if ( api.mock_type() == MockApiType.TYPE_EXPECT_AND_RETURN or api.mock_type() == MockApiType.TYPE_EXPECT ):
                source_code += self.__build_add_expectation_api( api )
            elif ( api.mock_type() == MockApiType.TYPE_IGNORE_ARG ):
                source_code += self.__build_ignore_arg_api( api )
            elif ( api.mock_type() == MockApiType.TYPE_VERIFY_IN_POINTER ):
                source_code += self.__build_verify_parameter_api( api )
            elif ( api.mock_type() == MockApiType.TYPE_CATCH_PARAMETER ):
                source_code += self.__build_catch_parameter_api( api )
        return source_code


    def __build_store_conditions_for_add_expecataion_api( self, parameters ):
        set_conditions = ''
        ignore_conditions = ''
        for param in parameters:
            set_conditions += template_unittest_add_expectation_store_conditions.replace( '<parameter>', param.name() )
            if param.type() == ParameterType.PARAMETER_IN_POINTER:
                set_conditions += template_unittest_add_expectation_store_verify_in_pointer_conditions.replace( '<parameter>', param.name() )
        for param in parameters:
            if not param.name() == 'retval':
                ignore_conditions += template_unittest_add_expectation_store_ignore_conditions.replace( '<parameter>', param.name() )
        return set_conditions + ignore_conditions


    def __build_add_expectation_api( self, api ):
        expectation_api = template_unittest_add_expectation_api
        expectation_api = expectation_api.replace( '<expectation_api_name>', api.name() )
        expectation_api = expectation_api.replace( '<mocked_api_name>', api.mocked_api_name() )
        expectation_api = expectation_api.replace( '<expectation_parameters>', mcmock_utils_convert_params_list_to_string( api.parameters() ) )
        expectation_api = expectation_api.replace( '<store_expecatation_conditions>', self.__build_store_conditions_for_add_expecataion_api( api.parameters() ) )
        return expectation_api


    def __build_ignore_arg_api( self, api ):
        parameter_being_ignored = api.name().split('_ignore_arg_')[1]
        ignore_arg_api = template_unittest_ignore_arg_api
        ignore_arg_api = ignore_arg_api.replace( '<api_name>', api.name() )
        ignore_arg_api = ignore_arg_api.replace( '<mocked_api_name>', api.mocked_api_name() )
        ignore_arg_api = ignore_arg_api.replace( '<parameter_being_ignored>', parameter_being_ignored )
        return ignore_arg_api


    def __build_verify_parameter_api( self, api ):
        parameter_being_verified = api.name().split('_verify_pointer_data_' )[1]
        verify_arg_api = template_unittest_verify_in_pointer_api.replace( '<api_name>', api.name() )
        parameter_string = ""
        for param in api.parameters():
            parameter_string += "%s %s"%(param.data_type(), param.name())
        verify_arg_api = verify_arg_api.replace( '<parameters>', parameter_string )
        verify_arg_api = verify_arg_api.replace( '<mocked_api_name>', api.mocked_api_name() )
        verify_arg_api = verify_arg_api.replace( '<parameter_being_verified>', parameter_being_verified )
        return verify_arg_api


    def __build_catch_parameter_api( self, api ):
        parameter_being_caught = api.name().split('_catch_parameter_')[1]
        parameter_string = ''
        for param in api.parameters():
            parameter_string += "%s %s"%(param.data_type(), param.name())
        catch_parameter_api = template_unittest_catch_in_pointer_api.replace( '<api_name>', api.name() )
        catch_parameter_api = catch_parameter_api.replace( '<parameters>', parameter_string )
        catch_parameter_api = catch_parameter_api.replace( '<mocked_api_name>', api.mocked_api_name() )
        catch_parameter_api = catch_parameter_api.replace( '<parameter_being_caught>', parameter_being_caught )
        return catch_parameter_api

