/* Define an abc integer type */
typedef int abc_int_t;

/* Define a boolean (could just use stdbool, but this is more fun) */
typedef enum 
{
    ABC_FALSE,
    ABC_TRUE
} abc_bool_t;

/**
 * Callback function type "abc_message_handler_t"
 *
 * @param id The id of the message to handle
 *
 * @return ABC_TRUE if message was handled, ABC_FALSE otherwise
 */
typedef abc_bool_t (*abc_message_handler_t)(abc_int_t id);
