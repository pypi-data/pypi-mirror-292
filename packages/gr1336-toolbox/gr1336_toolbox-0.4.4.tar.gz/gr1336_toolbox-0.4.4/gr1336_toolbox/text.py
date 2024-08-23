import re
import nltk
import pyperclip
import markdown2
import subprocess
from .fast_types import *
from datetime import datetime
from textblob import TextBlob
from nltk.tag import PerceptronTagger
from markdownify import markdownify as md
from string import whitespace, punctuation
from textblob.exceptions import MissingCorpusError
from typing import List, Dict, Union, Tuple, AnyStr

TLSTRINGS = list(whitespace) + list(punctuation)


def download_nltk():
    nltk.download("wordnet")
    nltk.download("cmudict")
    nltk.download("punkt")
    nltk.download("punkt_tab")
    nltk.download("averaged_perceptron_tagger")


def extract_keys(string: str) -> list | list[str]:
    # Use a regular expression to find all occurrences of {key} in the string
    keys = re.findall(r"\{(\w+)\}", string)
    return keys


class ProcessSplit:
    """
    Apache 2.0 license
    Modified from https://github.com/fakerybakery/txtsplit/blob/main/txtsplit/__init__.py
    with was modified from Modified from https://github.com/neonbjb/tortoise-tts/blob/main/tortoise/utils/text.py
    """

    def __init__(self, text: str, desired_length=100, max_length=200):
        self.text = text
        self.rv = []
        self.in_quote = False
        self.current = ""
        self.split_pos = []
        self.pos = -1
        self.end_pos = len(self.text) - 1
        self.max_length = max_length
        self.desired_length = desired_length

    def seek(self, delta):
        is_neg = delta < 0
        for _ in range(abs(delta)):
            if is_neg:
                self.pos -= 1
                self.current = self.current[:-1]
            else:
                self.pos += 1
                self.current += self.text[self.pos]
            if self.text[self.pos] in '"“”':
                self.in_quote = not self.in_quote
        return self.text[self.pos]

    def peek(self, delta):
        p = self.pos + delta
        return self.text[p] if p < self.end_pos and p >= 0 else ""

    def commit(self):
        self.rv.append(self.current)
        self.current = ""
        self.split_pos = []

    def run(self) -> list[str]:
        while self.pos < self.end_pos:
            c = self.seek(1)
            if len(self.current) >= self.max_length:
                if len(self.split_pos) > 0 and len(self.current) > (
                    self.desired_length / 2
                ):
                    d = self.pos - self.split_pos[-1]
                    self.seek(-d)
                else:
                    while (
                        c not in "!?.\n "
                        and self.pos > 0
                        and len(self.current) > self.desired_length
                    ):
                        c = self.seek(-1)
                self.commit()
            elif not self.in_quote and (
                c in "!?\n" or (c == "." and self.peek(1) in "\n ")
            ):
                while (
                    self.pos < len(self.text) - 1
                    and len(self.current) < self.max_length
                    and self.peek(1) in "!?."
                ):
                    c = self.seek(1)
                self.split_pos.append(self.pos)
                if len(self.current) >= self.desired_length:
                    self.commit()
            elif self.in_quote and self.peek(1) == '"“”' and self.peek(2) in "\n ":
                self.seek(2)
                self.split_pos.append(self.pos)
        self.rv.append(self.current)
        self.rv = [s.strip() for s in self.rv]
        self.rv = [
            s for s in self.rv if len(s) > 0 and not re.match(r"^[\s\.,;:!?]*$", s)
        ]
        return self.rv


def current_time():
    """
    Returns the current date and time in a 'YYYY-MM-DD-HHMMSS' format.

    Returns:
        str: The current date and time.
    """
    return f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"


def recursive_replacer(text: str, dic: dict[str, str]) -> str:
    """
    Recursively replaces all keys of the dictionary with their corresponding values within a given string.

    Args:
        text (str): The original text.
        replacements (Dict[str, str]): A dictionary where keys are what to replace and values is what they will be replaced by

    Returns:
        str: The final modified text
    """
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def clipboard(text: str):
    """
    Set the clipboard to the given text.
    """
    pyperclip.copy(text)


def unescape(elem: str) -> str:
    """
    Unescapes the given string by encoding it to bytes and then decoding with 'unicode-escape' errors ignored.

    Args:
        elem (Optional[str]): The input string. If None, returns an empty string.

    Returns:
        str: The unescaped string.
    """
    assert is_string(elem, True), "The input should be a valid string."
    return elem.encode().decode("unicode-escape", "ignore")


def blob_split(text: str) -> List[str]:
    """
    Splits the input text into sentences using TextBlob.

    Args:
        text (str): The input text to split.

    Returns:
        list[str]: A list of the detected sentences in the provided text.
    """
    try:
        return [x for x in TextBlob(text).raw_sentences]
    except MissingCorpusError:
        subprocess.run(
            f"python -m textblob.download_corpora",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        download_nltk()
        return [x for x in TextBlob(text).raw_sentences]


def max_rfinder(txt: str, items_to_find: Union[List[str], Tuple[str, ...]]):
    """
    Finds the last occurrence of any item in a list or tuple within a string.

    Args:
        txt (str): The input string.
        items_to_find (Union[list[str], tuple[str]]): A list or tuple containing strings to find in 'txt'.

    Returns:
        int: The index of the last found item, -1 if no item is found.
    """
    highest_results = -1
    for item in items_to_find:
        current = txt.rfind(item)
        if current > highest_results:
            highest_results = current
    return highest_results


def check_next_string(
    text: str,
    current_id: int,
    text_to_match: str | list[str] | None = None,
    is_out_of_index_valid: bool = False,
):
    """
    Checks if the next character in a string matches one or more possibilities.

    Args:
        text (str): The input string.
        current_id (int): The index of the current character within the string.
        text_to_match (Union[str, list[str], None]): A single character to match or a list/tuple of characters.
                        If not provided and is_out_of_index_valid will be used as a result. Defaults to None.
        is_out_of_index_valid (bool): Whether returning True when the index is out of bounds should be valid. Defaults to False.

    Returns:
        bool: True, if any condition is met; False otherwise.
    """
    try:
        if is_array(text_to_match):
            return text[current_id + 1] in text_to_match
        return text[current_id + 1] == text_to_match
    except IndexError:
        return is_out_of_index_valid


def check_previous_string(
    text: str,
    current_id: int,
    text_to_match: str | list[str] | None = None,
    is_out_of_index_valid: bool = False,
):
    """
    Checks if the previous character in a string matches one or more possibilities.

    Args:
        text (str): The input string.
        current_id (int): The index of the current character within the string.
        text_to_match (Union[str, list[str], None]): A single character to match or a list/tuple of characters.
                        If not provided and is_out_of_index_valid will be used as a result. Defaults to None.
        is_out_of_index_valid (bool): Whether returning True when the index is out of bounds should be valid. Defaults to False.

    Returns:
        bool: True, if any condition is met; False otherwise.
    """

    try:
        if is_array(text_to_match):
            return text[current_id - 1] in text_to_match
        return text[current_id - 1] == text_to_match
    except IndexError:
        return is_out_of_index_valid


def trimincompletesentence(txt: str) -> str:
    """
    Tries to trim an incomplete sentence to the nearest complete one. If it fails returns the original sentence back.

    Args:
        txt (str): The original string containing sentences.
            If not complete, it will be trimmed to end with a valid punctuation mark.

    Returns:
        str: The finalized string.

    Example:

        >>> trimincompletesentence("Hello World! How are you doing?")
        "Hello World!"

        >>> trimincompletesentence("I like programming.")
        "I like programming." # Returns the sentence as it was.
        >>> trimincompletesentence("Hello there. This sentence is incomplete")
        "Hello there." # Returns the lastest complete sequence.
        >>> trimincompletesentence("Hello there This sentence is incomplete")
        "Hello there This sentence is incomplete" # Returns the entire sentence if no cutting point was found.
    """
    possible_ends = (".", "?", "!", '."', '?"', '!"')
    txt = str(txt).rstrip()
    lastpunc = max_rfinder(txt, possible_ends)
    ln = len(txt)
    lastpunc = max(txt.rfind("."), txt.rfind("!"), txt.rfind("?"))
    if lastpunc < ln - 1:
        if txt[lastpunc + 1] == '"':
            lastpunc = lastpunc + 1
    if lastpunc >= 0:
        txt = txt[: lastpunc + 1]
    return txt


def simplify_quotes(txt: str) -> str:
    """
    Replaces special characters with standard single or double quotes.

    Args:
        txt (str): The input string containing special quote characters.

    Returns:
        str: The simplified string without the special quote characters.
    """
    assert is_string(txt, True), f"The input '{txt}' is not a valid string"
    replacements = {
        "“": '"',
        "”": '"',
        "’": "'",
        "‘": "'",
        "`": "'",
    }
    return recursive_replacer(txt, replacements)


def clear_empty(text: str, clear_empty_lines: bool = True) -> str:
    """A better way to clear multiple empty lines than just using regex for it all.
    For example if you use:
    ```py
    text = "Here is my text.\nIt should only clear empty spaces and           not clear the lines out.\n\n\nThe lines should be preserved!"

    results = re.sub(r"\s+", " ", text)
    # results = "Here is my text. It should only clear empty spaces and not clear the lines out. The lines should be preserved!"
    ```
    As shown in the example above, the lines were all removed even if we just wanted to remove empty spaces.

    This function can also clear empty lines out, with may be useful. Its enabled by default.
    """
    return "\n".join(
        [
            re.sub(r"\s+", " ", x.strip())
            for x in text.splitlines()
            if not clear_empty_lines or x.strip()
        ]
    )


def txtsplit(
    text: str,
    desired_length=100,
    max_length=200,
    simplify_quote: bool = True,
) -> list[str]:
    text = clear_empty(text, True)
    if simplify_quote:
        text = simplify_quotes(text)
    processor = ProcessSplit(text, desired_length, max_length)
    return processor.run()


def remove_special_characters(text: str) -> str:
    """
    Remove special characters from the given text using regular expressions.
    """
    pattern = r"a-zA-Z0-9\s\'\?\!\@\#\$\%\&\:\;\.\,\(\)\[\]\{\}\=\+\-\*"
    cleaned_text = re.sub(pattern, "", text)
    return cleaned_text


def html_to_markdown(html: AnyStr) -> str:
    """
    Converts HTML content to Markdown format.

    Args:
        html (str): The HTML string that needs to be converted.
                    Example - "<h1>Hello, World!</h1>"

    Returns:
        str: The corresponding markdown version of the inputted HTML
             Example - "# Hello, World!"
    """
    return md(html)


def markdown_to_html(markdown: AnyStr) -> str:
    """
    Converts Markdown text to HTML.

    Args:
        markdown (Union[str, bytes]): The input Markdown text. Can be either a string or bytes object.

    Returns:
        str: The converted HTML.
    """
    return markdown2.markdown(markdown)


def replace_pos_tags(text: str, target_pos_tags: list[str], replacer: str):
    filtered_text = text.replace("{}", "")
    # checks if there is fstrings to remove them to avoid conflicts.
    all_fstrings = extract_keys(text)
    if all_fstrings:
        filtered_text = recursive_replacer(
            filtered_text, {key: "" for key in all_fstrings}
        )
    try:
        tokens = nltk.word_tokenize(filtered_text)
        tagged_tokens = PerceptronTagger().tag(tokens)
    except:
        download_nltk()
        tokens = nltk.word_tokenize(filtered_text)
        tagged_tokens = PerceptronTagger().tag(tokens)

    raplacers = {}
    for word, pos in tagged_tokens:
        if pos in target_pos_tags:
            for start_txt in TLSTRINGS:
                for end_txt in TLSTRINGS:
                    raplacers[f"{start_txt}{word}{end_txt}"] = (
                        f"{start_txt}{replacer}{end_txt}"
                    )

    if raplacers:
        return recursive_replacer(text, raplacers)
    return text


__all__ = [
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
