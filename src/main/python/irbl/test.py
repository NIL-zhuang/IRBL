import unittest
from simi_calculator import *
from weight_definer import *


class WeightDefinerTestCase(unittest.TestCase):
    def test_get_wordcount(self):
        expected = {'a': 1, 'b': 2, 'c': 3}
        words = ['a', 'c', 'b', 'c', 'b', 'c']
        result = get_word_count(words)
        for word in expected:
            self.assertEqual(expected[word], result[word])

    def test_get_total_words(self):
        expected = 6
        word_count = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(expected, sum(word_count.values()))

    # 下面的测试用例在迭代二中已经过时
    # def test_calculate_tfidf(self):
    #     all_word_count = {'a': 2, 'b': 2, 'c': 2, 'd': 2, 'e': 2, 'f': 1}
    #     each_file_word_count = [
    #         {'a': 2, 'b': 1, 'c': 1, 'd': 1, 'e': 1},
    #         {'a': 1, 'c': 1, 'e': 1, 'f': 1},
    #         {'b': 1, 'd': 1}
    #     ]
    #     result = calculate_tfidf([], all_word_count, each_file_word_count)
    #     expected = [
    #         {'a': 2 / 6 * math.log(3 / 2), 'b': 1 / 6 * math.log(3 / 2), 'c': 1 / 6 * math.log(3 / 2),
    #          'd': 1 / 6 * math.log(3 / 2), 'e': 1 / 6 * math.log(3 / 2), 'f': 0},
    #         {'a': 1 / 4 * math.log(3 / 2), 'b': 0, 'c': 1 / 4 * math.log(3 / 2), 'd': 0, 'e': 1 / 4 * math.log(3 / 2),
    #          'f': 1 / 4 * math.log(3 / 1)},
    #         {'a': 0, 'b': 1 / 2 * math.log(3 / 2), 'c': 0, 'd': 1 / 2 * math.log(3 / 2), 'e': 0, 'f': 0}
    #     ]
    #     for i in range(3):
    #         for w in result[i]:
    #             self.assertAlmostEqual(result[i][w], expected[i][w])

    def test_get_cos_sim(self):
        a = [1, 1, 1, 1]
        b = [1, 1, 1, 1]
        sim = get_cos_sim(a, b)
        self.assertEqual(1.0000, sim)
        b = [-1, -1, -1, -1]
        sim = get_cos_sim(a, b)
        self.assertEqual(-1.0000, sim)


if __name__ == '__main__':
    unittest.main()
