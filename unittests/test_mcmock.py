
import pathlib
import pytest


from mcmock.mcmock import McMock


_ABC_PATH = pathlib.Path("samples/abc")
_XYZ_PATH = pathlib.Path("samples/xyz")


def test_foo():
    abc = _ABC_PATH.joinpath("abc.h")
    output = pathlib.Path("tmp")
    inst = McMock([abc], output_path=output, include_paths=[_ABC_PATH])
    inst.generate()

def test_bar():
    macros = _XYZ_PATH.joinpath("macros.h")
    output = pathlib.Path("tmp")
    inst = McMock([macros], output_path=output)
    inst.generate()

