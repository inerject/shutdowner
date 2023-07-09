from pathlib import Path


def abs_path(relative_path):
    return (Path(__file__).parent / relative_path).resolve()


def str_abs_path(relative_path):
    return str(abs_path(relative_path))
