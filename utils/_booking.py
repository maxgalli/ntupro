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

    def __init__(self, name, ntuples):
        self.name = name
        self.ntuples = ntuples

    def __str__(self):
        return 'Dataset-{}'.format(self.name)

    def add_to_ntuples(*new_ntuples):
        for new_ntuple in new_ntuples:
            self.ntuples.append(new_ntuple)


class Operation:
    def __init__(
            self, expression, name):
        self.expression = expression
        self.name = name

    def __eq__(self, other):
        return self.expression == other.expression and \
            self.name == other.name


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
        return self.name == other.name and \
            self.cuts == other.cuts and \
            self.weights == other.weights

    def __hash__(self):
        return hash((
            self.name, tuple(self.cuts), tuple(self.weights)))

    def set_cuts(self, cuts):
        if cuts is not None:
            self.__check_format(cuts, Cut)
            self.cuts = cuts
        else:
            self.cuts = []

    def set_weights(self, weights):
        if weights is not None:
            self.__check_format(weights, Weight)
            self.weights = weights
        else:
            self.weights = []

    def __check_format(self, lst, operation):
        if isinstance(lst, list):
            for ob in lst:
                if isinstance(ob, tuple)\
                        and len(ob) == 2:
                    lst[lst.index(ob)] = operation(*ob)
                    ret_value = True
                elif isinstance(ob, operation):
                    ret_value = True
                else:
                    raise TypeError(
                            'TypeError: pass 2-tuples or {} objects.\n'.format(
                                str(operation)))
        else:
            raise TypeError(
                    'TypeError: a list of tuples is needed.\n')
        return ret_value


class Binning:
    def __init__(self,
            name, edges):
        self.name = name
        self.edges = edges
        self.nbins = len(edges) - 1


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
