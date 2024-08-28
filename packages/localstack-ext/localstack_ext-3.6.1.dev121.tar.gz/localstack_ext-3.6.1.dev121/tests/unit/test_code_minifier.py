import pytest


@pytest.mark.parametrize("decorator", ["dataclasses.dataclass", "dataclass"])
@pytest.mark.parametrize("brackets", ["", "()", "(frozen=True)"])
def test_dataclasses_types(decorator, brackets):
    python_minifier = patch_pyminifier()

    code = f"""
from dataclasses import dataclass
import dataclasses.dataclass
@{decorator + brackets}
class A:
    arg1: str
    arg2: str = ""
    arg3: int = 1
    """

    result = python_minifier.minify(code)
    assert "arg1:str" in result
    assert "arg2:str=''" in result
    assert "arg3:int=1" in result


def test_code_minifier():
    python_minifier = patch_pyminifier()

    code = """
from typing import Optional, TypedDict
class A(TypedDict):
    arg1: str
class B(A):
    arg2: Optional[int]
FancyType = Optional[int]
class C(B):
    arg3: Optional[str]
    arg4: FancyType
    """

    result = python_minifier.minify(code)
    assert "arg2:Optional[int]" in result
    assert "arg3:Optional[str]" in result
    assert "arg4:FancyType" in result

    # assert that the code can be run by the interpreter
    globals = {}
    exec(result, globals)
    for clazz in ["A", "B", "C"]:
        assert isinstance(globals.get(clazz), type)


def patch_pyminifier():
    try:
        import python_minifier
        from localstack.pro.core.internal.obfuscate import apply_python_minifier_patches

        apply_python_minifier_patches()

        return python_minifier
    except Exception:
        return pytest.skip("skipping test as python-minifier or internal package are not available")
