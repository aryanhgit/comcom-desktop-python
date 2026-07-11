import re


def natural_key(value: str):
    return [
        int(chunk) if chunk.isdigit() else chunk.lower()
        for chunk in re.split(r"(\d+)", value)
    ]
