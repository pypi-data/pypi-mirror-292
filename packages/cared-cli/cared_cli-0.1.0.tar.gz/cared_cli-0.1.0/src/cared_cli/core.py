# file with functions called by cli commands


def hello(you: str) -> str:
    """Says hello to the world or to you if you give your name."""
    return f"Hello, {you}!"
