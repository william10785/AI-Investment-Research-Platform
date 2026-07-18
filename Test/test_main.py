"""Tests for the ticker validation behavior in main.py."""

import unittest

from main import validate_ticker #used function

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


if __name__ == "__main__":
    unittest.main()
