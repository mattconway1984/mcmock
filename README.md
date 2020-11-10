McMock
======

McMock is an automatic mock generation tool for C header files and is 
independent of any unit test framework. It could be, for example, used in 
conjunction with test frameworks such as unity, check, gtest etc...


Usage
=====
Once installed, mcmock should provide a command line shortcut tool so it can
be easily executed.

Sources
-------
Specifying lists of source directories. These can be listed as a single path,
for example:

    `mcmock --source my_project/include`

Or to include many sources, for example:

    `mcmock --source my_project/first/path my_project/second/path my_project/include`
