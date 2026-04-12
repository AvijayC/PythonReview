# Fixtures Quiz Log

## Quiz 1

| Field | Value |
|---|---|
| Date | 2026-03-22 |
| Source lesson file | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) |

### Question Log

| Date | Quiz | Lesson Dir | Source File | Q# | Attempt # | Prompt Summary | User Answer | Status | Feedback | Progress Notes |
|---|---|---|---|---:|---:|---|---|---|---|---|
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 1 | 1 | Same-file test requests `my_fruit` | yes | correct | Fixtures defined in the same test module are available to tests in that module. | Same-file fixture access is understood. |
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 2 | 1 | Same-file fixture requests `my_fruit` | yes | correct | Fixtures can depend on other fixtures by naming them as parameters. | Fixture-to-fixture dependency is understood. |
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 3 | 1 | Normal helper function called directly with fixture-named parameter | uncertain | not yet correct | No. Pytest only injects fixtures into pytest-managed functions such as test functions and fixture functions. A normal helper function does not get fixture injection just because it has a matching parameter name. | Main gap: why helper functions do not get auto-injection. |
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 4 | 1 | Different file test requests `my_fruit` with no import and no `conftest.py` | no | correct | Fixtures defined in a test module are not automatically shared with unrelated test modules. | Import-based sharing versus `conftest.py` sharing still needs reinforcement. |
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 5 | 1 | Move `my_fruit` into `pytest/basics/conftest.py` | yes | correct | Fixtures in `conftest.py` are available to tests in that directory and its subdirectories. | `conftest.py` directory visibility is understood. |
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 6 | 1 | Test parameter `my_fruit` meaning | mostly no, but mixed with scope reasoning | partially correct | No. Inside the test, `my_fruit` is the fixture value returned by the fixture, not the fixture function object. Pytest calls the fixture and passes the result into the test as an argument value. | Needs more practice on fixture value versus fixture function object. |
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 7 | 1 | Meaning of `my_fruit` inside dependent fixture `fruit_basket(my_fruit)` | fixture value | correct | Pytest resolves fixture dependencies before calling the dependent fixture. | Fixture dependency resolution is understood. |
| 2026-03-22 | Quiz 1 | `pytest/basics` | [test_what_are_fixtures.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/pytest/basics/test_what_are_fixtures.py) | 8 | 1 | Does every matching Python function parameter get fixture injection? | only test functions and fixture functions | mostly correct | Not every Python function. For the current learning level, treat injection as applying to test functions and fixture functions that pytest is managing. | Remaining focus: the exact boundary of pytest-managed injection. |

### Follow-Up Notes

| Note type | Details |
|---|---|
| Biggest gap | The difference between: <br>- Python function parameters <br>- pytest deciding what values to pass into pytest-managed functions |
| Module-scope meaning | A fixture name at module scope refers to the fixture definition. |
| Parameter meaning | A fixture name as a parameter inside a test or fixture refers to the value pytest passed in for that call. |

### Progress Updates

| Update type | Details |
|---|---|
| Attempt 1 summary | Attempt 1 established good understanding of same-file access, fixture-to-fixture dependency, and `conftest.py` directory visibility. |
| Remaining focus areas | - why helper functions do not get auto-injection <br>- the difference between fixture function objects and fixture return values <br>- import-based sharing versus `conftest.py` sharing |
