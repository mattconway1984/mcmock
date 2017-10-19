#!/usr/bin/python
# @file build_mock_data.py
# @author matthew.denis.conway@gmail.com
# @description Parses the parsed C header data and creates the data required for
# the mock implementation to be generated


from mcmock_types import *
from mcmock_utils import *
from mock_templates import *
from parse_c_header import CHeaderParser


class MockDataBuilder:


    # Public API to get a list of all the unittest APIs that must be added to
    # the mock
    def get_build_mock_data( self ):
        return self.unittest_apis

    # Public API to get a list of all the unittest generated typedefs that must
    # be added to the mock header
    def get_mock_typedefs( self ):
        return self.mock_typedefs

    #
    # PRIVATE IMPLEMENTATION
    #
    def __init__( self, parsed_header, pre_parsed_included_headers ):
        self.unittest_apis = []
        self.mock_typedefs = []
        for function in parsed_header.get_function_list():
            self.unittest_apis += self.__add_expectation_api_for_function_to_mock( function )
            self.unittest_apis += self.__add_ignore_param_apis_for_function_to_mock( function )
            self.unittest_apis += self.__add_verify_in_pointer_data_apis_for_function_to_mock( function )
            self.unittest_apis += self.__add_catch_parameter_apis_for_function_to_mock( function )


    def __add_expectation_api_for_function_to_mock( self, function ):
        mock_api_type = self.__get_func_expectation_type( function.return_type() )
        parameter_list = []
        for parameter in function.parameters():
            if parameter.type() == ParameterType.PARAMETER_CALLBACK:
                typedef_name = template_callback_typedef_name.replace( '<function_name>', function.name() ).replace( '<callback_name>', parameter.name() )
                self.mock_typedefs.append(
                    CallbackTypedef (
                        typedef_name,
                        parameter.data_type(),
                        parameter.name(),
                        function.name()
                    )
                )
                # Create a new parameter that allows unit tests to hook into
                # this callback and add it to the list.
                parameter_list.append(
                    Parameter(
                        ParameterType.PARAMETER_CALLBACK,
                        typedef_name,
                        "callback"
                    )
                )
            else:
                parameter_list.append( parameter )

        if mock_api_type == MockApiType.TYPE_EXPECT_AND_RETURN:
            parameter_list.append(
                Parameter(
                    ParameterType.PARAMETER_RETVAL,
                    function.return_type(),
                    'retval'
                )
            )
            expectation_name = 'mock_%s_expect_and_return'%( function.name() )
        else:
            expectation_name = 'mock_%s_expect'%( function.name() )
        return [
            MockFunction( expectation_name, 'void', parameter_list, mock_api_type, function.name() )
        ]


    def __add_ignore_param_apis_for_function_to_mock( self, function ):
        ignore_parameter_apis = []
        for param in function.parameters():
            # No need to add "ignore parameter" APIs for callbacks/function pointers
            if not param.type() == ParameterType.PARAMETER_CALLBACK:
                ignore_parameter_apis.append(
                    MockFunction(
                        'mock_%s_ignore_arg_%s'%( function.name(), param.name() ),
                        'void',
                        [],
                        MockApiType.TYPE_IGNORE_ARG,
                        function.name()
                    )
                )
        return ignore_parameter_apis


    def __get_func_expectation_type( self, ret_type ):
        type = MockApiType.TYPE_EXPECT
        if ( ret_type != 'void' ):
            type = MockApiType.TYPE_EXPECT_AND_RETURN
        return type


    def __add_verify_in_pointer_data_apis_for_function_to_mock( self, function ):
        verify_in_pointer_parameter_apis = []
        for param in function.parameters():
            if param.type() == ParameterType.PARAMETER_IN_POINTER:
                verify_in_pointer_parameter_apis.append(
                    MockFunction(
                        'mock_%s_verify_pointer_data_%s'%( function.name(), param.name() ),
                        'void',
                        [ Parameter(
                            ParameterType.PARAMETER_VALUE,
                            'size_t',
                            'buffer_size'
                        ) ],
                        MockApiType.TYPE_VERIFY_IN_POINTER,
                        function.name()
                    )
                )
        return verify_in_pointer_parameter_apis


    def __add_catch_parameter_apis_for_function_to_mock( self, function ):
        catch_parameter_apis = []
        for param in function.parameters():
            if param.type() == ParameterType.PARAMETER_IN_POINTER:
                catch_parameter_api_name = template_catch_parameter_api_name.replace( '<function_name>', function.name() ).replace( '<param_name>', param.name() )
                catch_parameter_typedef_name = template_catch_parameter_typedef_name.replace( '<api_name>', catch_parameter_api_name )
                self.mock_typedefs.append(
                    CallbackTypedef (
                        catch_parameter_typedef_name,
                        param.data_type(),
                        param.name(),
                        function.name()
                    )
                )
                catch_parameter_apis.append(
                    MockFunction(
                        catch_parameter_api_name,
                        'void',
                        [ Parameter(
                            ParameterType.PARAMETER_CALLBACK,
                            catch_parameter_typedef_name,
                            "callback"
                        ) ],
                        MockApiType.TYPE_CATCH_PARAMETER,
                        function.name()
                    )
                )
        return catch_parameter_apis


