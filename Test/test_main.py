"""Tests for the ticker validation and company-profile extraction behavior."""

import unittest

from main import extract_company_essential_data, validate_ticker


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


if __name__ == "__main__":
    unittest.main()
