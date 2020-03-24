import logging
logger = logging.getLogger(__name__)

import itertools



class NtupleBase:

    def __init__(self, path, directory):
        self.path = path
        self.directory = directory

    def __str__(self):
        layout = '(' + self.path \
                + ', ' + self.directory \
                + ')'
        return layout

    def __eq__(self, other):
        return self.path == other.path and \
            self.directory == other.directory

    def __hash__(self):
        return hash((
            self.path, self.directory))


class Friend(NtupleBase):

    def __init__(self,
            path, directory, tag = None):
        NtupleBase.__init__(self, path, directory)
        self.tag = tag

    def __str__(self):
        if self.tag is None:
            return NtupleBase.__str__(self)
        else:
            layout = '(' + self.path \
                    + ', ' + self.directory \
                    + ', ' + 'tag = {}'.format(self.tag) \
                    + ')'
        return layout


class Ntuple(NtupleBase):

    def __init__(self, path, directory, friends = []):
        NtupleBase.__init__(self, path, directory)
        self.friends = self.__add_tagged_friends(friends)

    def __add_tagged_friends(self, friends):
        for f1,f2 in itertools.combinations(friends, 2):
            l1 = f1.path.split('/')
            l2 = f2.path.split('/')
            tags = list(set(l1).symmetric_difference(set(l2)))
            if tags:
                for t in tags:
                    if t in l1 and f1.tag is None:
                        f1.tag = t
                    elif t in l2 and f2.tag is None:
                        f2.tag = t
        return friends


class Dataset:

    def __init__(self, name, ntuples,
            *build_info):
        self.name = name
        self.ntuples = ntuples
        if build_info:
            self.__set_build_info(*build_info)

    def __str__(self):
        return 'Dataset-{}'.format(self.name)

    def __repr__(self):
        return self.__str__()

    def add_to_ntuples(self, *new_ntuples):
        for new_ntuple in new_ntuples:
            self.ntuples.append(new_ntuple)

    def __set_build_info(self, *build_info):
        self._build_info = dict()
        keys = [
            'file_names', 'folder',
            'files_base_directories',
            'friends_base_directories'
            ]
        for key, info in zip(keys, build_info):
            self._build_info[key] = info

    def __eq__(self, other):
        return self.name == other.name and \
            self.ntuples == other.ntuples

    def __hash__(self):
        return hash((
            self.name, tuple(self.ntuples)))


class Operation:
    def __init__(
            self, expression, name):
        self.expression = expression
        self.name = name

    def __eq__(self, other):
        return self.expression == other.expression and \
            self.name == other.name

    def __hash__(self):
        return hash((
            self.expression, self.name))


class Cut(Operation):
    def __str__(self):
        layout = 'C(' + self.name \
                + ', ' + self.expression \
                + ')'
        return layout

    def __repr__(self):
        layout = 'C(' + self.name \
                + ', ' + self.expression \
                + ')'
        return layout


class Weight(Operation):
    def __str__(self):
        layout = 'W(' + self.name \
                + ', ' + self.expression \
                + ')'
        return layout

    def __repr__(self):
        layout = 'W(' + self.name \
                + ', ' + self.expression \
                + ')'
        return layout

    def square(self):
        self.name = self.name + '^2'
        self.expression = '*'.join([
            self.expression, self.expression])


class Selection:
    def __init__(
            self, name = None,
            cuts = None, weights = None):
        self.name = name
        self.set_cuts(cuts)
        self.set_weights(weights)

    def __str__(self):
        return 'Selection-{}'.format(self.name)

    def __eq__(self, other):
        return self.cuts == other.cuts and \
            self.weights == other.weights

    def __hash__(self):
        return hash((tuple(self.cuts), tuple(self.weights)))

    def split(self):
        minimal_selections = list()
        for cut in self.cuts:
            s = Selection(name = '-'.join([cut.name, self.name]),
                    cuts = [cut])
            minimal_selections.append(s)
        for weight in self.weights:
            s = Selection(name = '-'.join([weight.name, self.name]),
                    weights = [weight])
            minimal_selections.append(s)
        return minimal_selections

    def add_cut(self, cut_expression, cut_name):
        self.cuts.append(Cut(
            cut_expression, cut_name))

    def add_weight(self, weight_expression, weight_name):
        self.weights.append(Weight(
            weight_expression, weight_name))

    def remove_cut(self, cut_name):
        for cut in self.cuts:
            if cut.name is cut_name:
                self.cuts.remove(cut)

    def remove_weight(self, weight_name):
        for weight in self.weights:
            if weight.name is weight_name:
                self.weights.remove(weight)

    def set_cuts(self, cuts):
        self.cuts = list()
        if cuts is not None:
            if isinstance(cuts, list):
                for cut in cuts:
                    if isinstance(cut, Cut):
                        self.cuts.append(cut)
                    elif isinstance(cut, tuple):
                        self.cuts.append(Cut(*cut))
                    else:
                        raise TypeError(
                                'TypeError: Not a Cut object or tuple')
            else:
                raise TypeError(
                        'TypeError: a list is needed.\n')

    def set_weights(self, weights):
        self.weights = list()
        if weights is not None:
            if isinstance(weights, list):
                for weight in weights:
                    if isinstance(weight, Weight):
                        self.weights.append(weight)
                    elif isinstance(weight, tuple):
                        self.weights.append(Weight(*weight))
                    else:
                        raise TypeError(
                                'TypeError: Not a Weight object or tuple')
            else:
                raise TypeError(
                        'TypeError: a list is needed.\n')


class Binning:
    def __init__(self,
            name, edges):
        self.name = name
        self.edges = edges
        self.nbins = len(edges) - 1

    def __eq__(self, other):
        return self.name == other.name and \
            self.edges == other.edges

    def __hash__(self):
        return hash((
            self.name, tuple(self.edges)))

class Action:
    def __init__(self,
            variable, name = None):
        self.variable = variable
        self.name = name

    def __str__(self):
        return  self.name


class Count(Action):
    pass


class Histogram(Action):
    def __init__(
            self, variable,
            edges = None, name = None):
        Action.__init__(self, variable, name)
        if isinstance(variable, Binning) and edges is None:
            self.binning = variable
        else:
            self.binning = Binning(
                variable, edges)
    def __eq__(self, other):
        return self.variable == other.variable and \
            self.binning == other.binning and \
            self.name == other.name

    def __hash__(self):
        return hash((
            self.variable, self.binning,
            self.name))
