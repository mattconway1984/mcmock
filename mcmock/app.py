import argparse

def parse_command_args():
    """
    Parse command line args passed to the mcmock application.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        "-s",
        nargs="*",
        help="Path(s) to the source files; directories containing C header files to be mocked.",
        required=True)
    return parser.parse_args()


def main():
    """
    Main entry point for the mcmock application.
    """

    args = parse_command_args()
    print(args)
