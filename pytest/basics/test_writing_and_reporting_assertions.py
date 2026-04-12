import pytest

# Basic assertion test
def f():
    return 3

def test_function():
    assert f() == 4
    
def test_function_with_message():
    assert f() == 4, "Here is an example assert message"
    
# Check that a specific exception is raised, with message regex matching
def f2():
    raise ValueError("Exception 123 raised")

def test_exception():
    with pytest.raises(ValueError, match=r".* 123 .*"):
        f2()
        
# Rich support for context sensitive comparisons
def test_set_comparison():
    set1 = set("1308")
    set2 = set("8035")
    assert set1 == set2
    
