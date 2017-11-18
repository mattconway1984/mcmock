/**
 * @file mcmock.c
 *
 * @brief Contains the mcmock implementation.
 *
 * Copyright (C) Espial Limited 2017 Company Confidential - All Rights Reserved
 */


#include <mcmock.h>

#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdbool.h>

#define MCMOCK_PRINT_BUFFER_SIZE 3000

typedef struct
{
    const char * api_name;
    void * expected_conditions;

} mcmock_expectation_data_t;


typedef struct mcmock_expectation
{
    mcmock_expectation_data_t * data;
    struct mcmock_expectation * next;

} mcmock_expectation_t;


static mcmock_expectation_t *mcmock_expectations = NULL;
static mcmock_test_assert assertion_callback = NULL;


void mcmock_initialise( mcmock_test_assert callback )
{
    if ( mcmock_expectations != NULL )
    {
        mcmock_assert_msg( true, "\nTest error: Cannot re-initialise mcmock" );
    }
    assertion_callback = callback;
}


void mcmock_register_expectation( void * conditions, const char * api_name )
{
    mcmock_expectation_data_t * data = malloc( sizeof( mcmock_expectation_data_t ) );
    data->api_name = api_name;
    data->expected_conditions = conditions;

    if ( mcmock_expectations != NULL )
    {
        mcmock_expectation_t * current = mcmock_expectations;
        while ( current->next != NULL )
        {
            current = current->next;
        }
        current->next = malloc( sizeof( mcmock_expectation_t ) );
        current->next->data = data;
        current->next->next = NULL;
    }
    else
    {
        mcmock_expectations = malloc( sizeof( mcmock_expectation_t ) );
        mcmock_expectations->data = data;
        mcmock_expectations->next = NULL;
    }
}


void * mcmock_peek_latest_expectation( void )
{
    mcmock_expectation_t * current = mcmock_expectations;
    if ( current != NULL )
    {
        while ( current->next != NULL )
        {
            current = current->next;
        }
    }
    return current->data->expected_conditions;
}


void * mcmock_get_next_expectation( void )
{
    void * expectation = NULL;
    if ( mcmock_expectations != NULL )
    {
        expectation = mcmock_expectations->data->expected_conditions;
        mcmock_expectation_t * next_expectation = NULL;
        if ( mcmock_expectations->next )
        {
            next_expectation = mcmock_expectations->next;
        }
        free( mcmock_expectations->data );
        free( mcmock_expectations );
        mcmock_expectations = next_expectation;
    }
    return expectation;
}


void mcmock_verify( void )
{
    if ( mcmock_expectations != NULL )
    {
        char buf[ MCMOCK_PRINT_BUFFER_SIZE ];
        int i=0, len=0;
        while ( mcmock_expectations != NULL )
        {
            len += snprintf(
                        buf+len,
                        sizeof( buf ),
                        " %d. %s()\n",
                        ++i,
                        mcmock_expectations->data->api_name );
            mcmock_expectations = mcmock_expectations->next;
        }
        mcmock_assert_msg(
            true,
            "\nThere are %d unfulfilled expectations. The ordered list of unfilled expectations is:\n%s",
            i,
            buf );
    }
}


void mcmock_assert_msg( bool assert, const char * fmt, ... )
{
    if ( assert )
    {
        char buf[MCMOCK_PRINT_BUFFER_SIZE];
        va_list args;
        va_start( args, fmt );
        vsnprintf( buf, sizeof( buf ), fmt, args );
        va_end( args );
        assertion_callback( buf );
    }
}
