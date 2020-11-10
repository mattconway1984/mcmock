from mcmock.parse_command import ParseCommand
from mcmock.generate_mock import GenerateMock
from mcmock.mcmock_utils import sprint, eprint, exit_on_error


def generate_mocks( command_data ):
    for header in command_data.get_headers_to_mock():
        sprint( "Generating Mock for %s"%( header ) )
        mock_generator = \
            GenerateMock( \
                command_data.get_root_include_directory(), \
                command_data.get_output_directory(), \
                header, \
                command_data.get_additional_includes() )


def run_from_cmd_line(args):
    command_data = ParseCommand(args)
    if command_data.get_command_errors():
        exit_on_error( command_data.get_command_errors() )
    elif not command_data.get_headers_to_mock():
        exit_on_error( command_data.get_help_message() )
    elif command_data.show_help_message():
        sprint( command_data.get_help_message() )
    else:
        generate_mocks( command_data )


def main(*args):
    """
    Main entry point for the mcmock application.
    """
    run_from_cmd_line(args)
