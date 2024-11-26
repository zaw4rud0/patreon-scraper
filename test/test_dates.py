import unittest
from datetime import datetime, timedelta
from src.scraper import parse_post_date


class TestParsePostDate(unittest.TestCase):
    def setUp(self):
        """Set up today's date for relative time tests."""
        self.today = datetime.now()

    def test_hours_ago(self):
        """Test parsing relative time in hours."""
        raw_date = "6 hours ago"
        expected_date = (self.today - timedelta(hours=6)).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)

        raw_date = "21 hours ago"
        expected_date = (self.today - timedelta(hours=21)).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)

    def test_yesterday(self):
        """Test parsing 'yesterday'."""
        raw_date = "Yesterday"
        expected_date = (self.today - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)

    def test_days_ago(self):
        """Test parsing 'x days ago'."""
        raw_date = "3 days ago"
        expected_date = (self.today - timedelta(days=3)).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)

    def test_specific_dates_recent_month(self):
        """Test parsing specific dates in the current or recent month."""
        raw_date = "November 19"
        expected_date = self.today.replace(month=11, day=19).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)

        raw_date = "November 11"
        expected_date = self.today.replace(month=11, day=11).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)

    def test_specific_dates_older_month(self):
        """Test parsing specific dates from older months."""
        raw_date = "October 31"
        expected_date = self.today.replace(year=self.today.year - 1 if self.today.month < 10 else self.today.year,
                                           month=10, day=31).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)

        raw_date = "September 30"
        expected_date = self.today.replace(year=self.today.year - 1 if self.today.month < 9 else self.today.year,
                                           month=9, day=30).strftime("%Y-%m-%d")
        self.assertEqual(parse_post_date(raw_date), expected_date)


if __name__ == "__main__":
    unittest.main()
