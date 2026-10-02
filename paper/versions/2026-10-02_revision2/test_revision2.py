"""Focused metric edge cases and checks of completed, real-data review outputs."""
import csv
import json
import unittest
from pathlib import Path
import rescore as r

def csvrows(name):
    with (r.OUT/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

class ScoringReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.officials=r.official()

    def test_categorical_dataset_difference(self):
        for answer in ('yes','no','noanswer'):
            prediction=answer+' indeed'
            self.assertEqual(r.canonical(prediction,[answer],r.H,self.officials),(0.,0.))
            self.assertAlmostEqual(r.canonical(prediction,[answer],r.M,self.officials)[1],2/3)
            self.assertAlmostEqual(r.legacy(prediction,[answer],'4H',r.H)[1],2/3)
            self.assertEqual(r.legacy(prediction,[answer],'4E',r.H)[1],0.)

    def test_empty_and_normalization(self):
        self.assertEqual(r.canonical('The!',['a'],r.H,self.officials),(1.,0.))
        self.assertEqual(r.canonical('The!',['a'],r.M,self.officials),(1.,1.))
        self.assertEqual(r.legacy('The!',['a'],'4E',r.H),(1.,0.))
        self.assertEqual(r.legacy('The!',['a'],'4G',r.H),(1.,1.))
        for dataset in (r.H,r.M):
            self.assertEqual(r.canonical('The BLUE, bird!',['blue bird'],dataset,self.officials),(1.,1.))

    def test_aliases(self):
        self.assertEqual(r.canonical('NYC',['New York City','NYC'],r.M,self.officials),(1.,1.))
        with self.assertRaises(AssertionError):r.canonical('NYC',['New York City','NYC'],r.H,self.officials)

    def test_completed_prediction_reconstruction(self):
        status=json.loads((r.OUT/'RECONSTRUCTION_STATUS.json').read_text())
        self.assertEqual(sum(s['predictions'] for s in status.values()),74750)
        self.assertEqual(sum(s['affected_predictions'] for s in status.values()),17)
        self.assertEqual(sum(s['predictions'] for k,s in status.items() if k!='5A_development'),53500)
        self.assertTrue(all(s['legacy_per_query_means_and_intervals']=='RECONSTRUCTED' for s in status.values()))
        changed=csvrows('AFFECTED_PREDICTIONS.csv')
        self.assertEqual(len(changed),17)
        self.assertEqual(len({x['query_id'] for x in changed}),1)
        for row in csvrows('PAIRED_COMPARISONS.csv'):
            self.assertAlmostEqual(float(row['delta_shift']),0.,places=12)
            for field in ('delta','lower','upper'):
                if row['legacy_'+field]:
                    self.assertAlmostEqual(float(row['legacy_'+field]),float(row['canonical_'+field]),places=12)

    def test_actual_visible_content(self):
        data=csvrows('PLACEMENT_QUERY_CHECKS.csv')
        self.assertEqual(len(data),2500)
        for row in data:
            for key in ('membership_equal','visible_content_equal','protected_prompt_verified','unprotected_prompt_verified'):
                self.assertEqual(row[key],'True')
            self.assertEqual(row['protected_visible_digest'],row['unprotected_visible_digest'])
            self.assertEqual(row['protected_tokens'],row['unprotected_tokens'])
            self.assertEqual(row['protected_dropped'],'0')
            self.assertEqual(row['unprotected_dropped'],'0')
            self.assertEqual(row['protected_partial'],'False')
            self.assertEqual(row['unprotected_partial'],'False')

    def test_placement_set_identity(self):
        dense=list(range(20))
        for m in range(5):
            ins=list(range(20,20+m))
            protected=(dense[:10]+ins+dense[10:])[:20]
            unprotected=(ins+dense)[:20]
            self.assertEqual(set(protected),set(unprotected))
            self.assertEqual(set(protected),set(ins+dense[:20-m]))

if __name__=='__main__':unittest.main(verbosity=2)
