#!/usr/bin/python
# @file parse_c_header.py
# @author matthew.denis.conway@gmail.com
# @description Parse a C header file, creating logical python data structures
# for the definitions in the C header.


import re

from mcmock.mcmock_types import ParameterType, Parameter, Function, TypedefType, Typedef
from mcmock.mcmock_utils import *


class CHeaderParser:

    # API to get a list of functions defined in the header file. This is a list
    # of Function objects.
    def get_function_list( self ):
        return self.function_list


    def parse_function_parameter_list( self, function_name, function_parameters, pre_parsed_header, pre_parsed_included_headers ):
        return self.__parse_function_parameter_list( function_name, function_parameters, pre_parsed_header, pre_parsed_included_headers )


    def parse_function_pointer_type( self, f_ptr ):
        return self.__parse_function_pointer_string( f_ptr )


    #
    # PRIVATE IMPLEMENTATION
    #
    # CHeaderParser( stripped_header, pre_parsed_header, pre_parsed_included_headers )
    def __init__( self, pre_parsed_header, pre_parsed_included_headers ):
        working_copy = []
        self.function_list = []
        self.auto_gen_id = 0;
        working_copy = list( self.__merge_multiline_variable_definitions( pre_parsed_header.unparsed_content ) )
        working_copy = list( self.__concatenate_multi_line_split_lines( working_copy ) )
        working_copy = list( self.__parse_defined_variables( working_copy ) )
        self.__parse_function_definitions( working_copy, pre_parsed_header, pre_parsed_included_headers )


    def __parse_defined_variables( self, stripped_data ):
        working_copy = []
        for line in stripped_data:
            # TODO : Parse any variables that have been defined in the header.
            # Think about the best way to handle them.... Maybe they don't even
            # need to be parsed.... BUt if they do, look for things like:
            #int a;
            #extern int b;
            #unsigned int c;
            #extern unsigned int d;
            #extern unsigned int * e;
            #extern (*asdf)(int, char);
            #struct xyz{ int a; int b; };
            #extern struct uop{ int x; int z; };
            working_copy.append( line )
        return working_copy


    def __merge_multiline_variable_definitions( self, stripped_data ):
        working_copy = []
        brace_open_count = 0
        multi_liner = ''
        for line in stripped_data:
            line = line.strip()
            if line.startswith( '#' ):
                working_copy.append( line )
            else:
                # Variables like enums and structs that can be spread across multiple
                # lines need to be merged so their definition is only on one line
                x=0
                for x in range( 0, len( line ) ):
                    c = line[x]
                    if c == '{':
                        brace_open_count+=1
                    elif c == '}':
                        brace_open_count=0
                    if ( x+1 == len( line ) ):
                        if ( brace_open_count > 0 ):
                            multi_liner += line + ' '
                        else:
                            if ( multi_liner != '' ):
                                working_copy.append( multi_liner + ' ' + line )
                                multi_liner = ''
                            else:
                                working_copy.append( line )
                    x+=1
        return working_copy


    def __concatenate_multi_line_split_lines( self, unparsed_content ):
        working_copy = []
        i=0
        concatenated_line = ''
        if ( len( unparsed_content ) > 0 ):
            while( i < len( unparsed_content ) ):
                add_concatenated_line = False
                if unparsed_content[i].startswith('#'):
                    concatenated_line = unparsed_content[i]
                    add_concatenated_line = True
                else:
                    concatenated_line += unparsed_content[i] + ' '
                    re_result = re.search( ';', unparsed_content[i])
                    if ( re_result ):
                        add_concatenated_line = True
                if add_concatenated_line:
                    working_copy.append( concatenated_line.strip() )
                    concatenated_line = ''
                i += 1
        return working_copy


    def __parse_function_definitions( self, stripped_content, pre_parsed_header, pre_parsed_included_headers):
        for function in stripped_content:
            i = 0
            function_name_and_retval = ''
            while i < len( function ):
                char = function[i]
                if ( char == '(' ):
                    break;
                i += 1
            if ( i != len( function ) ):
                function_name_and_retval = self.__find_function_name_and_retval( function[0:i] )
                self.function_list.append(
                    Function(
                        function_name_and_retval['name'],
                        function_name_and_retval['ret_type'],
                        self.__parse_function_parameter_list(
                            function_name_and_retval['name'],
                            self.__get_parameter_list( function[i:len(function)] ),
                            pre_parsed_header,
                            pre_parsed_included_headers
                        )
                    )
                )


    def __find_function_name_and_retval( self, line ):
        f = {}
        parse_list = line.strip().replace( "extern", "" ).split( ' ' )
        f['name'] = parse_list.pop().strip()
        ptr_depth = f['name'].count('*')
        f['name'] = f['name'].replace("*","")
        f['ret_type'] = " ".join( parse_list ).strip()
        for x in range(0,ptr_depth):
            f['ret_type'] = f['ret_type'] + "*"
        if not f['name'] or not f['ret_type']:
            exit_on_error( "ERROR parsing line: ", line )
        return f


    def __get_parameter_list( self, function_parameters ):
        stripped_function_parameters = ''
        i = 0
        open_braces = 0;
        function_parameters = function_parameters.strip()
        while i < len( function_parameters ):
            if ( function_parameters[i] == '(' ):
                open_braces += 1
                # Don't include the first open brace; skip straight to next char
                if ( open_braces == 1 ):
                    i+=1
            if ( function_parameters[i] == ')'):
                open_braces -= 1
                # Don't include the final close brace
                if ( open_braces == 0 ):
                    break
            if ( open_braces > 0 ):
                stripped_function_parameters += function_parameters[i]
            i+=1
        return stripped_function_parameters


    def __get_next_parameter_from_parameter_string( self, parameter_string ):
        brace_open_count = 0
        i=0
        while i < len( parameter_string ):
            if parameter_string[i] == '(':
                brace_open_count += 1
            elif parameter_string[i] == ')':
                brace_open_count -= 1
            if brace_open_count == 0 and parameter_string[i] == ',':
                return \
                {
                    'parameter':parameter_string[0:i].strip(),
                    'remainder':parameter_string[i+1:].strip()
                }
                break
            else:
                i+=1
        # parameter_string only contains one parameter:
        return \
        {
            'parameter':parameter_string,
            'remainder':''
        }


    def __extract_function_pointer_parameter( self, parameter_list ):
        f_ptr_str = ''
        # Run a regex on the function parameter to extract three groups:
        # 1. The return type of the function
        # 2. The function pointer name
        # 3. The rest of the parameter list including parameters of the function
        #    pointer
        f_ptr_matched = re.match( r'^([^,*]+)(\(\ *\*\ *[A-Za-z0-9_]+\ *\))(.*)', parameter_list['parameter'] + parameter_list['remainder'] )
        if f_ptr_matched:
            f_ptr_str = f_ptr_matched.group(1).strip() + f_ptr_matched.group(2).strip()
        else:
            exit_on_error( "Failed to parse the function pointer parameter [", parameter_list, "]" )

        brace_open_count = 0
        i=0
        while i < len( f_ptr_matched.group(3) ):
            if f_ptr_matched.group(3)[i] == '(':
                brace_open_count += 1
            elif f_ptr_matched.group(3)[i] == ')':
                brace_open_count -= 1
            # Got to the end of the function pointer definition, so
            # extract the function pointer parameters and check if there
            # are any more parameters to be parsed (parameter_string).
            if brace_open_count == 0:
                f_ptr_str += f_ptr_matched.group(3)[0:i+1]
                break
            i+=1
        return {
            'f_ptr_str':f_ptr_str,
            'remainder':f_ptr_matched.group(3)[i+1:].strip()[1:]
        }


    # Returns a dictionary containing the function pointer data:
    # 'name' = function pointer name
    # 'return_type' = return type of the function pointer
    # 'parameters' = string containing the parameters for the function pointer
    def __parse_function_pointer_string( self, f_ptr_str ):
        function_pointer = {}
        # regex to extract information about the function ptr typedef:
        # group(1) is the function ptr return type
        # group(2) is the function pointer name
        # group(3) is the function pointer parameter list
        matched = re.match( r'^ *([A-Za-z0-9_]+) *(\(\ *\*\ *[A-Za-z0-9_]+\ *\))(.*)', f_ptr_str )
        if matched:
            function_pointer['return_type'] = matched.group(1)
            # regex to extract the name of the typedef function pointer:
            matched_name = re.match( r'^ *\( *\* *([A-Za-z0-9_]*)', matched.group(2) )
            if matched_name:
                function_pointer['name'] = matched_name.group(1).strip()
            else:
                exit_on_error( "ERROR: Failed to parse the function pointer string [",f_ptr_str,"]" )
            # Extract the parameters of the function pointer:
            function_pointer['parameters'] = ''
            brace_open_count = 0
            i=0
            while i < len( matched.group(3).strip() ):
                # NOTE: This code assumes that the first char will be a '('
                if matched.group(3)[i] == '(':
                    brace_open_count += 1
                elif matched.group(3)[i] == ')':
                    brace_open_count -= 1
                if brace_open_count == 0:
                    function_pointer['parameters'] = matched.group(3)[1:i].strip()
                    break
                i+=1
        else:
            function_pointer = None
        return function_pointer


    def __parse_function_parameter( self, parameter ):
        param = parameter.strip()
        # If the param is void, it means there are no parameters, so ensure
        # nothing is returned from this function.
        retval = None
        if not param == 'void':
            arg = {}
            arg_split = param.split(' ')
            if len( arg_split ) == 1:
                # A parameter where only the type has been specified, so generate
                # a name for the parameter
                arg['type'] = arg_split[0].strip()
                arg['name'] = 'arg_' + arg['type'] + '_' + chr(ord('a') + self.auto_gen_id )
                self.auto_gen_id += 1
                retval = arg
            else:
                # A parameter where type and name has been specified, the param
                # name is always the last item in the split string, i.e.
                # arg_split = [ "unsigned", "int", "my_param" ]
                arg_name = arg_split[len(arg_split)-1].strip()
                ptr_suffix = ''
                ptr_depth = 0
                if ( arg_name.startswith( '*' ) ):
                    ptr_depth = arg_name.count( '*' )
                    for x in range(0, ptr_depth):
                        ptr_suffix += '*'
                i=0
                arg_type = ''
                # Ignore const(ness) when parsing parameters:
                while ( i < len(arg_split)-1 ):
                    arg_type += arg_split[i] + ' '
                    i+=1
                # Move any * chars from the start of the parameter name and
                # append them to the parameter data type
                arg['type'] = arg_type.strip() + ptr_suffix
                arg['name'] = re.sub( '[*]', '', arg_name )
                retval = arg
        return retval

    # Look at the parameter and make a decision as to what sort of parameter it is:
    # If the parameter is a pointer and it's name takes the form "out_<name>",
    # it is considered an output pointer. Otherwise it is considered to be
    # an input pointer.
    # TODO : THESE SEARCHES ARE FAR TOO GENERAL, THEY NEED TO BE IMPROVED i.e.
    # name of parameter may well be int * data_outer would be treated as an
    # output parameter - NOT GOOD!
    def __get_parameter_type( self, parameter ):
        if re.search( '\(', parameter ):
            param_type = ParameterType.PARAMETER_FUNCTION_POINTER
        elif re.search( 'callback', parameter ):
            param_type = ParameterType.PARAMETER_CALLBACK
        # TODO : How should the mock handle pointer to pointer parameters?
        elif re.search( '\*', parameter ):
            if re.search( 'out_', parameter ):
                param_type = ParameterType.PARAMETER_OUT_POINTER
            else:
                param_type = ParameterType.PARAMETER_IN_POINTER
        elif re.search( r'.*(\.\.\.)|(va_list)', parameter ):
            param_type = ParameterType.PARAMETER_VA_LIST
        else:
            param_type = ParameterType.PARAMETER_VALUE
        return param_type


    # Parse the string representation of a parameter, extracting the name
    # and data type of the parameter and finding out the type of parameter,
    # refer to class Parameter(Enum) for parameter types.
    def __parse_parameter( self, parameter, pre_parsed_header, pre_parsed_included_headers ):
        parsed_parameter = True
        retval = None
        check_p_type = self.__get_parameter_type( parameter )
        if check_p_type == ParameterType.PARAMETER_FUNCTION_POINTER:
            p_type = check_p_type
            p_name = self.__parse_function_pointer_string( parameter )['name']
            p_data_type = parameter
        elif check_p_type == ParameterType.PARAMETER_VA_LIST:
            # Note: Parameter name is set to 'variable_list' so a mock API will be generated to allow unittest to ignore the va_list argument
            p_type = check_p_type
            p_name = 'variable_list'
            p_data_type = '...'
        else:
            parsed_param = self.__parse_function_parameter( parameter )
            if parsed_param:
                p_type = check_p_type
                p_name = re.sub(' +',' ', parsed_param['name'] )
                p_data_type = re.sub(' +',' ', parsed_param['type'] )
            else:
                parsed_parameter = False
        if parsed_parameter:
            retval = Parameter( p_type, p_data_type, p_name )
        return retval


    # Parse the parameter list into a list of Parameter objects
    # TODO : It seems pre_parsed_header AND pre_parsed_included_headers are not actually being used, so remove them from this API
    def __parse_function_parameter_list( self, function_name, function_parameters, pre_parsed_header, pre_parsed_included_headers ):
        parameter_list = []
        if function_parameters.strip():
            parameter_string = function_parameters
            while parameter_string:
                result = self.__get_next_parameter_from_parameter_string( parameter_string )
                parameter_string = result['remainder']
                if result['parameter']:
                    if result['parameter'].strip() != "void":
                        p_instance = self.__parse_parameter( result['parameter'], pre_parsed_header, pre_parsed_included_headers )
                        if p_instance:
                            parameter_list.append( p_instance )
                        else:
                            exit_on_error( "ERROR parsing parameter[", result['parameter'], "] for function[", function_name ,"]"  )
                else:
                    exit_on_error( "ERROR parsing function definition: ", function_name, "(", function_parameters, ");" )
        return parameter_list

