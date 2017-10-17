#!/usr/bin/python
# @file mcmock_utils.py
# @author mconway@Espial.com
# @description Utility functions used by mcmock mock generation scripts
# Copyright (C) Espial Limited 2017 Company Confidential - All Rights Reserved


from __future__ import print_function
import sys
from mcmock_types import Parameter, ParameterType


def mcmock_utils_convert_params_list_to_string( parameters ):
    parameter_string = ' '
    i=0
    if len(parameters) == 0:
        parameter_string = ' void '
    else:
        while i<len( parameters ):
            if parameters[i].type() == ParameterType.PARAMETER_FUNCTION_POINTER:
                parameter_string += parameters[i].data_type()
            elif parameters[i].type() == ParameterType.PARAMETER_VA_LIST:
                parameter_string += parameters[i].data_type()
            else:
                parameter_string += parameters[i].data_type() + ' ' + parameters[i].name()
            i+=1
            if ( i < len( parameters ) ):
                parameter_string += ', '
            else:
                parameter_string += ' '
    return parameter_string


# Function to strip the constness of a variable; this will ensure we can store
# things like constant pointers
def mcmock_utils_strip_constness( variable_data_type ):
    result = variable_data_type
    vdt_split = variable_data_type.split( ' ' )
    if ( vdt_split[-1] == "const" ):
        result = " ".join( vdt_split[0:-1] )
    return result


# Function to print to stderr and terminate
def exit_on_error( *args, **kwargs ):
    print("mCmock:",*args, file=sys.stderr, **kwargs)
    sys.exit( 1 )


# Function to print to stderr
def eprint(*args, **kwargs):
    print("mCmock:",*args, file=sys.stderr, **kwargs)


# Function to print to stdout
def sprint(*args, **kwargs):
    print("mCmock:",*args, file=sys.stdout, **kwargs)
