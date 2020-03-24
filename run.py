from multiprocessing import Pool

from .utils import Count
from .utils import Histogram
from .utils import RDataFrameCutWeight

from ROOT import gROOT
gROOT.SetBatch(True)
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
        Count()       -->   Sum()
        Histogram()   -->   Histo1D()

    Args:
        graphs (list): List of Graph objects that are converted
            node by node to RDataFrame operations
        workers (int): number of slaves passed to the
            multiprocessing.Pool() function
        nthreads (int): number of threads passed to the
            EnableImplicitMT function

    Attributes:
        final_results (list): List of TH1D objects resulting from a
            set of Filter operations performed on RDataFrames; on
            all them we need to perform a Write operation
        tchains (list): List of TChains created, saved as attribute
            for the class in order to not let them go out of scope
        friend_tchains (list): List of friend TChains created,
            saved as attribute for the class in otder to not let
            them out of scope
        workers (int): number of slaves passed to the
            multiprocessing.Pool() function
        nthreads (int): number of threads passed to the
            EnableImplicitMT function
    """
    def __init__(self, graphs,
            workers = 1,
            nthreads = 1):
        self.final_results = list()
        self.tchains = list()
        self.friend_tchains = list()
        if not isinstance(nthreads, int):
            raise TypeError('TypeError: wrong type for nthreads')
        if nthreads < 1:
            raise ValueError('ValueError: nthreads has to be larger zero')
        self.nthreads = nthreads
        if not isinstance(workers, int):
            raise TypeError('TypeError: wrong type for workers')
        if workers < 1:
            raise ValueError('ValueError: workers has to be larger zero')
        logger.info('Computing {} graphs using {} workers with {} threads each'.format(
            len(graphs), workers, nthreads))
        pool = Pool(workers)
        self.final_results = list(pool.map(self._run_multiprocess, graphs))
        self.final_results = [j for i in self.final_results for j in i]

    def _run_multiprocess(self, graph):
        ptrs = self.node_to_root(graph)
        logger.debug('%%%%%%%%%% Ready to produce a subset of {} shapes'.format(
            len(ptrs)))
        results = list()
        for ptr in ptrs:
            th = ptr.GetValue()
            results.append(th)
        return results

    def run_locally(self, of_name, update = False):
        """Save to file the histograms booked.

        Args:
            of_name (str): Name of the output .root
                file
        """
        logger.info('%%%%%%%%%% Writing {} shapes to {}'.format(
            len(self.final_results), of_name))
        if update:
            root_file = TFile(of_name, 'UPDATE')
        else:
            root_file = TFile(of_name, 'RECREATE')
        for op in self.final_results:
            op.Write()
        root_file.Close()

    def node_to_root(self, node, final_results = None, rcw = None):
        if final_results is None:
            final_results = list()
        if node.kind == 'dataset':
            logger.debug('%%%%%%%%%% node_to_root, converting to ROOT language the following dataset node\n{}'.format(
                node))
            result = self.__rdf_from_dataset(
                node.unit_block)
        elif node.kind == 'selection':
            if len(node.children) > 1:
                logger.debug('%%%%%%%%%% node_to_root, converting to ROOT language the following crossroad node\n{}'.format(
                    node))
            result = self.__cuts_and_weights_from_selection(
                rcw, node.unit_block)
        elif node.kind == 'action':
            logger.debug('%%%%%%%%%% node_to_root, converting to ROOT language the following action node\n{}'.format(
                node))
            if isinstance(node.unit_block, Count):
                result = self.__sum_from_count(
                    rcw, node.unit_block)
            elif isinstance(node.unit_block, Histogram):
                result = self.__histo1d_from_histo(
                    rcw, node.unit_block)
        if node.children:
            for child in node.children:
                self.node_to_root(child, final_results, result)
        else:
            final_results.append(result)
        return final_results

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
        if self.nthreads != 1:
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
