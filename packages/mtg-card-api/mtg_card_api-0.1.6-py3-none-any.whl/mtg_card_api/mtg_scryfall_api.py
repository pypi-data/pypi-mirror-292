"""
Entrypoint for running card requests
"""

from rest_client_micro import Response as R
from rest_client_micro import BaseRESTAPI, VERSION_STRING

from . import _utils as Utils


class ScryfallAPI(BaseRESTAPI):
    """
    Entrypoint to run requests against scryfall API
    """

    def __init__(self,
                 config_dir: str = None,
                 cache_dir: str = None,
                 cache_refresh_mins: int = 1440,
                 force_cache: bool = False,
                 use_cache: bool = True) -> None:

        app_name: str = 'MTGScryfallAPI'
        root_endpoint: str = 'https://api.scryfall.com/'
        basic_auth = None
        user_agent: str = (
            f'MTG-Card-API/'
            f'{VERSION_STRING}'
            f'(https://github.com/samuelshiels/MTG-Card-API)'
        )
        sleep_ms: int = 100
        cache_timeout_mins = cache_refresh_mins
        super().__init__(app_name, root_endpoint, user_agent, sleep_ms, basic_auth,
                         config_dir, cache_dir, cache_timeout_mins, force_cache, use_cache)

    def get_card_by_name(self, card_name: str) -> R:
        """Searches Scryfall by the exact name

        Args:
            card_name (str): Exact string oracle english name of a card, case insensitive

        Returns:
            R: Full card object https://scryfall.com/docs/api/cards
        """
        return self._run_get(
            'cards/named',
            {
                'exact': card_name
            },
            Utils.encodeMD5(card_name),
            'cache/cards')

    def get_card_variants(self, oracle_id: str) -> R:
        """Searches Scryfall by the oracle to find all variants of a card

        Args:
            card_name (str): Exact string oracle id of a card

        Returns:
            R: Full search result
        """
        return self._run_get(
            'cards/search',
            {
                'q': f'oracle_id={oracle_id}',
                'unique': 'prints'
            },
            oracle_id,
            'cache/variants'
        )
