"""Module for handling persona-related functionality in the Syft theme."""

import re

from docutils import nodes
from sphinx.transforms import SphinxTransform


def convert_shortcodes_in_text(text, shortcode_to_image):
    """Convert short codes in text."""
    pattern = re.compile(r"(\|\:\w+?\:\|)")
    parts = pattern.split(text)
    result = []

    for part in parts:
        if part in shortcode_to_image:
            image_node = nodes.image(
                uri=shortcode_to_image[part], alt=part, classes=["persona"]
            )
            result.append(image_node)
        else:
            result.append(nodes.Text(part))

    return result


def convert_shortcodes_to_nodes(node, shortcode_to_image):
    """Convert short codes to nodes."""
    if isinstance(node, nodes.Text):
        new_nodes = convert_shortcodes_in_text(node.astext(), shortcode_to_image)
        for new_node in new_nodes:
            node.parent.insert(node.parent.index(node), new_node)
        node.parent.remove(node)
    elif isinstance(node, nodes.Element):
        for child in list(node.children):  # Use a copy of the list for safe iteration
            convert_shortcodes_to_nodes(child, shortcode_to_image)


class Persona(SphinxTransform):
    """A Persona directive for use with headers."""

    default_priority = 211

    def apply(self):
        """Apply persona file."""
        # Retrieve the custom shortcode to image mapping from the configuration
        shortcode_to_image = self.app.config.html_theme_options.get(
            "custom_shortcode_to_image", {}
        )
        convert_shortcodes_to_nodes(self.document, shortcode_to_image)
