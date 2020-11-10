#!/usr/bin/python
# @file mcmock_types.py
# @author matthew.denis.conway@gmail.com
# @description Custom types used by mcmock


from enum import Enum

# List of things that can be typedef'd in C
class TypedefType(Enum):
    TYPEDEF_STRUCT = 0      # Declaring a custom C data structure
    TYPEDEF_ENUM = 1        # Declaring a custom enumeration type
    TYPEDEF_CALLBACK = 2    # Delcaring a function pointer
    TYPEDEF_CUSTOM = 3      # Declaring a some other custom data type
    TYPEDEF_UNKNOWN = 4

    def to_string( self ):
        if type == TypedefType.TYPEDEF_STRUCT:
            return 'TypedefType.TYPEDEF_STRUCT'
        elif type == TypedefType.TYPEDEF_ENUM:
            return 'TypedefType.TYPEDEF_ENUM'
        elif type == TypedefType.TYPEDEF_CALLBACK:
            return 'TypedefType.TYPEDEF_CALLBACK'
        elif type == TypedefType.TYPEDEF_CUSTOM:
            return 'TypedefType.TYPEDEF_CUSTOM'
        else:
            return 'TypedefType.TYPEDEF_UNKNOWN'


# Class to encapsulate a typedef
class Typedef:

    def type( self ):
        return self._type

    def name( self ):
        return self._name

    def data( self ):
        return self._data

    def __init__( self, type, name, data ):
        self._type = type
        self._name = name
        self._data = data

#CallbackTypedef (
#    catch_parameter_typedef_name,
#    param.data_type(),
#    param.name(),
#    function.name()
#)

# Class to encapsulate a typedef describing a callback (function pointer)
class CallbackTypedef:

    def typedef_name( self ):
        return self._typedef_name

    def callback_type( self ):
        return self._callback_type

    def callback_name( self ):
        return self._callback_name

    def function_name( self ):
        return self._function_name

    def __init__( self, typedef_name, callback_type, callback_name, function_name ):
        self._typedef_name = typedef_name
        self._callback_type = callback_type
        self._callback_name = callback_name
        self._function_name = function_name


# Class to encapsulate a defined symbol
class DefinedSymbol:

    def name( self ):
        return self._name

    def value( self ):
        return self._value

    def __init__( self, name, value ):
        self._name = name
        self._value = value



# List of API types used by unittest code
class MockApiType(Enum):
    TYPE_MOCK_CONTROL = 0
    TYPE_EXPECT_AND_RETURN = 1
    TYPE_EXPECT = 2
    TYPE_IGNORE_ARG = 3
    TYPE_REGISTER_CALLBACK = 4
    TYPE_INVOKE_CALLBACK = 5
    TYPE_VERIFY_IN_POINTER = 6
    TYPE_CATCH_PARAMETER = 7


# List types of parameters
class ParameterType(Enum):
    PARAMETER_VALUE = 0             # Input value parameter (i.e. 'int age')
    PARAMETER_IN_POINTER = 1        # Pointer to input data for the function
    PARAMETER_OUT_POINTER = 2       # Pointer to data the function will modify
    PARAMETER_FUNCTION_POINTER = 3  # Function pointer
    PARAMETER_CALLBACK = 4          # Callback (a typedef function pointer)
    PARAMETER_VA_LIST = 5           # Parameter is a VA List
    PARAMETER_RETVAL = 6            # A return value (only used by mock APIs)
    PARAMETER_UNKNOWN = 7

    def to_string( self ):
        if type == ParameterType.PARAMETER_IN_POINTER:
            return 'ParameterType.PARAMETER_IN_POINTER'
        elif type == ParameterType.PARAMETER_OUT_POINTER:
            return 'ParameterType.PARAMETER_OUT_POINTER'
        elif type == ParameterType.PARAMETER_FUNCTION_POINTER:
            return 'ParameterType.PARAMETER_FUNCTION_POINTER'
        elif type == ParameterType.PARAMETER_VALUE:
            return 'ParameterType.PARAMETER_VALUE'
        elif type == ParameterType.PARAMETER_VA_LIST:
            return 'ParameterType.PARAMETER_VA-LIST'
        else:
            return 'ParameterType.PARAMETER_UNKNOWN'


# Class to encapsulate data describing a function parameter
class Parameter:

    def type( self ):
        return self._type

    def data_type( self ):
        return self._data_type
        # data_type = '(int)(*func_ptr_name)(int, char, bool)'

    def name( self ):
        return self._name
        # name = 'func_ptr_name'

    # type = Set to one of the values described in enum <ParameterType>
    # data_type = The data type of the parameter (i.e. int, char, bool etc.)
    # name = The parameters name (i.e. "house_number")
    def __init__( self, type, data_type, name ):
        self._type = type
        self._data_type = data_type
        self._name = name


# Class to encapsulate data describing a function definition
class Function:

    def name( self ):
        return self._name

    def return_type( self ):
        return self._return_type

    def parameters( self ):
        return self._parameter_list

    # name = Name of the function pointer
    # return_type = The return type of the function pointer
    # parameter_list = List of <Parameter> objects, one for each parameter of
    # the function pointer.
    def __init__( self, name, return_type, parameter_list ):
        self._name = name
        self._return_type = return_type
        self._parameter_list = parameter_list


# Class to encapsulate data describing a mock function definition
class MockFunction( Function ):

    def mock_type( self ):
        return self._mock_type

    def mocked_api_name( self ):
        return self._mocked_api_name

    # mock_type = The type of mock API, see class MockApiType
    # mocked_api_name = The name of the API which is being mocked
    def __init__( self, name, return_type, parameter_list, mock_type, mocked_api_name ):
        Function.__init__( self, name, return_type, parameter_list )
        self._mock_type = mock_type
        self._mocked_api_name = mocked_api_name



