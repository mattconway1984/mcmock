
import pathlib
import pytest


from mcmock.mcmock import McMock


_ABC_PATH = pathlib.Path("samples/abc")


def test_foo():
    abc = _ABC_PATH.joinpath("abc.h")
    output = pathlib.Path("tmp")
    inst = McMock([abc], output_path=output, include_paths=[_ABC_PATH])
    inst.generate()
    for mock in inst.mocks:
        print(f"mock: {mock}")
