"""
* CLI Commands: Test
"""
# Standard Library Imports
import os
from pathlib import Path

# Third Party Imports
import click
from omnitils.files import load_data_file, DisposableDir
from omnitils.logs import logger, log_test_result

# Local Imports
from hexproof.mtgjson import fetch as MTGJsonFetch
from hexproof.mtgjson import schema as MTGJson
from hexproof.scryfall import fetch as ScryfallFetch
from hexproof.scryfall import schema as Scryfall
from hexproof.vectors import fetch as VectorsFetch
from hexproof.vectors import schema as Vectors

# Core variables
project_cwd = Path(__file__).parent.parent.parent

"""
* Commands: MTGJSON
"""


@click.command
@log_test_result(on_error='Invalid Schemas: Card', on_success='Schemas Validated: Card')
def test_mtgjson_schema_card() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.card` module."""
    # Atomic card
    obj_atomic = MTGJsonFetch.get_cards_atomic_all()
    assert isinstance(next(iter(obj_atomic.values())), MTGJson.CardAtomic)


@click.command
@log_test_result(on_error='Invalid Schemas: Card Types', on_success='Schemas Validated: Card Types')
def test_mtgjson_schema_card_types() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.card_types` module."""
    obj = MTGJsonFetch.get_card_types()
    assert isinstance(obj, MTGJson.CardTypes)


@click.command
@log_test_result(on_error='Invalid Schemas: Deck', on_success='Schemas Validated: Deck')
def test_mtgjson_schema_deck() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.deck` module."""

    # Check all deck files
    with DisposableDir(path=project_cwd) as _path:
        all_decks = MTGJsonFetch.cache_decks_all(_path)
        for _deck in os.listdir(all_decks):
            _deck_json = all_decks / _deck

            # Check deck JSON data file
            if _deck_json.is_file() and _deck_json.suffix == '.json':
                obj = MTGJson.Deck(**load_data_file(_deck_json)['data'])
                assert isinstance(obj, MTGJson.Deck)
                del obj


@click.command
@log_test_result(on_error='Invalid Schemas: Deck List', on_success='Schemas Validated: Deck List')
def test_mtgjson_schema_deck_list() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.deck_list` module."""
    obj = MTGJsonFetch.get_deck_list()
    assert isinstance(obj[0], MTGJson.DeckList)


@click.command
@log_test_result(on_error='Invalid Schemas: Keywords', on_success='Schemas Validated: Keywords')
def test_mtgjson_schema_keywords() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.keywords` module."""
    obj = MTGJsonFetch.get_keywords()
    assert isinstance(obj, MTGJson.Keywords)


@click.command
@log_test_result(on_error='Invalid Schemas: Meta', on_success='Schemas Validated: Meta')
def test_mtgjson_schema_meta() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.meta` module."""
    obj = MTGJsonFetch.get_meta()
    assert isinstance(obj, MTGJson.Meta)


@click.command
@log_test_result(on_error='Invalid Schemas: Price', on_success='Schemas Validated: Price')
def test_mtgjson_schema_price() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.price` module."""
    obj: dict = MTGJsonFetch.get_prices_today_all()
    assert isinstance(next(iter(obj.values())), MTGJson.PriceFormats)


@click.command
@log_test_result(on_error='Invalid Schemas: Set', on_success='Schemas Validated: Set')
def test_mtgjson_schema_set() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.set` module."""

    # Check all deck files
    with DisposableDir(path=project_cwd) as _path:
        all_decks = MTGJsonFetch.cache_sets_all(_path)
        for _set in os.listdir(all_decks):
            _set_json = all_decks / _set

            # Check deck JSON data file
            if _set_json.is_file() and _set_json.suffix == '.json':
                obj = MTGJson.Set(**load_data_file(_set_json)['data'])
                assert isinstance(obj, MTGJson.Set)
                del obj


@click.command
@log_test_result(on_error='Invalid Schemas: Set List', on_success='Schemas Validated: Set List')
def test_mtgjson_schema_set_list() -> None:
    """Tests MTGJSON schemas defined in `mtgjson.schema.set_list` module."""
    obj = MTGJsonFetch.get_set_list()
    assert isinstance(obj[0], MTGJson.SetList)


@click.command
@click.pass_context
def test_mtgjson_schema_all(ctx: click.Context):
    """Tests all MTGJSON schemas."""

    # Tests to run
    logger.info('Testing Schemas: MTGJSON')
    tests = [
        test_mtgjson_schema_card_types,
        test_mtgjson_schema_deck,
        test_mtgjson_schema_deck_list,
        test_mtgjson_schema_keywords,
        test_mtgjson_schema_meta,
        test_mtgjson_schema_price,
        test_mtgjson_schema_set,
        test_mtgjson_schema_set_list
    ]

    # Test each schema
    for func in tests:
        ctx.invoke(func)


"""
* Commands: Scryfall
"""


@click.command
@log_test_result(on_error='Invalid Schemas: Card', on_success='Schemas Validated: Card')
def test_scryfall_schema_card() -> None:
    """Tests Scryfall schemas defined in `scryfall.schema.card` module."""
    obj = ScryfallFetch.get_card_named('Damnation', set_code='TSR')
    assert isinstance(obj, Scryfall.Card)


@click.command
@log_test_result(on_error='Invalid Schemas: Ruling', on_success='Schemas Validated: Ruling')
def test_scryfall_schema_ruling() -> None:
    """Tests Scryfall schemas defined in `scryfall.schema.ruling` module."""
    obj = ScryfallFetch.get_card_rulings('CMA', '176')
    assert isinstance(obj[0], Scryfall.Ruling)


@click.command
@log_test_result(on_error='Invalid Schemas: Set', on_success='Schemas Validated: Set')
def test_scryfall_schema_set() -> None:
    """Tests Scryfall schemas defined in `scryfall.schema.set` module."""
    obj = ScryfallFetch.get_set_list()
    assert isinstance(obj[0], Scryfall.Set)


@click.command
@click.pass_context
def test_scryfall_schema_all(ctx: click.Context):
    """Tests all Scryfall schemas."""

    # Tests to run
    logger.info('Testing Schemas: Scryfall')
    tests = [
        test_scryfall_schema_card,
        test_scryfall_schema_ruling,
        test_scryfall_schema_set
    ]

    # Test each schema
    for func in tests:
        ctx.invoke(func)


"""
* Commands: MTG Vectors
"""


@click.command
@log_test_result(on_error='Invalid Schemas: Manifest', on_success='Schemas Validated: Manifest')
def test_vectors_schema_manifest() -> None:
    """Tests MTG Vectors 'Manifest' schema and nested schemas defined in `vectors.schema` module."""
    obj = VectorsFetch.get_vectors_manifest()
    assert isinstance(obj, Vectors.Manifest)


@click.command
@click.pass_context
def test_vectors_schema_all(ctx: click.Context):
    """Tests all MTG Vectors schemas."""

    # Tests to run
    logger.info('Testing Schemas: MTG Vectors')
    tests = [
        test_vectors_schema_manifest,
    ]

    # Test each schema
    for func in tests:
        ctx.invoke(func)


"""
* Command Groups
"""


@click.command
@click.pass_context
def test_all_schema(ctx: click.Context) -> None:
    """Tests every schema group."""
    ctx.invoke(test_mtgjson_schema_all)
    ctx.invoke(test_scryfall_schema_all)
    ctx.invoke(test_vectors_schema_all)


@click.group(
    name='mtgjson',
    commands={
        '.': test_mtgjson_schema_all,
        'card-types': test_mtgjson_schema_card_types,
        'deck': test_mtgjson_schema_deck,
        'deck-list': test_mtgjson_schema_deck_list,
        'keywords': test_mtgjson_schema_keywords,
        'meta': test_mtgjson_schema_meta,
        'price': test_mtgjson_schema_price,
        'set': test_mtgjson_schema_set,
        'set-list': test_mtgjson_schema_set_list,
    },
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@click.pass_context
def TestSchemaMTGJSON(ctx: click.Context):
    """Command group for performing MTGJSON schema tests."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(test_mtgjson_schema_all)
    pass


@click.group(
    commands={
        '.': test_scryfall_schema_all,
        'card': test_scryfall_schema_card,
        'ruling': test_scryfall_schema_ruling,
        'set': test_scryfall_schema_set
    },
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@click.pass_context
def TestSchemaScryfall(ctx: click.Context):
    """Command group for performing Scryfall schema tests."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(test_scryfall_schema_all)
    pass


@click.group(
    commands={
        '.': test_vectors_schema_all,
        'manifest': test_vectors_schema_manifest
    },
    invoke_without_command=True,
    context_settings={'ignore_unknown_options': True}
)
@click.pass_context
def TestSchemaVectors(ctx: click.Context):
    """Command group for performing MTG Vectors schema tests."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(test_vectors_schema_all)
    pass


@click.group(
    commands={
        '.': test_all_schema,
        'mtgjson': TestSchemaMTGJSON,
        'scryfall': TestSchemaScryfall,
        'vectors': TestSchemaVectors
    }
)
def TestSchema():
    """Command group for performing schema tests."""
    pass
