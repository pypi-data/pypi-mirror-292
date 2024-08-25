"""
* CLI Application
* Primarily used for testing and development.
"""
# Third Party Imports
import click

# Local Imports
from .test_schema import TestSchema


@click.group(commands={'test-schema': TestSchema})
def HexproofCLI():
    """Hexproof CLI application entrypoint."""
    pass


# Export CLI Application
__all__ = ['HexproofCLI']
