import pytest

# Test basics
def func(x):
    return x + 1

def test_answer():
    """
    This test should fail.
    """
    assert func(3) == 5
    
def test_answer_2():
    """
    This test should pass.
    """
    assert func(5) == 6
    
# Test that a certain exception is raised.
def f_test_exception():
    raise SystemExit(1)

def test_raiseexception():
    with pytest.raises(SystemExit):
        f_test_exception()
        
# Group multiple tests in a class
class TestClass:
    def test_one(self):
        x = "this"
        assert "h" in x
        
    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")

# Compare floating point values
def test_sum():
    assert (0.1 + 0.2) == pytest.approx(0.3)
    
# Request a temp directory - what happens without fixture setup?
def test_needsfiles(tmp_path):
    """This function uses the `tmp_path` argument, which is created by Pytest per test invocation.

    Args:
        tmp_path (_type_): _description_
    """
    print(tmp_path)
    assert 0