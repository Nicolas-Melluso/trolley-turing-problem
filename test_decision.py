import unittest
from decision import decide


class DecisionTests(unittest.TestCase):
    def test_classic(self):
        result = decide(5, 1)
        self.assertEqual((result["action"], result["victims"], result["safe"]), ("divert", 1, 5))

    def test_same_facts_different_rules(self):
        self.assertEqual(decide(1, 5, "minimize")["action"], "keep")
        self.assertEqual(decide(1, 5, "protect_main")["action"], "divert")
        self.assertEqual(decide(5, 1, "nonintervention")["action"], "keep")

    def test_ties_and_empty_tracks(self):
        for count in range(13):
            self.assertEqual(decide(count, count)["action"], "keep")
        self.assertEqual(decide(5, 0)["victims"], 0)
        self.assertEqual(decide(0, 5, "protect_main")["action"], "keep")

    def test_minimum_and_conservation(self):
        for main in range(13):
            for branch in range(13):
                result = decide(main, branch)
                self.assertEqual(result["victims"], min(main, branch))
                self.assertEqual(result["safe"] + result["victims"], main + branch)

    def test_invalid_input(self):
        for value in (-1, 13, 1.5, "5", True, None):
            with self.assertRaises(ValueError):
                decide(value, 1)
            with self.assertRaises(ValueError):
                decide(1, value)
        with self.assertRaises(ValueError):
            decide(5, 1, "unknown")


if __name__ == "__main__":
    unittest.main()
