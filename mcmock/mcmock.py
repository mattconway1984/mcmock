import pathlib
import re
import string

import mcmock
from mcmock.parse_c_header import CHeaderParser
from mcmock.pre_parse_c_header import PreParseCHeader
from mcmock.strip_c_header import StripCHeader
from mcmock.build_mock_data import MockDataBuilder
from mcmock.generate_mock_source import GenerateMockSource
from mcmock.generate_mock_header import GenerateMockHeader


class Mock:
    """
    Class to represent a single generated mock.
    """

    _MOCK_FILENAME = string.Template("mock_${name}.${extension}")
    _C_EXT = "c"
    _H_EXT = "h"

    def __init__(self, header_to_mock, include_paths, output_path):
        self._header_to_mock = header_to_mock
        self._include_paths = include_paths
        self._output_path = output_path
        self.generate()

    def generate(self):
        print(f"PreParsing header: {self._header_to_mock}")
        pre_parsed_header = PreParseCHeader(self._header_to_mock)
        pre_parsed_includes = self._pre_parse_included_headers(pre_parsed_header)
        parsed_header = CHeaderParser(pre_parsed_header, pre_parsed_includes)
        mock_source, mock_header = \
            self._generate_mock_files(
                pre_parsed_header,
                parsed_header,
                pre_parsed_includes)
        self._write_mock_header(mock_header)
        self._write_mock_source(mock_source)

    @property
    def mock_source(self):
        """
        pathlib.Path: Path to the generated mock source file.
        """
        cls = type(self)
        return self._output_path.joinpath(
            cls._MOCK_FILENAME.substitute(
                name=self._header_to_mock.stem,
                extension=cls._C_EXT))

    @property
    def mock_header(self):
        """
        pathlib.Path: Path to the generated mock header file.
        """
        cls = type(self)
        return self._output_path.joinpath(
            cls._MOCK_FILENAME.substitute(
                name=self._header_to_mock.stem,
                extension=cls._H_EXT))

    def __repr__(self):
        return f"{self.mock_source} {self.mock_header}"


    def _pre_parse_included_headers(self, parsed_header):
        parsed_includes = []
        for include in parsed_header.included_application_headers:
            header_path = self._get_path_for(include)
            print(f"Pre-parsing included header: {header_path}")
            with header_path.open() as header:
                parsed_includes.append(PreParseCHeader(header_path))
        return parsed_includes

    def _get_path_for(self, header):
        # First check whether the header exists in the same directory as the
        # "header to mock". If it doesn't, check any additional paths that
        # were supplied.
        header_path = \
            pathlib.Path(self._header_to_mock.parent).joinpath(header)
        if not header_path.exists():
            for potential_path in (
                    path.joinpath(header) for path in self._include_paths):
                if potential_path.exists():
                    header_path = potential_path
                    break
            else:
                # raise IncludedHeaderNotFound("")
                raise Exception(f"Unable to find included file: {header}")
        return header_path

    def _generate_mock_files(self, pre_parsed_header, parsed_header, parsed_includes):
        mock_data_builder = MockDataBuilder(parsed_header, parsed_includes)
        mock_source = GenerateMockSource(pre_parsed_header, parsed_header, mock_data_builder, self._header_to_mock.stem, self._header_to_mock)
        mock_header = GenerateMockHeader(pre_parsed_header, mock_data_builder, self._header_to_mock.stem, self._header_to_mock)
        return mock_source, mock_header

    def _write_mock_header(self, mock_header):
        print(f"Generating mock header file: {self.mock_header}")
        with self.mock_header.open("w+") as handle:
            handle.write(
                mock_header.get_mock_header_file_contents(
                    self.mock_header.name,
                    self._header_to_mock.name))

    def _write_mock_source(self, mock_source):
        print(f"Generating mock source file: {self.mock_source}")
        with self.mock_source.open("w+") as handle:
            handle.write(
                mock_source.get_mock_source_file_contents(
                    self.mock_source.name,
                    self._header_to_mock.name))


class McMock:
    """
    Top level class for McMock application.

    Args:
        headers_to_mock (list[pathlib.Path]): List of header files to mock.
        output_path (pathlib.Path): Path where generated mocks will be written.
        include_paths (list[pathlib.Path]): List of additional include paths,
            this could be where external headers define data structure
            definitions used by any of the header files to be mocked.
    """

    _MOCK_FILENAME = string.Template("mock_${name}.${extension}")

    def __init__(self, headers_to_mock, *, output_path=None, include_paths=None):
        self._headers_to_mock = headers_to_mock
        self._output_path = output_path
        self._include_paths = include_paths
        self._mocks = []

    @property
    def version(self):
        """
        str: Version string describing McMock
        """
        return mcmock.__version__

    @property
    def mocks(self):
        """
        just for testing.
        """
        return self._mocks

    def generate(self):
        """
        Generate mocks for the defined headers to mock.
        """
        for mock in self._headers_to_mock:
            self._mocks.append(Mock(mock, self._include_paths, self._output_path))
