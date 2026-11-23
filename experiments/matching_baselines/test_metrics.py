import itertools
import unittest
from metrics import ndcg, expected_random, bootstrap

class MetricsTests(unittest.TestCase):
    def test_perfect_and_reverse(self):
        self.assertAlmostEqual(ndcg([3,2,0],[3,2,0],5),1)
        self.assertLess(ndcg([3,2,0],[0,2,3],5),1)
    def test_random_is_average_over_uniform_permutations(self):
        labels=[0,.2,.7,1]
        for k in (1,3,5):
            expected=sum(ndcg(labels,p,k) for p in itertools.permutations(range(4)))/24
            self.assertAlmostEqual(expected_random(labels,k),expected)
    def test_tied_scores_average_positions_across_cutoff(self):
        self.assertAlmostEqual(ndcg([1,.4,0],[2,1,1],2),(ndcg([1,.4,0],[2,1,0],2)+ndcg([1,.4,0],[2,0,1],2))/2)
    def test_zero_ideal_and_bootstrap(self):
        self.assertIsNone(ndcg([0,0],[1,2],5))
        self.assertEqual(bootstrap([.5]*4)['ci95'],[.5,.5])
        self.assertIsNone(bootstrap([None])['mean'])
if __name__=='__main__': unittest.main()
