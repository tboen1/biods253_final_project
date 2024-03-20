import numpy as np

import unittest
from utils import (load_words,
                   guess2color,
                   get_color_distribution,
                   get_expected_information)

class wordle_tests(unittest.TestCase):
    def test_words_list(self):
        self.assertTrue("crane" in load_words("wordle_words.txt")) 

    def test_color_simple(self):
        self.assertEqual(guess2color("crane", "grace"), "XGGYG")
    
    def test_color_duplicate(self):
        self.assertEqual(guess2color("child", "couch"), "GXXXY")

    def test_color_distribution(self):
        valid_words = load_words("data/wordle_words.txt")
        dist = get_color_distribution(guess = "colly",
                                  possible_answers = valid_words,
                                  show_progress = False)

        self.assertTrue("clamp" in dist["GXYXX"])

    def test_expected_information(self):
        valid_words = load_words("wordle_words.txt")
        guesses = {"crane"}
        guess_information = get_expected_information(guesses = guesses, 
                                             answers = valid_words,
                                             show_progress = False)
        self.assertTrue(np.linalg.norm(guess_information["crane"]
                                       - 5.74) < 0.01)
        
        
if __name__ == "__main__":
    unittest.main()
