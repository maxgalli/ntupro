import unittest

from ntupro.booking import Ntuple, Dataset, Cut, Weight


class TestBookingMethods(unittest.TestCase):
    """ Test main classes and methods inside
    the booking submodule of ntuple_processor
    """
    def setUp(self):
        self.nt = Ntuple('path', 'directory')
        self.nt_friend = Ntuple('friend_path', 'friend_directory')
        self.ds = Dataset('ds', [self.nt])
        self.ct = Cut('cut_exp', 'cut_name')
        self.wh = Weight('weight_exp', 'weight_name')

    def test_ntuples(self):
        """
        Ntuple objects equal if have same path and directory
        """
        same_nt = Ntuple(self.nt.path, self.nt.directory)
        other_nt = Ntuple('other_path', self.nt.directory)
        self.assertEqual(self.nt, same_nt)
        self.assertNotEqual(self.nt, other_nt)

    def test_ntuple_with_friends(self):
        """
        Friends don't influence the comparison
        """
        same_nt = Ntuple(self.nt.path, self.nt.directory, [self.nt_friend])
        other_nt = Ntuple('other_path', self.nt.directory, [self.nt_friend])
        self.assertEqual(self.nt, same_nt)
        self.assertNotEqual(same_nt, other_nt)

    def test_datasets(self):
        """
        Dataset objects equal if have same name and list of ntuples
        """
        same_ds = Dataset(self.ds.name, [self.nt])
        other_ds = Dataset(self.ds.name, [self.nt_friend])
        self.assertEqual(self.ds, same_ds)
        self.assertNotEqual(self.ds, other_ds)

    def test_cuts_weights(self):
        """
        Cuts and Weights equal if same name and expression
        """
        same_ct = Cut(self.ct.expression, self.ct.name)
        other_ct = Cut(self.ct.expression, 'other_cut_name')
        same_wh = Weight(self.wh.expression, self.wh.name)
        other_wh = Weight(self.wh.expression, 'other_weight_name')
        self.assertEqual(self.ct, same_ct)
        self.assertNotEqual(self.ct, other_ct)
        self.assertEqual(self.wh, same_wh)
        self.assertNotEqual(self.wh, other_wh)


if __name__ == '__main__':
    unittest.main()
