import unittest
from grouping import source_core, split_source_groups, source_group_bootstrap

class GroupingTests(unittest.TestCase):
    def row(self):
        return dict(resume_text='Objective: Build systems Skills: Python', education_text="['BSc'] ['CS'] ['School'] appended degree", experience_text="['Engineer'] appended tasks ['2010'] ['N/A']")
    def test_target_specific_appended_fields_do_not_change_core(self):
        a=self.row(); b=dict(a, resume_text=a['resume_text']+' SQL', education_text=a['education_text']+' another degree', experience_text=a['experience_text']+' tasks')
        self.assertEqual(source_core(a),source_core(b))
    def test_history_changes_core(self):
        a=self.row(); b=dict(a,experience_text=a['experience_text'].replace('2010','2011'))
        self.assertNotEqual(source_core(a),source_core(b))
    def test_incomplete_excluded(self):
        self.assertIsNone(source_core(dict(self.row(),experience_text="['Engineer']")))
    def test_no_group_crosses_split(self):
        keys={str(i):str(i//3) for i in range(60)}
        splits=split_source_groups(keys)
        groups=[{keys[c] for c in ids} for ids in splits.values()]
        self.assertFalse(groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
        self.assertEqual(set(keys),set(sum(splits.values(),[])))
    def test_bootstrap_weights_candidates_and_resamples_groups(self):
        result=source_group_bootstrap({'a':0.,'b':0.,'c':1.},{'a':'x','b':'x','c':'y'},repetitions=100)
        self.assertAlmostEqual(result['mean'],1/3)
        self.assertEqual(result['source_groups'],2)
if __name__=='__main__': unittest.main()
