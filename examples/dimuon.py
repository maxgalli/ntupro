from ntupro import setup_logger
from ntupro import dataset_from_files
from ntupro import Selection
from ntupro import Histogram
from ntupro import Unit
from ntupro import UnitManager
from ntupro import GraphManager
from ntupro import RunManager

import argparse
import ROOT



def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run dimuon Opendata example")

    parser.add_argument(
        "--local",
        required=False,
        default=True,
        type=bool,
        help="Run with a ROOT file found in ./data"
        )

    parser.add_argument(
        "--log-level",
        required=False,
        default="INFO",
        type=str,
        help="Level of information printed by the logger"
        )

    parser.add_argument(
        "--log-file",
        required=False,
        type=str,
        help="Name of the log file"
        )

    return parser.parse_args()


def main(args):
    local = args.local
    log_level = args.log_level
    log_file = args.log_file

    logger = setup_logger(log_level, log_file)

    file_name = "Run2012BC_DoubleMuParked_Muons.root"
    if local:
        path = "./data/"
    else:
        path = "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/"
    full_file_name = path + file_name
    tree_name = "Events"
    output_file = "./output/dimuon.root"

    dataset = dataset_from_files('DoubleMuParked', 'Events', [full_file_name])

    selection = Selection(
        'Muons', 
        [("nMuon == 2", "Events with exactly two muons"), 
        ("Muon_charge[0] != Muon_charge[1]", "Muons with opposite charge")]
            )

    ROOT.gInterpreter.Declare(
    """
    using namespace ROOT::VecOps;
    float computeInvariantMass(RVec<float>& pt, RVec<float>& eta, RVec<float>& phi, RVec<float>& mass) {
        ROOT::Math::PtEtaPhiMVector m1(pt[0], eta[0], phi[0], mass[0]);
        ROOT::Math::PtEtaPhiMVector m2(pt[1], eta[1], phi[1], mass[1]);
        return (m1 + m2).mass();
    }
    """)

    histo = Histogram(
        'Dimuon_mass', 
        'Dimuon_mass', 
        (30000, 0.25, 300.0), 
        "computeInvariantMass(Muon_pt, Muon_eta, Muon_phi, Muon_mass)"
        )

    unit = Unit(dataset, [selection], [histo])
    um = UnitManager()
    um.book([unit])

    g_manager = GraphManager(um.booked_units)
    g_manager.optimize(2)
    graphs = g_manager.graphs

    r_manager = RunManager(graphs)
    r_manager.run_locally(output_file)



if __name__ == "__main__":
    args = parse_arguments()
    main(args)