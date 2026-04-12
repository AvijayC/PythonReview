import pytest

# First, the anatomy of a test.
# Arrange: set up your mock systems, services, etc. around the test.
# Act: Execute the test on the temp context you set up
# Assert: check the results and pass/fail it
# Cleanup: make sure your tests do not interfere with this one - enforce sandboxing, and careful reuse.

# What is a fixture?
# Provides a consistent mock context for my tests. E.g. a database, etc.
# You can also use fixtures in the Act phase for more complex tests (later)

# Example pytest fixture usage
class Fruit:
    def __init__(self, name):
        self.name = name
        self.mutable_value = []
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fruit):
            return False
        return self.name == other.name
    
        
@pytest.fixture
def my_fruit():
    return Fruit("apple")

@pytest.fixture
def fruit_basket(my_fruit):
    my_fruit.mutable_value.append('from fruit_basket')
    return [Fruit("banana"), my_fruit]

def test_my_fruit_in_basket(my_fruit, fruit_basket):
    my_fruit.mutable_value.append('from test_my_fruit_in_basket')
    print(f"Mutable value in test: {my_fruit.mutable_value}")
    assert my_fruit not in fruit_basket
    
