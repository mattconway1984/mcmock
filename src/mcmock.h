/**
 * @file mcmock.h
 *
 * @brief The mcmock implementation, this is the central module for mcmock
 * where mock implementations can register and unregister themselves. As well as
 * allowing mocks to register test expectations so the order of the calls made
 * by the code under test can be verified to be correct.
 *
 * Copyright (C) Espial Limited 2017 Company Confidential - All Rights Reserved
 */

#ifndef INCLUDE_MCMOCK_H
#define INCLUDE_MCMOCK_H


#include <stdarg.h>
#include <stdbool.h>


#ifdef __cplusplus
extern "C" {
#endif


/**
 * @brief Function pointer definition for a test failure callback
 */
typedef void ( *mcmock_test_assert )( const char * message );


/**
 * @brief Initialise the mcmock library
 *
 * Call this API once per test suite to initialise the mcmock library. If this
 * API is not called, auto-generated mocks will not work as expected.
 *
 * @param callback: Register a callback function that will be invoked if mcmock
 * has encounted a test failure. The callback will be invoked with a relavent
 * failure message which can be displayed to the user.
 */
extern void mcmock_initialise( mcmock_test_assert callback );


/**
 * @brief Register an expectation
 *
 * This API should only ever be used by the auto-generated mocks. It is used so
 * that a mock can register an expectation with mcmock
 * @note The order in which expectations are registered is important.
 */
extern void mcmock_register_expectation( void * conditions, const char * api_name );


/**
 * @brief Get the latest expectation without removing it from the list
 *
 * This API should only ever be used by the auto-generated mocks. It is used to
 * take a peek at the latest expecation that was registered.
 */
extern void * mcmock_peek_latest_expectation( void );


/**
 * @brief Get the next expecation
 *
 * This API should only ever be used by the auto-generated mocks. It is used to
 * get the latest registered expectation.
 */
extern void * mcmock_get_next_expectation( void );


/**
 * @brief Verify all expectations have been satisfied
 *
 * This API should be called once per test run, the full list of registered
 * expectations should be emptied as the test runs, if the full list is not
 * emptied, it's considered a test failure as there are unsatisifed
 * expectations.
 * @note Calling this API when there are unsatisfied expectations will cause
 * mcmock to automatically clean these, free'ing any allocated memory used to
 * store the expectation.
 */
extern void mcmock_verify( void );


/**
 * @brief Assert the unit test on a genuine unit test failure
 *
 * This API should only ever be used by the auto-generated mocks. It is used to
 * assert the unit test, assert should never be called inside an auto-generated
 * mock otherwise memory leaks will occur.
 */
extern void mcmock_assert_msg( bool condition, const char * expr, ... );


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_MCMOCK_H */

