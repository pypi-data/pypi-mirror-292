import uuid
import traceback
import importlib.util
from pathlib import Path
from .files import get_files
from typing import Any, TypeAlias, Literal, Callable
from .fast_types import is_array, is_dict, is_number, is_string, is_float, is_int


def percentage_difference(num1: int, num2: int):
    """
    Calculate the percentage difference between two numbers.

    Parameters:
    - num1 (float): The first number.
    - num2 (float): The second number.

    Returns:
    float: The percentage difference.
    """
    assert (
        num1 != 0
    ), "Cannot calculate percentage difference when the first number is zero."

    percentage_difference = ((num2 - num1) / num1) * 100
    return abs(percentage_difference)


def flatten_list(entry):
    """
    Example:
    ```py
    from grtoolbox.types import flatten_list

    sample = ["test", [[[1]], [2]], 3, [{"last":4}]]
    results = flatten_list(sample)
    # results = ["test", 1, 2, 3, {"last": 4}]
    ```"""
    if is_array(entry):
        return [item for sublist in entry for item in flatten_list(sublist)]
    return [entry] if entry is not None else []


def filter_list(entry: list | tuple, types: TypeAlias) -> list:
    if not is_array(entry, allow_empty=False):
        return []
    return [x for x in entry if isinstance(x, types)]


def dict_to_list(
    entry: dict[str, Any],
    return_item: Literal["key", "content"] = "content",
) -> list:
    res = []
    assert is_dict(
        entry
    ), "the entry provided is not a valid dictionary. Received: {}".format(entry)
    if return_item == "content":
        return list(entry.values())
    return list(entry.keys())


def try_call(comp: Callable, verbose_exception: bool = False, **kwargs):
    """Can be used to call a function prune to errors, it returns its response if successfuly executed, otherwise it prints out an traceback if verbose_exception.

    Args:
        comp (Callable): _description_
        verbose_exception (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    try:
        return comp(**kwargs)
    except Exception as e:
        if verbose_exception:
            print(f"Exception: '{e}'. Traceback:")
            traceback.print_exc()
        return None


def import_functions(path: str | Path, target_function: str, pattern: str = "*.py"):
    """
    Imports and returns all functions from .py files in the specified directory matching a certain function name.

    Args:
        path (str or Path): The path of the directories to search for the Python files.
        target_function (str): The exact string representing the function name to be searched within each file.

    Returns:
        list: A list containing all the functions with the given name found in the specified directory and subdirectories.

    Example:
        >>> import_functions('/path/to/directory', 'some_function')
        [<function some_function at 0x7f036b4c6958>, <function some_function at 0x7f036b4c69a0>]
    """
    results = []
    python_files = [x for x in Path(path).rglob(pattern) if x.is_file()]
    for file in python_files:
        spec = importlib.util.spec_from_file_location(file.name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, target_function):
            results.append(getattr(module, target_function))
    return results


def sort_array(array: list | tuple, reverse: bool = False):
    """
    Sorts a list of tuples based on the first element of each tuple.

    Args:
        imports (list of tuple): A list where each element is a tuple,
                                 with the first element being a string or integer.

    Returns:
        list of tuple: The sorted list of import tuples.

    Example:
        >>> sort_imports([(3, 'bar'), (1, 'foo'), (2, 'baz')])
        [(1, 'foo'), (2, 'baz'), (3, 'bar')]
    """
    if is_array(array, allow_empty=False):
        return sorted(array, key=lambda x: x[0], reverse=reverse)
    return array


def process_number(
    value: int | float | str | Any,
    default_value: int | float | Any | None = None,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
    return_type: Literal["int", "float"] = None,
) -> int | float | Any:
    """Process a number while constraining it

    Args:
        value (int | float | str | Any): _description_
        default_value (int | float | Any | None, optional): _description_. Defaults to None.
        minimum (int | float | None, optional): _description_. Defaults to None.
        maximum (int | float | None, optional): _description_. Defaults to None.
        return_type (Literal[&quot;int&quot;, &quot;float&quot;], optional): _description_. Defaults to None.

    Returns:
        int | float | Any: _description_
    """
    if not is_number(value, True):
        return default_value

    if is_string(value, strip_string=True):
        value = str(value).strip()
        if is_float(value, True):
            try:
                value = float(value)
            except ValueError:
                return default_value

    if is_int(minimum, True):
        value = max(value, int(minimum))
    elif is_float(minimum, True):
        value = max(value, float(minimum))

    if is_int(maximum, True):
        value = min(value, int(maximum))
    elif is_float(maximum, True):
        value = min(value, float(maximum))

    return (
        value
        if return_type is None
        else float(value) if return_type == "float" else int(value)
    )


def remove_file_extension(
    file_name: str | Path, default_file_name: str | None = None
) -> str:
    """Remove the extension from a given file_name. If filename is not valid, then it tries to use default_file_name.
    If both are invalid, it returns a random uuid4 in string format (not hex).

    Args:
        file_name (str | Path): _description_
        default_file_name (str | None, optional): _description_. Defaults to None.

    Returns:
        str: _description_
    """
    if is_string(file_name, False, True):
        return Path(file_name).stem
    elif is_string(default_file_name, False, True):
        return str(default_file_name)
    return str(uuid.uuid4())


__all__ = [
    "import_functions",
    "sort_array",
    "try_call",
    "dict_to_list",
    "filter_list",
    "flatten_list",
    "percentage_difference",
    "process_number",
    "remove_file_extension",
]
