"""Misc util functions."""
from __future__ import annotations

import pathlib
import pickle
import unicodedata
from collections.abc import Generator, Iterable
from typing import Any

import yaml

from sparv.api import get_logger
from sparv.api.classes import Model
from sparv.core.misc import parse_annotation_list  # noqa: F401 - Imported to make available through the API

logger = get_logger(__name__)


def dump_yaml(data: dict, resolve_alias: bool = False, sort_keys: bool = False, indent: int = 2) -> str:
    """Convert a dict to a YAML document string.

    Args:
        data: The data to be dumped.
        resolve_alias: Will replace aliases with their anchor's content if set to True.
        sort_keys: Whether to sort the keys alphabetically.
        indent: Number of spaces used for indentation.

    Returns:
        The YAML document as a string.
    """

    class IndentDumper(yaml.SafeDumper):
        """Customized YAML dumper that indents lists."""

        def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:  # noqa: ARG002
            """Force indentation."""
            return super().increase_indent(flow)

    def str_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
        """Custom string representer for prettier multiline strings."""  # noqa: DOC201
        if "\n" in data:  # Check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    def obj_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
        """Custom representer to cast subclasses of str to strings."""  # noqa: DOC201
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))

    yaml.representer.SafeRepresenter.add_representer(str, str_representer)
    yaml.representer.SafeRepresenter.add_multi_representer(str, obj_representer)

    if resolve_alias:
        # Resolve aliases and replace them with their anchors' contents
        yaml.SafeDumper.ignore_aliases = lambda *_args: True

    return yaml.dump(
        data, sort_keys=sort_keys, allow_unicode=True, Dumper=IndentDumper, indent=indent, default_flow_style=False
    )


# TODO: Split into two functions: one for Sparv-internal lists of values, and one used by the CWB module to create the
# CWB-specific set format.
def cwbset(
    values: Iterable[str],
    delimiter: str = "|",
    affix: str = "|",
    sort: bool = False,
    maxlength: int = 4095,
    encoding: str = "UTF-8",
) -> str:
    """Take an iterable with strings and return a set in the format used by Corpus Workbench.

    Args:
        values: The values to be joined.
        delimiter: The delimiter to be used between the values.
        affix: The affix to be used at the beginning and end of the set.
        sort: Whether to sort the values before joining them.
        maxlength: Maximum length of the resulting string.
        encoding: Encoding to use when calculating the length of the string.

    Returns:
        The joined string.
    """
    values = list(values)
    if sort:
        values.sort()
    if maxlength:
        length = 1  # Including the last affix
        for i, value in enumerate(values):
            length += len(value.encode(encoding)) + 1
            if length > maxlength:
                values = values[:i]
                break
    return affix if not values else affix + delimiter.join(values) + affix


def set_to_list(setstring: str, delimiter: str = "|", affix: str = "|") -> list[str]:
    """Turn a set string into a list.

    Args:
        setstring: The set string to be converted.
        delimiter: The delimiter used in the set string.
        affix: The affix used in the set string.

    Returns:
        A list of strings.
    """
    if setstring == affix:
        return []
    setstring = setstring.strip(affix)
    return setstring.split(delimiter)


def remove_control_characters(text: str, keep: str | None = None) -> str:
    """Remove control characters from text, except for those in 'keep'.

    Args:
        text: The text to be processed.
        keep: A list of control characters to keep.

    Returns:
        The text with control characters removed.
    """
    if keep is None:
        keep = ["\n", "\t", "\r"]
    return "".join(c for c in text if c in keep or unicodedata.category(c)[0:2] != "Cc")


def remove_formatting_characters(text: str, keep: str | None = None) -> str:
    """Remove formatting characters from text, except for those in 'keep'.

    Args:
        text: The text to be processed.
        keep: A list of formatting characters to keep.

    Returns:
        The text with formatting characters removed.
    """
    if keep is None:
        keep = []
    return "".join(c for c in text if c in keep or unicodedata.category(c)[0:2] != "Cf")


def chain(annotations: Iterable[dict], default: Any = None) -> Generator[tuple]:
    """Create a functional composition of a list of annotations.

    Args:
        annotations: A list of dictionaries where each dictionary maps keys to values. The values are keys in the next
            dictionary, except for the last dictionary where the values are the final values.
        default: The default value to return if a key is not found.

    Returns:
        A generator that yields tuples with the original key and the final value.

    E.g., token.sentence + sentence.id -> token.sentence-id

    >>> from pprint import pprint
    >>> pprint(dict(
    ...   chain([{"w:1": "s:A",
    ...           "w:2": "s:A",
    ...           "w:3": "s:B",
    ...           "w:4": "s:C",
    ...           "w:5": "s:missing"},
    ...          {"s:A": "text:I",
    ...           "s:B": "text:II",
    ...           "s:C": "text:mystery"},
    ...          {"text:I": "The Bible",
    ...           "text:II": "The Samannaphala Sutta"}],
    ...         default="The Principia Discordia")))
    {'w:1': 'The Bible',
     'w:2': 'The Bible',
     'w:3': 'The Samannaphala Sutta',
     'w:4': 'The Principia Discordia',
     'w:5': 'The Principia Discordia'}
    """
    def follow(key: Any) -> Any:
        for annot in annotations:
            try:
                key = annot[key]
            except KeyError:  # noqa: PERF203
                return default
        return key
    return ((key, follow(key)) for key in annotations[0])


def test_lexicon(lexicon: dict, testwords: list[str]) -> None:
    """Test the validity of a lexicon.

    Takes a dictionary ('lexicon') and a list of test words that are expected to occur as keys in 'lexicon'.
    Prints the value for each test word.

    Args:
        lexicon: The lexicon to test.
        testwords: A list of test words.
    """
    logger.info("Testing annotations...")
    for key in testwords:
        logger.info("  %s = %s", key, lexicon.get(key))


class PickledLexicon:
    """Read basic pickled lexicon and look up keys."""

    def __init__(self, picklefile: pathlib.Path | Model, verbose: bool = True) -> None:
        """Read lexicon from picklefile."""
        picklefile_path: pathlib.Path = picklefile.path if isinstance(picklefile, Model) else picklefile
        if verbose:
            logger.info("Reading lexicon: %s", picklefile)
        with picklefile_path.open("rb") as f:
            self.lexicon = pickle.load(f)
        if verbose:
            logger.info("OK, read %d words", len(self.lexicon))

    def lookup(self, key: Any, default: Any = None) -> Any:
        """Lookup a key in the lexicon.

        Args:
            key: The key to look up.
            default: The default value to return if the key is not found.

        Returns:
            The value for the key, or the default value if the key is not found.
        """
        return self.lexicon.get(key, default)


def get_language_name_by_part3(part3: str) -> str | None:
    """Return language name in English given an ISO 639-3 code.

    Args:
        part3: ISO 639-3 code.

    Returns:
        Language name in English.
    """
    import pycountry  # noqa: PLC0415

    lang = pycountry.languages.get(alpha_3=part3)
    return lang.name if lang else None


def get_language_part1_by_part3(part3: str) -> str | None:
    """Return ISO 639-1 code given an ISO 639-3 code.

    Args:
        part3: ISO 639-3 code.

    Returns:
        ISO 639-1 code.
    """
    import pycountry  # noqa: PLC0415

    lang = pycountry.languages.get(alpha_3=part3)
    return lang.alpha_2 if lang else None
