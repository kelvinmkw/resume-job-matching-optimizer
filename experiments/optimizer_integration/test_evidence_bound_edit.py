import unittest
from evidence_bound_edit import validate_edit, validate_json

class EvidenceBoundEditTests(unittest.TestCase):
    def setUp(self):
        self.source='Experienced analyst seeking a role in data science.'
        self.original='Objective: '+self.source+' Skills: SQL'
        self.start=self.original.index(self.source)
        self.end=self.start+len(self.source)
    def payload(self,replacement=None,**overrides):
        data={'source':self.source,'replacement':replacement or self.source,'evidence_quote':self.source}
        data.update(overrides); return data
    def test_supported_surface_edit_is_pending_review(self):
        changed=self.source.replace('seeking','looking')
        result=validate_edit(self.original,self.start,self.end,self.payload(changed))
        self.assertEqual(result.status,'accepted_pending_manual_review')
        self.assertEqual(result.effective_text[self.end:],self.original[self.end:])
    def test_changed_number_rejected_and_original_retained(self):
        source='Analyst with 3 years of experience in SQL and Python.'
        original='Objective: '+source; start=11
        result=validate_edit(original,start,start+len(source),{'source':source,'replacement':source.replace('3','8'),'evidence_quote':source})
        self.assertEqual(result.effective_text,original)
        self.assertIn('numeric_claim_changed',result.violations)
    def test_new_skill_rejected(self):
        changed=self.source.replace('data science','data science and Kubernetes')
        result=validate_edit(self.original,self.start,self.end,self.payload(changed))
        self.assertIn('content_words_changed',result.violations)
    def test_negation_change_rejected(self):
        source='Analyst with experience in SQL and Python.'
        original='Objective: '+source
        result=validate_edit(original,11,11+len(source),{'source':source,'replacement':'Analyst without experience in SQL and Python.','evidence_quote':source})
        self.assertIn('logical_qualifiers_changed',result.violations)
    def test_bad_evidence_quote_rejected(self):
        result=validate_edit(self.original,self.start,self.end,self.payload(overrides={'evidence_quote':'different'}))
        self.assertIn('source_or_evidence_mismatch',result.violations)
    def test_invalid_json_keeps_original(self):
        result=validate_json('{bad',self.original,self.start,self.end)
        self.assertEqual(result.status,'rejected_response')
        self.assertEqual(result.effective_text,self.original)
    def test_unchanged_is_not_success(self):
        self.assertEqual(validate_edit(self.original,self.start,self.end,self.payload()).status,'unchanged')
if __name__=='__main__': unittest.main()
