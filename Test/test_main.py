"""Tests for the ticker validation and company-profile extraction behavior."""

import unittest
from unittest.mock import Mock, patch

import requests

from main import extract_company_essential_data, fetch_company_profile, validate_ticker


class ValidateTickerTests(unittest.TestCase):
    """Verify the accepted ticker format without checking market existence."""

    def assert_tickers_valid(self, tickers: list[str]) -> None:
        for ticker in tickers:
            with self.subTest(ticker=ticker):
                self.assertIs(validate_ticker(ticker), True)

    def assert_tickers_invalid(self, tickers: list[str]) -> None:
        for ticker in tickers:
            with self.subTest(ticker=ticker):
                self.assertIs(validate_ticker(ticker), False)

    def test_accepts_standard_tickers(self) -> None:
        self.assert_tickers_valid(["A", "AAPL", "MSFT", "NVDA", "ABC1"])

    def test_accepts_internal_separators(self) -> None:
        self.assert_tickers_valid(["BRK.B", "BRK-B", "A.B-C"])

    def test_accepts_maximum_length(self) -> None:
        self.assertIs(validate_ticker("ABCDEFGHIJ"), True)

    def test_rejects_empty_and_whitespace_only_input(self) -> None:
        self.assert_tickers_invalid(["", " ", "   ", "\t", "\n"])

    def test_rejects_tickers_longer_than_ten_characters(self) -> None:
        self.assert_tickers_invalid(["ABCDEFGHIJK", "12345678901"])

    def test_rejects_unsupported_characters(self) -> None:
        self.assert_tickers_invalid(
            ["$", "$TSLA", "AAPL!", "ABC_", "AA PL", "AAPL/WS", "AAPL@"]
        )

    def test_rejects_leading_separators(self) -> None:
        self.assert_tickers_invalid([".AAPL", "-AAPL"])

    def test_rejects_trailing_separators(self) -> None:
        self.assert_tickers_invalid(["AAPL.", "AAPL-"])

    def test_rejects_consecutive_separators(self) -> None:
        self.assert_tickers_invalid(["BRK..B", "BRK--B", "BRK.-B", "BRK-.B"])

    def test_always_returns_a_boolean(self) -> None:
        for ticker in ["AAPL", "", "$TSLA", "BRK.B"]:
            with self.subTest(ticker=ticker):
                self.assertIsInstance(validate_ticker(ticker), bool)


class ExtractCompanyEssentialDataTests(unittest.TestCase):
    """Verify that Finnhub data is normalized to the four-field app format."""

    def setUp(self) -> None:
        self.raw_profile: dict[str, object] = {
            "ticker": "AAPL",
            "name": "Apple Inc",
            "exchange": "NASDAQ NMS - GLOBAL MARKET",
            "finnhubIndustry": "Technology",
            "country": "US",
            "currency": "USD",
            "marketCapitalization": 4_901_758.48,
            "weburl": "https://www.apple.com/",
        }

    def test_extracts_and_renames_the_four_essential_fields(self) -> None:
        result = extract_company_essential_data(self.raw_profile)

        self.assertEqual(
            result,
            {
                "ticker": "AAPL",
                "company_name": "Apple Inc",
                "exchange": "NASDAQ NMS - GLOBAL MARKET",
                "industry": "Technology",
            },
        )

    def test_returns_none_for_an_empty_profile(self) -> None:
        self.assertIsNone(extract_company_essential_data({}))

    def test_uses_not_available_when_industry_is_missing(self) -> None:
        raw_profile = self.raw_profile.copy()
        raw_profile.pop("finnhubIndustry")

        result = extract_company_essential_data(raw_profile)

        self.assertIsNotNone(result)
        self.assertEqual(result["industry"], "Not available")

    def test_ignores_fields_outside_the_app_format(self) -> None:
        result = extract_company_essential_data(self.raw_profile)

        self.assertIsNotNone(result)
        self.assertEqual(
            set(result), {"ticker", "company_name", "exchange", "industry"}
        )

    def test_does_not_modify_the_raw_profile(self) -> None:
        original_profile = self.raw_profile.copy()

        extract_company_essential_data(self.raw_profile)

        self.assertEqual(self.raw_profile, original_profile)

    def test_uses_defaults_when_profile_fields_are_missing(self) -> None:
        result = extract_company_essential_data({"country": "US"})

        self.assertEqual(
            result,
            {
                "ticker": "Not available",
                "company_name": "Not available",
                "exchange": "Not available",
                "industry": "Not available",
            },
        )


class FetchCompanyProfileTests(unittest.TestCase):
    """Verify API behavior without making real network requests."""

    @patch("main.requests.get")
    def test_returns_decoded_profile_after_successful_request(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(
            status_code=200,
            text='{"ticker": "AAPL", "name": "Apple Inc"}',
        )

        result = fetch_company_profile("AAPL", "test-api-key")

        self.assertEqual(result, {"ticker": "AAPL", "name": "Apple Inc"})
        mock_get.assert_called_once_with(
            "https://finnhub.io/api/v1/stock/profile2",
            params={"symbol": "AAPL"},
            headers={"X-Finnhub-Token": "test-api-key"},
            timeout=10,
        )

    @patch("main.requests.get")
    @patch("builtins.print")
    def test_rejects_missing_api_key(self, mock_print: Mock, mock_get: Mock) -> None:
        result = fetch_company_profile("AAPL", "")

        self.assertIsNone(result)
        mock_get.assert_not_called()
        mock_print.assert_called_once_with("Missing API Key")

    @patch("main.requests.get", side_effect=requests.exceptions.Timeout)
    @patch("builtins.print")
    def test_handles_timeout(self, mock_print: Mock, mock_get: Mock) -> None:
        result = fetch_company_profile("AAPL", "test-api-key")

        self.assertIsNone(result)
        mock_print.assert_called_once_with("The request timed out.")

    @patch("main.requests.get", side_effect=requests.exceptions.ConnectionError)
    @patch("builtins.print")
    def test_handles_connection_failure(self, mock_print: Mock, mock_get: Mock) -> None:
        result = fetch_company_profile("AAPL", "test-api-key")

        self.assertIsNone(result)
        mock_print.assert_called_once_with("Invalid Connection")

    @patch("main.requests.get", side_effect=requests.exceptions.RequestException)
    @patch("builtins.print")
    def test_handles_other_request_errors(self, mock_print: Mock, mock_get: Mock) -> None:
        result = fetch_company_profile("AAPL", "test-api-key")

        self.assertIsNone(result)
        mock_print.assert_called_once_with("External Error")

    @patch("main.requests.get")
    @patch("builtins.print")
    def test_handles_error_status_codes(self, mock_print: Mock, mock_get: Mock) -> None:
        cases = [
            (400, "Missing or Invalid Paramters in API Request"),
            (401, "Missing or Invalid API Key"),
            (403, "Insufficient permission"),
            (429, "Rate Limit Exceeded"),
            (502, "Server side error."),
        ]

        for status_code, expected_message in cases:
            with self.subTest(status_code=status_code):
                mock_get.return_value = Mock(status_code=status_code, text="")

                result = fetch_company_profile("AAPL", "test-api-key")

                self.assertIsNone(result)
                mock_print.assert_called_once_with(expected_message)
                mock_get.reset_mock()
                mock_print.reset_mock()

    @patch("main.requests.get")
    @patch("builtins.print")
    def test_handles_ticker_that_does_not_exist(
        self, mock_print: Mock, mock_get: Mock
    ) -> None:
        mock_get.return_value = Mock(status_code=200, text="{}")

        result = fetch_company_profile("ZZZZZZ", "test-api-key")

        self.assertIsNone(result)
        mock_print.assert_called_once_with("Ticker does not exist")


if __name__ == "__main__":
    unittest.main()
