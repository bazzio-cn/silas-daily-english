import unittest

from silas_daily_english.themes import select_theme


THEMES = [
    {"key": "school_comedy", "weight": 40},
    {"key": "family_life", "weight": 20},
    {"key": "small_adventure", "weight": 20},
]


class ThemeTest(unittest.TestCase):
    def test_select_theme_avoids_recent_theme_when_options_remain(self):
        selected = select_theme(THEMES, ["school_comedy", "family_life"])
        self.assertEqual(selected["key"], "small_adventure")

    def test_select_theme_avoids_immediate_repeat_after_all_themes_seen(self):
        for _ in range(20):
            selected = select_theme(
                THEMES,
                ["school_comedy", "family_life", "small_adventure"],
            )
            self.assertNotEqual(selected["key"], "school_comedy")


if __name__ == "__main__":
    unittest.main()
