#!/usr/bin/env python

import argparse
import os
import textwrap

import mcmock
from mcmock.generate_mock import GenerateMock


_DESCRIPTION="""mcmock
======

A tool to auto-generate mocks for C headers:

To mock a header file, output to current working directory:
    mcmock header_to_mock.h

To mock several header files, specifying an output directory:
    mcmock -o /tmp/mocks/ -m header_one.h header_two.h

To mock headers which depend on external datastructures:
    mcmock -o /tmp/mocks/ -i /usr/include  my_project/include -m header_one.h header_two.h

======
"""


def _parse_command_args():
    """
    Parse command line args passed to the mcmock application.
    """

    parser = \
        argparse.ArgumentParser(
            description=textwrap.dedent(_DESCRIPTION),
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-v",
        action="version",
        version=f"{mcmock.__version__}")
    parser.add_argument(
        "--output",
        "-o",
        help="Path of output directory; where the generated mocks will be written.",
        default=os.getcwd())
    parser.add_argument(
        "--include",
        "-i",
        nargs="*",
        help="Path(s) to depended include files; directories containing header files.")
    parser.add_argument(
        "--mock",
        "-m",
        nargs="*",
        help="Paths to header files to be mocked.",
        required=True)
    return parser.parse_args()


def main():
    """
    Main entry point for the mcmock application.
    """
    args = _parse_command_args()


def generate_mocks( command_data ):
    for header in command_data.get_headers_to_mock():
        sprint( "Generating Mock for %s"%( header ) )
        mock_generator = \
            GenerateMock( \
                command_data.get_root_include_directory(), \
                command_data.get_output_directory(), \
                header, \
                command_data.get_additional_includes() )


if __name__ == "__main__":
    main()
