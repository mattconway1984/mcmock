#!/usr/bin/python
# @file parse_c_header.py
# @author matthew.denis.conway@gmail.com
# @description Parse a C header file, creating logical python data structures
# for the definitions in the C header.


import re

from mcmock.mcmock_types import ParameterType, Parameter, Function, TypedefType, Typedef, DefinedSymbol
from mcmock.mcmock_utils import *


class PreParseCHeader:
    """
    Represents a pre-parsed header file.

    Args:
        filename (pathlib.Path): path to the pre-parsed header.
    """

    def get_filename( self ):
        return self.filename


    @property
    def included_application_headers( self ):
        """
        list[str]: Names of included application headers.

        This list represents all the includes that exist in the header file
        that has been parsed, for example:

            #include "my_api.h"
            #include "sub/another_api.h"

        would be returned as:

            ["my_api.h", "sub/another_api.h"]
        """
        return self._included_application_headers


    # API to get a list of included system and/or library headers
    def get_included_system_header_list( self ):
        return self.included_system_headers


    def lookup_defined_symbol( self, lookup ):
        result = None
        for sym in self.defined_symbols:
            if ( sym.name() == lookup ):
                result = sym
                break
        return result


    # API to get a list of all typedefs defined within the header file, this
    # is currently a simple list of strings with one entry for each typedef.
    def get_typedefs( self ):
        return self.typedefs


    # API to get the file contents which have not yet been parsed
    def get_unparsed_content( self ):
        return self.unparsed_content


    # API to get ALL the defined symbols that were extracted from the header
    # file during pre-parsing
    def get_defined_symbols( self ):
        return self.defined_symbols



    def __init__(self, header_file):
        self._header_file = header_file
        self._included_application_headers = []
        self.included_system_headers = []
        self.defined_symbols = []
        self.typedefs = []
        with self._header_file.open("r") as handle:
            header_data = handle.readlines()
        header_data = self._strip_comments(header_data)
        header_data = self._strip_whitespace(header_data)
        working_copy = list( header_data )
        working_copy = list( self.__parse_defined_symbols( working_copy ) )
        working_copy = list( self.__parse_included_headers( working_copy ) )
        working_copy = list( self.__split_multi_statement_lines( working_copy ) )
        working_copy = list( self.__parse_typedefs( working_copy ) )
        self.unparsed_content = working_copy

    @staticmethod
    def _strip_comments(lines):
        """
        Strip C/C++ comments from the source file (lines).
        """
        return \
            re.sub(
                r"\/\*(.|[\r\n])+?\*\/|//.*",
                "",
                "".join(lines)).splitlines()

    @staticmethod
    def _strip_whitespace(lines):
        stripped = []
        for line in lines:
            if line:
                stripped.append(line.strip())
        return stripped

    def __split_multi_statement_lines( self, unparsed_data ):
        expanded = []
        for line in unparsed_data:
            line = line.strip()
            open_brace_count = 0
            line_to_add = ''
            x=0
            for x in range(0, len(line)):
                c = line[x]
                line_to_add += c
                if c == '{':
                    open_brace_count += 1
                elif c == '}':
                    open_brace_count -= 1
                if ( open_brace_count <= 0 ) and ( c == ';') and ( len( line ) > ( x + 1 ) ):
                    expanded.append( line_to_add.strip() )
                    line_to_add = ''
                x+=1
            expanded.append( line_to_add.strip() )
        return expanded


    def __parse_defined_symbols( self, stripped_content ):
        working_copy = []
        multiline_string = ''
        parsed_multiline = False
        for line in stripped_content:
            line = line.strip()
            if multiline_string != '':
                if line.endswith('\\'):
                    multiline_string += line[0:-1]
                else:
                    # Add a whitespace char at the end of the line to ensure correct
                    # concatenation of defines spread over multiple lines
                    multiline_string += line + ' '
                    matched = re.match( r'#define +([A-Za-z0-9_]+)(.*)', multiline_string)
                    if matched:
                        self.defined_symbols.append( DefinedSymbol( matched.group(1), matched.group(2).strip() ) )
                    else:
                        eprint( "WARNING: Failed to parse the multi-line #define: ", multiline_string )
                    parsed_multiline = True
            else:
                matched = re.match( r'#define +([A-Za-z0-9_]+)(.*)', line)
                if matched:
                    if matched.group(2).strip().endswith('\\'):
                        multiline_string = line[0:-1]
                    else:
                        self.defined_symbols.append( DefinedSymbol( matched.group(1), matched.group(2).strip() ) )
            if multiline_string == '':
                working_copy.append( line )
            elif parsed_multiline:
                working_copy.append( multiline_string )
                multiline_string = ''
                parsed_multiline = False
        return working_copy


    def __parse_included_headers( self, stripped_content ):
        working_copy = []
        for line in stripped_content:
            matched = re.match( r'#include +"([\/\.A-Za-z0-9_-]+)*"', line)
            if ( matched ):
                self._included_application_headers.append( matched.group(1) )
            else:
                matched = re.match( r'#include +<([\/\.A-Za-z0-9_-]+)*>', line)
                if matched:
                    self.included_system_headers.append( matched.group(1) )
                else:
                    working_copy.append( line )
        return working_copy


    def __get_typedef_type( self, typedef_string ):
        typedef_type = TypedefType.TYPEDEF_UNKNOWN
        if re.search( r'typedef +struct', typedef_string ):
            typedef_type = TypedefType.TYPEDEF_STRUCT
        elif re.search( r'typedef +enum', typedef_string ):
            typedef_type = TypedefType.TYPEDEF_ENUM
        elif re.search( r'typedef +.+ +\( *.+\) *\(.+\)', typedef_string ):
            typedef_type = TypedefType.TYPEDEF_CALLBACK
        elif re.search ( r'typedef', typedef_string ):
            typedef_type = TypedefType.TYPEDEF_CUSTOM
        else:
            exit_on_error( "ERROR parsing typedef definition[", typedef_string, "]" )
        return typedef_type


    def __parse_typedef_struct( self, typedef_string ):
        # TODO : Parse the structure typedef
        return Typedef( TypedefType.TYPEDEF_STRUCT, "TODO: EXTRACT STRUCT TYPEDEF NAME", typedef_string )

    def __parse_typedef_enum( self, typedef_string ):
        # TODO : Parse the enum typedef
        return Typedef( TypedefType.TYPEDEF_ENUM, "TODO: EXTRACT ENUM TYPEDEF NAME", typedef_string )


    def __parse_typedef_callback( self, typedef_string ):
        # Extract the name of the function pointer definition
        matched = re.match( r'typedef +(.+?) +\( *\*(.+?) *\) *\((.+?)\)', typedef_string )
        if matched:
            return Typedef( TypedefType.TYPEDEF_CALLBACK, matched.group(2), typedef_string )
        else:
            exit_on_error( "Failed to parse the typedef [", typedef_string, "]" )


    def __parse_typedef_custom( self, typedef_string ):
        # TODO : Parse the custom typedef
        return Typedef( TypedefType.TYPEDEF_CUSTOM, "TODO: EXTRACT CUSTOM TYPEDEF NAME", typedef_string )


    def __parse_active_typedef( self, typedef_string ):
        typedef = None
        typedef_type = self.__get_typedef_type( typedef_string )
        if ( typedef_type == TypedefType.TYPEDEF_STRUCT ):
            typedef = self.__parse_typedef_struct( typedef_string )
        elif ( typedef_type == TypedefType.TYPEDEF_ENUM ):
            typedef = self.__parse_typedef_enum( typedef_string )
        elif ( typedef_type == TypedefType.TYPEDEF_CALLBACK ):
            typedef = self.__parse_typedef_callback( typedef_string )
        elif ( typedef_type == TypedefType.TYPEDEF_CUSTOM ):
            typedef = self.__parse_typedef_custom( typedef_string )
        return typedef


    def __parse_typedefs( self, stripped_content ):
        working_copy = []
        add_active_typedef = False
        active_typedef = ''
        for line in stripped_content:
            line = line.strip()
            if ( active_typedef == '' ):
                matched = re.match( r'typedef', line )
                if ( matched ):
                    # Using the guilty until proven innocent rule ;)
                    multi_line_typedef = True
                    open_brace_count = 0
                    i=0
                    for c in line:
                        active_typedef += c;
                        if c == '{':
                            open_brace_count += 1
                        elif c == '}':
                            open_brace_count -= 1
                        if ( open_brace_count == 0 ) and ( c == ';'):
                            add_active_typedef = True
                        i+=1
            else:
                for c in line:
                    active_typedef += c;
                    if c == '{':
                        open_brace_count += 1
                    elif c == '}':
                        open_brace_count -= 1
                    if ( open_brace_count == 0 ) and ( c == ';'):
                        add_active_typedef = True
            if ( active_typedef == '' ):
                working_copy.append( line )
            elif add_active_typedef:
                typedef = self.__parse_active_typedef( active_typedef )
                if typedef:
                    self.typedefs.append( typedef )
                else:
                    exit_on_error( "Failed to parse typedef definition[", active_typedef, "]" )
                add_active_typedef = False
                active_typedef = ''
        return working_copy
