import unittest
import subprocess
import os
import ROOT
import ntupro


class TestFullAnalyses(unittest.TestCase):
    """ Test full HEP analyses
    """
    def setUp(self):
        '''
        self.file_name = 'Run2012BC_DoubleMuParked_Muons.root'
        self.file_exists = os.path.isfile('./tests/samples/' + self.file_name)
        if not self.file_exists:
            remote_file_name = 'root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/' + self.file_name
            subprocess.run(['xrdcp', remote_file_name, './tests/samples/'])
            self.file_exists = os.path.isfile('./tests/samples/' + self.file_name)
            self.error_msg = "Could not find {}".format(self.file_name)
        '''
        self.file_name = 'Run2012BC_DoubleMuParked_Muons.root'
        self.path_to_file = './tests/samples/'
        self.error_msg = "Could not find {}".format(self.file_name)
        try:
            remote_file_name = 'root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/' + self.file_name
            subprocess.run(['xrdcp', remote_file_name, self.path_to_file])
        except:
            pass
        self.file_exists = os.path.isfile(self.path_to_file + self.file_name)

    def test_full_dimuon(self):
        """ CMS di-muon spectrum analysis from http://opendata.cern.ch/record/12342
        """
        if not self.file_exists:
            self.skipTest(self.error_msg)

        with self.subTest('Dataset creation'):
            self.dataset = ntupro.dataset_from_files('DoubleMuParked', 'Events', [self.path_to_file + self.file_name])
            self.assertIsNotNone(self.dataset)

        with self.subTest('Selection creation'):
            self.selection = ntupro.Selection('Muons', [("nMuon == 2", "Events with exactly two muons"), ("Muon_charge[0] != Muon_charge[1]", "Muons with opposite charge")])
            self.assertIsNotNone(self.selection)

        with self.subTest('Histogram Action creation'):
            ROOT.gInterpreter.Declare(
            """
            using namespace ROOT::VecOps;
            float computeInvariantMass(RVec<float>& pt, RVec<float>& eta, RVec<float>& phi, RVec<float>& mass) {
                ROOT::Math::PtEtaPhiMVector m1(pt[0], eta[0], phi[0], mass[0]);
                ROOT::Math::PtEtaPhiMVector m2(pt[1], eta[1], phi[1], mass[1]);
                return (m1 + m2).mass();
            }
            """)
            self.histo = ntupro.Histogram('Dimuon_mass', 'Dimuon_mass', (30000, 0.25, 300.0), "computeInvariantMass(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")
            self.assertIsNotNone(self.histo)

        with self.subTest('Units creation and booking'):
            self.unit = ntupro.Unit(self.dataset, [self.selection], [self.histo])
            self.um = ntupro.UnitManager()
            self.um.book([self.unit])
            self.assertIsNotNone(self.unit)
            self.assertIsNotNone(self.um)

        with self.subTest('Graphs handling'):
            self.g_manager = ntupro.GraphManager(self.um.booked_units)
            self.g_manager.optimize(2)
            self.graphs = self.g_manager.graphs
            self.assertIsNotNone(self.g_manager)
            self.assertIsNotNone(self.graphs)

        with self.subTest('Run event loop'):
            output = './tests/output_files/output_di_muon.root'
            self.r_manager = ntupro.RunManager(self.graphs)
            self.assertIsNotNone(self.r_manager)
            self.r_manager.run_locally(output)


if __name__ == '__main__':
    unittest.main()
