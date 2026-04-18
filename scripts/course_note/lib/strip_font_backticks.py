#!/usr/bin/env python3
"""Remove Markdown inline-code backticks erroneously wrapped around <font color=...> spans."""
import re
import sys

# ` <font color="#hex"> ... </font> `  →  <font ...> ... </font>
_PATTERN = re.compile(
    r"`(<font\s+color=\"[^\"]+\">.*?</font>)`",
    re.DOTALL,
)


def strip_font_backticks(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = _PATTERN.sub(r"\1", text)
    return text


def main() -> None:
    data = sys.stdin.read()
    sys.stdout.write(strip_font_backticks(data))


if __name__ == "__main__":
    main()
