from .utils import Count
from .utils import Histogram
from .utils import RDataFrameCutWeight

from ROOT import RDataFrame
from ROOT import TFile
from ROOT import TChain
from ROOT import EnableImplicitMT
from ROOT.std import vector

import logging
logger = logging.getLogger(__name__)



class RunManager:
    """Convert the Graph-style language into PyROOT/RDataFrame
    language and schedule RDataFrame operations, like the
    following:
        Dataset()     -->   RDataFrame()
        Selection()   -->   Filter()
        Count()   -->   Sum()
        Histogram()   -->   Histo1D()

    Args:
        graphs (list): List of Graph objects that are converted
            node by node to RDataFrame operations

    Attributes:
        final_ptrs (list): List of TH1D objects resulting from a
            set of Filter operations performed on RDataFrames; on
            all them we need to perform a Write operation
    """
    def __init__(self, graphs,
            parallelize = False,
            nthreads = 0):
        self.final_ptrs = list()
        self.tchains = list()
        self.friend_tchains = list()
        self.parallelize = parallelize
        self.nthreads = nthreads
        for graph in graphs:
            self.__node_to_root(graph)

    def run_locally(self, of_name, update = False):
        """Save to file the histograms booked.

        Args:
            of_name (str): Name of the output .root
                file
        """
        logger.info('%%%%%%%%%% Start producing {} shapes'.format(len(self.final_ptrs)))
        logger.debug('%%%%%%%%%% Start producing {} shapes'.format(len(self.final_ptrs)))
        if update:
            root_file = TFile(of_name, 'UPDATE')
        else:
            root_file = TFile(of_name, 'RECREATE')
        for op in self.final_ptrs:
            op.Write()
        root_file.Close()

    def __node_to_root(self, node, rcw = None):
        if node.kind == 'dataset':
            logger.debug('%%%%%%%%%% __node_to_root, converting to ROOT language the following dataset node\n{}'.format(
                node))
            result = self.__rdf_from_dataset(
                node.unit_block)
        elif node.kind == 'selection':
            if len(node.children) > 1:
                logger.debug('%%%%%%%%%% __node_to_root, converting to ROOT language the following crossroad node\n{}'.format(
                    node))
            result = self.__cuts_and_weights_from_selection(
                rcw, node.unit_block)
        elif node.kind == 'action':
            logger.debug('%%%%%%%%%% __node_to_root, converting to ROOT language the following action node\n{}'.format(
                node))
            if isinstance(node.unit_block, Count):
                result = self.__sum_from_count(
                    rcw, node.unit_block)
            elif isinstance(node.unit_block, Histogram):
                result = self.__histo1d_from_histo(
                    rcw, node.unit_block)
        if node.children:
            for child in node.children:
                self.__node_to_root(child, result)
        else:
            self.final_ptrs.append(result)

    def __rdf_from_dataset(self, dataset):
        t_names = [ntuple.directory for ntuple in \
            dataset.ntuples]
        if len(set(t_names)) == 1:
            tree_name = t_names.pop()
        else:
            raise NameError(
                'Impossible to create RDataFrame with different tree names')
        chain = TChain(tree_name, tree_name)
        ftag_fchain = {}
        for ntuple in dataset.ntuples:
            chain.Add(ntuple.path)
            for friend in ntuple.friends:
                if friend.tag not in ftag_fchain.keys():
                    ftag_fchain[friend.tag] = TChain(friend.directory, friend.directory)
                ftag_fchain[friend.tag].Add(friend.path)
        for ch in ftag_fchain.values():
            chain.AddFriend(ch)
            # Keep friend chains alive
            self.friend_tchains.append(ch)
        if self.parallelize:
            EnableImplicitMT(self.nthreads)
        # Keep main chain alive
        self.tchains.append(chain)
        rdf = RDataFrame(chain)
        rcw = RDataFrameCutWeight(rdf)
        return rcw

    def __cuts_and_weights_from_selection(self, rcw, selection):
        l_cuts = [cut for cut in rcw.cuts]
        l_weights = [weight for weight in rcw.weights]
        for cut in selection.cuts:
            l_cuts.append(cut)
        for weight in selection.weights:
            l_weights.append(weight)
        l_rcw = RDataFrameCutWeight(rcw.frame, l_cuts, l_weights)
        return l_rcw

    def __sum_from_count(self, rdf, count):
        return rdf.Sum(count.variable)

    def __histo1d_from_histo(self, rcw, histogram):
        name = histogram.name
        nbins = histogram.binning.nbins
        edges = histogram.binning.edges
        var = histogram.variable

        # Create macro weight string from sub-weights applied
        # (saved earlier as rdf columns)
        weight_expression = '*'.join([weight.expression for weight in rcw.weights])

        # Create macro cut string from sub-cuts applied
        # (saved earlier as rdf columns)
        cut_expression = ' && '.join([cut.expression for cut in rcw.cuts])
        if cut_expression:
            rcw.frame = rcw.frame.Filter(cut_expression)

        # Create std::vector with the histogram edges
        l_edges = vector['double']()
        for edge in edges:
            l_edges.push_back(edge)


        if not weight_expression:
            logger.debug('%%%%%%%%%% Attaching histogram called {}'.format(name))
            histo = rcw.frame.Histo1D((
                    name, name, nbins, l_edges.data()),
                    var)
        else:
            weight_name = name.replace('#', '_')
            weight_name = weight_name.replace('-', '_')
            rcw.frame = rcw.frame.Define(weight_name, weight_expression)
            logger.debug('%%%%%%%%%% Attaching histogram called {}'.format(name))
            histo = rcw.frame.Histo1D((
                name, name, nbins, l_edges.data()),
                var, weight_name)

        return histo
