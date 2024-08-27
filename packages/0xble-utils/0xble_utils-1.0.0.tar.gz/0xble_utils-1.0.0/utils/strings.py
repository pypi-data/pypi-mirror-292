import re


def titlecase(text: str):
    # Replace underscores or dashes with spaces
    text = re.sub(r"[_-]", " ", text)

    # Capitalize the first letter of each word
    text = text.title()

    return text


def truncate(text: str, length: int = 120, ellipsis: str = "..."):
    if len(text) > length:
        text = text[: length // 2] + ellipsis + text[-length // 2 :]

    return text
