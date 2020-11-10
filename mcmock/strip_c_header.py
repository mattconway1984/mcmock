#!/usr/bin/python
# @file strip_c_header.py
# @author matthew.denis.conway@gmail.com
# @description Strip out any content inside the header file that is contained
# inside "undefined" pre-processor conditional blocks
# Copyright (C) Espial Limited 2017 Company Confidential - All Rights Reserved


import re
from mcmock.mcmock_utils import *


class StripCHeader:


    _protected_block_starters = ['#if ','#ifdef','#ifndef', '#elif']



    # Public API to get the stripped file content
    def get_stripped_data( self ):
        return self._stripped_data


    #
    # PRIVATE IMPLEMENTATION
    #
    def __init__( self, pre_parsed_header, pre_parsed_included_headers ):
        self._stripped_data = list( pre_parsed_header.get_unparsed_content() )
        self.__strip_file_data_protected_by_undefined_symbols( pre_parsed_header, pre_parsed_included_headers )
        self.__strip_variables()
        self.__concatenate_multi_split_lines()
        self.__strip_leftover_defined_symbols()


    def __strip_file_data_protected_by_undefined_symbols( self, pre_parsed_header, pre_parsed_included_headers ):
        do_stripping = self.__more_stripping_required( self._stripped_data )
        if do_stripping:
            self.__strip_data_protected_by_undefined_conditionals( pre_parsed_header, pre_parsed_included_headers )


    def __strip_data_protected_by_undefined_conditionals( self, pre_parsed_header, pre_parsed_included_headers ):
        do_more_stripping = True
        working_copy = []
        while ( do_more_stripping ):
            i = 0
            while ( i < len( self._stripped_data ) ):
                line = self._stripped_data[i]
                start_of_protected_block = False
                for start_protector in self._protected_block_starters:
                    if ( re.search( start_protector, line ) ):
                        start_of_protected_block = True
                if start_of_protected_block:
                    result = self.__process_protected_block( pre_parsed_header, pre_parsed_included_headers, self._stripped_data, i )
                    if result['include_block']:
                        i = result['start_block'] + 1
                        while ( i < result['include_end'] ):
                            working_copy.append( self._stripped_data[i] )
                            i+=1
                        i = result['end_block']
                    else:
                        i = result['end_block']
                else:
                    working_copy.append( line )
                i+=1
            self._stripped_data = list( working_copy )
            do_more_stripping = self.__more_stripping_required( working_copy )
            if do_more_stripping:
                working_copy = []


    def __more_stripping_required( self, working_copy ):
        do_stripping = False
        for line in working_copy:
            for start_protector in self._protected_block_starters:
                if ( re.search( start_protector, line ) ):
                    do_stripping = True
                    break
        return do_stripping


    def __process_protected_block( self, pre_parsed_header, pre_parsed_included_headers, lines, start_block ):
        result = {}
        conditional_symbols = self.__get_conditional_symbol( lines[start_block] )
        if not conditional_symbols:
            exit_on_error( "ERROR: Failed to parse the conditional statement:\n    %s\n"%(lines[start_block]) )
        end_block = self.__find_end_of_protected_block( lines, start_block )
        if self.__include_the_protected_block( start_block, end_block, lines, conditional_symbols, pre_parsed_header, pre_parsed_included_headers ):
            result = self.__search_for_true_end_of_protected_block( start_block, end_block, lines )
        else:
            result = self.__search_protected_block_for_other_conditionals( start_block, end_block, lines )
        return result


    def __search_protected_block_for_other_conditionals( self, start_block, end_block, lines ):
        result = {}
        result['include_block'] = False
        result['end_block'] = end_block
        result['include_end'] = end_block
        result['start_block'] = start_block
        i = start_block + 1
        sub_block_count = 0
        while ( i < end_block ):
            if re.search( '#ifdef|#ifndef|#if ', lines[i] ):
                sub_block_count += 1
            if ( sub_block_count > 0 ):
                if re.search( '#endif', lines[i] ):
                    sub_block_count -= 1
            else:
                if re.search( '#elif', lines[i] ):
                    # restart parsing, starting at the #elif
                    result['end_block'] = i-1
                    break
                if re.search( '#else', lines[i] ):
                    result['include_block'] = True
                    result['start_block'] = i
                    break
            i+=1
        return result


    def __find_end_of_protected_block( self, lines, block_start_idx ):
        sub_block_starts = ['#ifndef','#if ', '#ifdef']
        block_depth = 0
        i = block_start_idx + 1
        result = block_start_idx
        while( i < len( lines ) ):
            line = lines[i]
            for sub_block_start in sub_block_starts:
                if re.match( sub_block_start, line):
                    block_depth += 1
            if re.match( '#endif', line):
                if ( block_depth == 0 ):
                    result = i
                else:
                    block_depth -= 1
            i += 1
        return result


    def __include_the_protected_block( self, start_block, end_block, lines, conditional_symbols, pre_parsed_header, pre_parsed_included_headers):
        include_protected_block = False
        for conditional in conditional_symbols:
            symbol_is_defined = False
            symbol_data = pre_parsed_header.lookup_defined_symbol( conditional['name'] )
            if symbol_data:
                symbol_is_defined = True
            else:
                for header in pre_parsed_included_headers:
                    symbol_data = header.lookup_defined_symbol( conditional['name'] )
                    if symbol_data:
                        symbol_is_defined = True
                        break;
            decision = False
            if conditional['positive_protector'] and symbol_is_defined:
                decision = True
            elif not conditional['positive_protector'] and not symbol_is_defined:
                decision = True
            elif not conditional['positive_protector'] and symbol_is_defined:
                result = self.__search_for_true_end_of_protected_block( start_block, end_block, lines )
                decision = self.__is_symbol_defined_inside_block( lines, start_block, result['end_block'], conditional['name'] )
            if conditional['action'] == '':
                include_protected_block = decision
            elif conditional['action'] == '&&':
                include_protected_block = decision and include_protected_block
            elif conditional['action'] == '||':
                include_protected_block = decision or include_protected_block
        return include_protected_block


    def __search_for_true_end_of_protected_block( self, block_start, block_end, lines ):
        result = {}
        result['include_block'] = True
        result['start_block'] = block_start
        result['end_block'] = block_end
        result['include_end'] = block_end
        i = block_start + 1
        sub_block_starts = ['#ifndef','#if ', '#ifdef']
        sub_block_depth = 0
        while ( i < block_end ):
            for sub_block_start in sub_block_starts:
                if re.match( sub_block_start, lines[i] ):
                    sub_block_depth += 1
            if ( sub_block_depth > 0 ):
                if re.match( '#endif', lines[i] ):
                    sub_block_depth -= 1
            elif re.search( '#else', lines[i] ) or re.search( '#elif', lines[i] ):
                result['include_end'] = i
                break
            i+=1
        return result;


    def __is_symbol_defined_inside_block( self, lines, start_block, end_block, check_symbol ):
        regexp = r'#define +(' + re.escape(check_symbol) + r')'
        result = False
        i = start_block
        while( i < end_block ):
            line = lines[i]
            matched = re.match( regexp, line)
            if ( matched ):
                result = True
            i += 1
        return result


    def __extract_defined_symbol( self, line ):
        defined_symbol = {}
        defined_symbol['action'] = ''
        matched = re.match( r'((?:#ifdef|#ifndef)|(?:#if *|#elif)) *(defined|!defined)* *\(* *([A-Za-z0-9_]+)', line)
        defined_symbol['name'] = matched.group(3).strip()
        if matched.group(2):
            if re.match( r'!defined', matched.group(2) ):
                defined_symbol['positive_protector'] = False
            elif re.match( r'defined', matched.group(2) ):
                defined_symbol['positive_protector'] = True
            else:
                exit_on_error( "Failed to parse the line %s"%(line) )
        else:
            if re.match( r'#ifndef', matched.group(1) ):
                defined_symbol['positive_protector'] = False
            elif re.match( r'#ifdef', matched.group(1) ):
                defined_symbol['positive_protector'] = True
            elif re.match( r'#if ',matched.group(1) ):
                new_matched = re.match( r'#if +(.+)', line )
                if new_matched:
                    defined_symbol['name'] = new_matched.group(1).strip()
                    defined_symbol['positive_protector'] = True
                    try:
                        symbol_text = defined_symbol['name'].replace('(','').replace(')','').strip()
                        int( symbol_text )
                        if symbol_text == '0':
                            # Change the symbol name from #if 0 to something creative
                            # that's not likely to be defined anywhere so the stuff
                            # its protecting is ignored when mocking!
                            defined_symbol['name'] = "XYZ_DO_NOT_INCLUDE_CODE_PROTECTED_IN_THIS_BLOCK_ZYX"
                    except ValueError:
                        exit_on_error("Error parsing defined symbol: ", line)
                else:
                    exit_on_error("Error parsing defined symbol: ", line)

            else:
                exit_on_error( "Failed to parse the line %s"%(line) )
        return defined_symbol


    def __parse_multistatement_condition( self, condition ):
        conditional = {}
        matched = re.match( r'(#if|\|\|.*|&&|#elif)(.*)defined *\(* *([A-Za-z0-9_]+) *[$|\)*]' , condition )
        if matched:
            if ( matched.group(1).strip() == '||' ):
                conditional['action'] = '||'
            elif ( matched.group(1).strip() == '&&' ):
                conditional['action'] = '&&'
            else:
                conditional['action'] = ''

            if ( matched.group(2).strip() == '!' ):
                conditional['positive_protector'] = False
            else:
                conditional['positive_protector'] = True
            conditional['name'] = matched.group(3)
        return conditional


    def __split_complex_statement( self, line ):
        temp_pos = 0
        multi_symbols = []
        for match in re.finditer('(&&)|(\|\|)', line ):
            multi_symbols.append( line[temp_pos:match.start() ] )
            temp_pos = match.start()
        multi_symbols.append( line[temp_pos:len(line) ] )
        return multi_symbols


    def __get_conditional_symbol( self, line ):
        conditional_symbols = []
        conditional = {}
        if re.findall('(&&)|(\|\|)', line ):
            multi_symbols = self.__split_complex_statement( line )
            for conditional_symbol in multi_symbols:
                conditional = self.__parse_multistatement_condition( conditional_symbol )
                conditional_symbols.append( conditional )
        else:
            conditional_symbol = self.__extract_defined_symbol( line )
            conditional_symbols.append( conditional_symbol )
        if not conditional_symbols:
            raise Exception( "\nFailed to parse the conditional statement:\n    %s\n"%(lines[start_block]) )
        return conditional_symbols


    def __strip_variables( self ):
        working_copy = []
        for line in self._stripped_data:
            matched = re.match( r'struct +([A-Za-z0-9]+)(;)', line)
            if not matched:
                working_copy.append(line);
        self._stripped_data = list( working_copy )


    def __concatenate_multi_split_lines( self ):
        working_copy = []
        concatenated_line = ''
        for line in self._stripped_data:
            matched = re.match( r'(.*)\\', line.strip() )
            if ( matched ):
                concatenated_line += matched.group(1)
            else:
                if ( concatenated_line != '' ):
                    concatenated_line += line.strip()
                    working_copy.append( concatenated_line )
                    concatenated_line = ''
                else:
                    working_copy.append( line.strip() )
        self._stripped_data = list( working_copy )


    def __strip_leftover_defined_symbols( self ):
        working_copy = []
        for line in self._stripped_data:
            if not line.strip().startswith( '#define' ):
                working_copy.append( line )
        self._stripped_data = list( working_copy )

