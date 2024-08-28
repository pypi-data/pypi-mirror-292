import re as _re

from markitup.html import elem as _elem


def style(
    text: str,
    word: str,
    strong: bool = False,
    bold: bool = False,
    italic: bool = False,
    emphasis: bool = False,
    underline: bool = False,
    url: str = "",
    count: int = 0,
    case_sensitive: bool = False
) -> str:
    """
    Given a string and a replacement map, it returns the replaced string.
    :param str string: string to execute replacements on
    :param dict words: replacement dictionary {value to find: value to replace}
    :param bool ignore_case: whether the match should be case insensitive
    :rtype: str

    Reference : https://stackoverflow.com/a/6117124/14923024
    """
    mod_word = word
    if strong:
        mod_word = f"<strong>{mod_word}</strong>"
    if bold:
        mod_word = f"<b>{mod_word}</b>"
    if italic:
        mod_word = f"<i>{mod_word}</i>"
    if emphasis:
        mod_word = f"<em>{mod_word}</em>"
    if underline:
        mod_word = f"<u>{mod_word}</u>"
    if url:
        mod_word = str(_elem.a(mod_word, href=url))
    pattern = _re.compile(_re.escape(word), flags=0 if case_sensitive else _re.IGNORECASE)
    replaced_text = pattern.sub(mod_word, text, count=count)
    return replaced_text
