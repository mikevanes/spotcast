"""Module to test the async_category_playlists"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock, patch
from time import time

from custom_components.spotcast.spotify.account import (
    SpotifyAccount,
    HomeAssistant,
    OAuth2Session,
    InternalSession,
)


class TestPlaylistRetrieval(IsolatedAsyncioTestCase):

    @patch.object(SpotifyAccount, "async_ensure_tokens_valid")
    @patch.object(SpotifyAccount, "_async_pager")
    async def asyncSetUp(self, mock_pager: AsyncMock, mock_ensure: AsyncMock):

        self.mocks = {
            "hass": MagicMock(spec=HomeAssistant),
            "external": MagicMock(spec=OAuth2Session),
            "internal": MagicMock(spec=InternalSession),
            "pager": mock_pager,
        }

        self.mocks["pager"].return_value = ["foo", "bar", "baz"]

        self.account = SpotifyAccount(
            entry_id="12345",
            hass=self.mocks["hass"],
            external_session=self.mocks["external"],
            internal_session=self.mocks["internal"],
        )
        self.account._datasets["profile"] = MagicMock()
        self.account._datasets["profile"].expires_at = time() + 9999
        self.account._datasets["profile"].data = {
            "country": "CA"
        }

        self.result = await self.account.async_category_playlists("12345")

    def test_pager_called_with_proper_arguments(self):
        try:
            self.mocks["pager"].assert_called_with(
                self.account._spotify.category_playlists,
                prepends=["12345", "CA"],
                sub_layer="playlists",
                max_items=None,
            )
        except AssertionError:
            self.fail()

    def test_correct_result_returned(self):
        self.assertEqual(self.result, ["foo", "bar", "baz"])
