/**
 * This is a sample header file used to test mcmock.
 *
 * This header file defines some APIs which some external code might like to
 * call on. However, in a unit-test environment, there's no need to rely on the
 * real abc implementation because that would mean having to rely on it being
 * available and tested and easy to add to a unit test. Therefore, mocking the
 * interface defined in this public header is a great solution to being able
 * to run your code in a predictive manner thus protecting it from silly 
 * programmer mistakes.
 *
 * This header relies on abc_types.h which defines some custom types. That
 * header file is not directly pulled in by mcmock, but it will need to be
 * parsed so that mcmock knows about the various data type definitions and how
 * to create declarations for those definitions. Not being able to do that will
 * mean mcmock is unable to work and that wouldn't be very good!
 */

#include "abc_types.h"

/**
 * A method that requires an `abc_int` and returns an `abc_int`
 *
 * @param arg Some value used by the method.
 *
 * @return an integer value.
 */
extern abc_int_t abc_method(abc_int arg);

/**
 * Method to register an abc handler
 *
 * @param handler The handler to register
 */
extern void register_handler(abc_message_handler_t handler);
