"""Parser module to parse gear config.json."""

from typing import Tuple

from flywheel_gear_toolkit import GearToolkitContext


def parse_config(
    gear_context: GearToolkitContext,
) -> Tuple[str, str]:
    """Parses gear_context config.json file and returns relevant inputs and options."""
    animal = gear_context.config.get("animal")
    with open(gear_context.get_input_path("text-input"), "r") as text_file:
        text = " ".join(text_file.readlines())

    return animal, text
