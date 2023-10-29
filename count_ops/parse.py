import ast
from pycparser import CParser


def strip_comments(txt):
    lines = txt.split("\n")
    new_lines = []
    for line in lines:
        if "//" in line:
            line = line[: line.index("//")]
        new_lines.append(line)
    return "\n".join(new_lines)


def parse(txt: str):
    try:
        return ast.parse(txt)
    except:
        txt = strip_comments(txt)
        return CParser().parse(txt)
