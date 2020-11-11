/* File with some horrible macros */

/* Seriously, I avoid doing things like this, but others don't :( */
#define NUMBERS 1, \
                2, \
                3

/* Please don't ever do this; it's horribly terrible */
#define MIN(X, Y)  ((X) < (Y) ? (X) : (Y))
#define MAX(X, Y)  ((X) > (Y) ? (X) : (Y))

/* Yes, this is a thing (lookup stringizing) */
#define WARN_IF(EXP) \
do { if (EXP) \
        fprintf (stderr, "Warning: " #EXP "\n"); } \
while (0)
