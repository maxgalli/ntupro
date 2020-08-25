from multiprocessing import Pool
from time import time

from .utils import Count
from .utils import Histogram
from .utils import RDataFrameCutWeight
from .utils import rdf_from_dataset_helper

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

    Attributes:
        graphs (list): List of graphs to be processed
        tchains (list): List of TChains created, saved as attribute
            for the class in order to not let them go out of scope
        friend_tchains (list): List of friend TChains created,
            saved as attribute for the class in otder to not let
            them out of scope
    """
    def __init__(self, graphs):
        self.graphs = graphs
        self.tchains = list()
        self.friend_tchains = list()
        self.rcws = list()

    def _run_multiprocess(self, graph):
        start = time()
        ptrs = self.node_to_root(graph)
        logger.debug('%%%%%%%%%% Ready to produce a subset of {} shapes'.format(
            len(ptrs)))
        results = list()
        for ptr in ptrs:
            th = ptr.GetValue()
            results.append(th)
        # Sanity check: event loop run only once for each RDataFrame
        for rcw in self.rcws:
            loops = rcw.frame.GetNRuns()
            if loops != 1:
                logger.warning('Event loop run {} times'.format(loops))
        end = time()
        logger.debug('Event loop for graph {:} run in {:.2f} seconds'.format(
            repr(graph), end - start))
        return results

    def run_locally(self, output, nworkers = 1, nthreads = 1):
        """Save to file the histograms booked.

        Args:
            output (str): Name of the output .root file
            nworkers (int): number of slaves passed to the
                multiprocessing.Pool() function
            nthreads (int): number of threads passed to the
                EnableImplicitMT function
        """
        if not isinstance(nthreads, int):
            raise TypeError('wrong type for nthreads')
        if nthreads < 1:
            raise ValueError('nthreads has to be larger zero')
        self.nthreads = nthreads
        if not isinstance(nworkers, int):
            raise TypeError('wrong type for nworkers')
        if nworkers < 1:
            raise ValueError('nworkers has to be larger zero')
        logger.info('Start computing locally results of {} graphs using {} workers with {} thread(s) each'.format(
            len(self.graphs), nworkers, nthreads))
        start = time()
        pool = Pool(nworkers)
        final_results = list(pool.map(self._run_multiprocess, self.graphs))
        final_results = [j for i in final_results for j in i]
        end = time()
        logger.info('Finished computations in {} seconds'.format(int(end - start)))
        logger.info('Write {} results from {} graphs to file {}'.format(
            len(final_results), len(self.graphs), output))
        root_file = TFile(output, 'RECREATE')
        for op in final_results:
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
            if result not in self.rcws:
                self.rcws.append(result)
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
        chain, self.friend_tchains = rdf_from_dataset_helper(dataset)
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
        var = histogram.variable
        edges = histogram.edges
        if edges:
            nbins = len(edges) - 1
        else:
            nbins = histogram.nbins
            low = histogram.low
            up = histogram.up
        var_expression = histogram.expression

        # Create column from expression if present in Histogram object
        if var_expression:
            rcw.frame = rcw.frame.Define(var, var_expression)

        # Create macro weight string from sub-weights applied
        # (saved earlier as rdf columns)
        weight_expression = '*'.join(['(' + weight.expression + ')' for weight in rcw.weights])

        # Create macro cut string from sub-cuts applied
        # (saved earlier as rdf columns)
        cut_expression = ' && '.join(['(' + cut.expression + ')' for cut in rcw.cuts])
        if cut_expression:
            rcw.frame = rcw.frame.Filter(cut_expression)

        # Create std::vector with the histogram edges
        if edges:
            l_edges = vector['double']()
            for edge in edges:
                l_edges.push_back(edge)

        if not weight_expression:
            logger.debug('%%%%%%%%%% Attaching histogram called {}'.format(name))
            if edges:
                histo = rcw.frame.Histo1D((
                        name, name, nbins, l_edges.data()),
                        var)
            else:
                histo = rcw.frame.Histo1D((
                        name, name, nbins, low, up),
                        var)
        else:
            weight_name = name.replace('#', '_')
            weight_name = weight_name.replace('-', '_')
            rcw.frame = rcw.frame.Define(weight_name, weight_expression)
            logger.debug('%%%%%%%%%% Attaching histogram called {}'.format(name))
            if edges:
                histo = rcw.frame.Histo1D((
                    name, name, nbins, l_edges.data()),
                    var, weight_name)
            else:
                histo = rcw.frame.Histo1D((
                    name, name, nbins, low, up),
                    var, weight_name)

        return histo
