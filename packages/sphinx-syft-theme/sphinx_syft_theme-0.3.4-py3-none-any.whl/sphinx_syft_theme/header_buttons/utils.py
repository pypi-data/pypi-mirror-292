"""Utility functions for header buttons in the Syft theme."""

import os


def get_svg_content(relative_path):
    """Returns the content of an SVG file given a relative path from the project root."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, relative_path)
    with open(full_path, encoding="utf-8") as file:
        return file.read()
