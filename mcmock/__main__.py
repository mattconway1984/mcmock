#!/usr/bin/env python

import argparse
import os
import textwrap

from mcmock.mcmock import McMock


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
        version=f"{McMock.version}")
    parser.add_argument(
        "--mock",
        "-m",
        nargs="*",
        help="Paths to header files to be mocked.",
        required=True)
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
    return parser.parse_args()


def main():
    """
    Main entry point for the mcmock application.
    """
    args = _parse_command_args()
    mcmock = McMock(args.mock, args.output, args.include)
    mcmock.generate()


if __name__ == "__main__":
    main()
