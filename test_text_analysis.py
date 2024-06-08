import unittest
from text_analysis import TextAnalyzer

class TestTextAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_analyze_phishing(self):
        message = "You have won a $1000 gift card. Click here to claim your prize!"
        label, score = self.analyzer.analyze(message)
        self.assertEqual(label, 'phishing')
        self.assertGreater(score, 0.5)

    def test_analyze_benign(self):
        message = "Let's schedule a meeting for next week to discuss the project updates."
        label, score = self.analyzer.analyze(message)
        self.assertEqual(label, 'benign')
        self.assertGreater(score, 0.5)

if __name__ == '__main__':
    unittest.main()
