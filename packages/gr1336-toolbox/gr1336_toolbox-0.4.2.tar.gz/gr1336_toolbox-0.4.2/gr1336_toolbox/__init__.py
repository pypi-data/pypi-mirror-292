from .misc import *
from .text import *
from .files import *
from .fast_types import *
from . import fast_types, files, misc, text

__all__ = [
    # main modules:
    "files",
    "fast_types",
    "misc",
    "text",
    # fast_types:
    "is_int",
    "is_string",
    "is_dict",
    "is_float",
    "is_number",
    "is_boolean",
    "is_tuple",
    "is_list",
    "is_array",
    "keys_in_text",
    "compare_none",
    "valid_path",
    "non_empty_check",
    # files:
    "get_folders",
    "get_files",
    "create_path",
    "load_json",
    "save_json",
    "load_text",
    "save_text",
    "load_yaml",
    "save_yaml",
    "move_to",
    "delete_path",
    # misc:
    "import_functions",
    "sort_array",
    "try_call",
    "dict_to_list",
    "filter_list",
    "flatten_list",
    "percentage_difference",
    "process_number",
    "remove_file_extension",
    # text:
    "current_time",
    "max_rfinder",
    "check_next_string",
    "check_previous_string",
    "recursive_replacer",
    "clipboard",
    "unescape",
    "blob_split",
    "trimincompletesentence",
    "clear_empty",
    "txtsplit",
    "remove_special_characters",
    "markdown_to_html",
    "replace_pos_tags",
]
