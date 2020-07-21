import logging
logger = logging.getLogger(__name__)



class Ntuple:
    def __init__(self, path, directory,
            friends = None, tag = None):
        self.path = path
        self.directory = directory
        if friends:
            self.friends = friends
        else:
            self.friends = list()
        self.tag = tag

    def __str__(self):
        if self.tag is None:
            layout = '({}, {})'.format(self.path, self.directory)
        else:
            layout = '({}, {}, tag = {})'.format(
                    self.path, self.directory, self.tag)
        return layout

    def __eq__(self, other):
        return self.path == other.path and \
            self.directory == other.directory

    def __hash__(self):
        return hash((
            self.path, self.directory))


class Dataset:
    def __init__(self, name, ntuples):
        self.name = name
        self.ntuples = ntuples

    def __str__(self):
        return 'Dataset-{}'.format(self.name)

    def __repr__(self):
        return self.__str__()

    def add_to_ntuples(self, *new_ntuples):
        for new_ntuple in new_ntuples:
            self.ntuples.append(new_ntuple)

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
        return 'Cut(' + self.name \
                + ', ' + self.expression \
                + ')'

    def __repr__(self):
        return self.__str__()


class Weight(Operation):
    def __str__(self):
        return 'Weight(' + self.name \
                + ', ' + self.expression \
                + ')'

    def __repr__(self):
        return self.__str__()

    def square(self):
        self.name = self.name + '^2'
        self.expression = '({0:})*({0:})'.format(self.expression)


class Selection:
    def __init__(
            self, name = None,
            cuts = None, weights = None):
        self.name = name
        self.set_cuts(cuts)
        self.set_weights(weights)

    def __str__(self):
        return 'Selection-{}'.format(self.name)

    def __repr__(self):
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
                        raise TypeError('not a Cut object or tuple')
            else:
                raise TypeError('a list is needed')

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
                        raise TypeError('not a Weight object or tuple')
            else:
                raise TypeError('a list is needed')


class Action:
    def __init__(self,
            name, variable):
        self.name = name
        self.variable = variable

    def __str__(self):
        return  self.name

    def __repr__(self):
        return  self.name

class Count(Action):
    pass


class Histogram(Action):
    def __init__(self, name, variable, setting, expression = None):
        Action.__init__(self, name, variable)
        if isinstance(setting, list):
            self.edges = setting
        elif isinstance(setting, tuple):
            self.nbins, self.low, self.up = setting
            self.edges = None
        else:
            raise TypeError('Argument {} must be either list or tuple'.format(setting))
        self.expression = expression

    def __eq__(self, other):
        if self.edges:
            return self.name == other.name and \
                self.variable == other.variable and \
                self.edges == other.edges
        else:
            return self.name == other.name and \
                self.variable == other.variable and \
                self.nbins == other.nbins and \
                self.low == other.low and \
                self.up == other.up

    def __hash__(self):
        if self.edges:
            return hash((self.name, self.variable, tuple(self.edges)))
        else:
            return hash((self.name, self.variable, self.nbins, self.low, self.up))
