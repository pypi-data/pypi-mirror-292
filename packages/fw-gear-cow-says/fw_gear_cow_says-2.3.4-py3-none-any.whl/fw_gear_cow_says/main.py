"""Main module."""

import logging

import cowsay

log = logging.getLogger(__name__)


def run(animal, text):
    """Prints what the animal has to say."""
    say_fn = getattr(cowsay, animal)
    say_fn(text)

    # Return exit code of 0 on success
    return 0
