import unittest
from run import simulate


class ModelTests(unittest.TestCase):
    def test_exact_no_fault_timeline(self):
        # work, work, save, work, work, save -> four delivered units.
        r = simulate(6, 2, 1, [])
        self.assertEqual(r['deliveredCorrectWorkTicks'], 4)
        self.assertEqual(r['checkpointOverheadTicks'], 2)
        self.assertEqual(r['lostWorkTicks'], 0)

    def test_failure_at_commit_boundary(self):
        # work, work, failure, work, work, save: first two units are lost.
        r = simulate(6, 2, 1, [3])
        self.assertEqual(r['deliveredCorrectWorkTicks'], 2)
        self.assertEqual(r['lostWorkTicks'], 2)
        self.assertEqual(r['recoveryTicks'], 1)

    def test_uncommitted_work_is_not_delivery(self):
        r = simulate(2, 2, 1, [])
        self.assertEqual(r['deliveredCorrectWorkTicks'], 0)
        self.assertEqual(r['uncommittedWorkTicks'], 2)

    def test_committed_work_survives_failure(self):
        r = simulate(4, 2, 1, [4])
        self.assertEqual(r['deliveredCorrectWorkTicks'], 2)
        self.assertEqual(r['lostWorkTicks'], 0)

    def test_mid_checkpoint_failure(self):
        r = simulate(4, 2, 2, [4])
        self.assertEqual(r['deliveredCorrectWorkTicks'], 0)
        self.assertEqual(r['checkpointOverheadTicks'], 1)
        self.assertEqual(r['lostWorkTicks'], 2)

    def test_invalid_inputs_fail(self):
        for args in [(5, 0, 1, []), (5, 2, 1, [6]), (5, 2, 1, [2, 2]),
                     (5, True, 1, []), (5, 2, 1, [1.5])]:
            with self.assertRaises(ValueError):
                simulate(*args)


if __name__ == '__main__':
    unittest.main()
