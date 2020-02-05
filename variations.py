from .booking import Unit
from .utils import Selection

import logging
logger = logging.getLogger(__name__)

class Variation:
    def __init__(self,
            name):
        self.name = name

    def create(self, unit):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class ChangeDataset(Variation):
    def __init__(self,
            name, folder_name,
            suffix = []):
        Variation.__init__(self, name)
        self.folder_name = folder_name
        self.suffix = suffix

    def create(self, unit):
        for suff in self.suffix:
            new_folder_name = unit.dataset._build_info['folder'].split('_')[0]\
                + '_'\
                + self.folder_name\
                + suff
            new_dataset = dataset_from_database(
                    self.folder_name,
                    unit.dataset._build_info['path_to_database'],
                    unit.dataset._build_info['queries'],
                    new_folder_name,
                    unit.dataset._build_info['files_base_directories'],
                    unit.dataset._build_info['friends_base_directories'])
            return Unit(new_dataset, unit.selections, unit.actions, self)


class ReplaceCut(Variation):
    def __init__(self,
            name, replaced_name, cut):
        Variation.__init__(self, name)
        self.replaced_name = replaced_name
        self.cut = cut

    def create(self, unit):
        new_selections = list()
        for selection in unit.selections:
            copy_cuts = list()
            for cut in selection.cuts:
                if cut.name == self.replaced_name:
                    logger.debug('Substitute {} with {} in selection {}'.format(
                        cut, self.cut, selection))
                    copy_cuts.append(self.cut)
                else:
                    copy_cuts.append(cut)
            new_selections.append(Selection(
                selection.name,
                copy_cuts,
                selection.weights))
        return Unit(unit.dataset, new_selections, unit.actions, self)


class ReplaceWeight(Variation):
    def __init__(self,
            name, replaced_name, weight):
        Variation.__init__(self, name)
        self.replaced_name = replaced_name
        self.weight = weight

    def create(self, unit):
        new_selections = list()
        for selection in unit.selections:
            copy_weights = list()
            for weight in selection.weights:
                if weight.name == self.replaced_name:
                    logger.debug('Substitute {} with {} in selection {}'.format(
                        weight, self.weight, selection))
                    copy_weights.append(self.weight)
                else:
                    copy_weights.append(weight)
            new_selections.append(Selection(
                selection.name,
                selection.cuts,
                copy_weights))
        return Unit(unit.dataset, new_selections, unit.actions, self)


class RemoveCut(Variation):
    def __init__(self,
            name, removed_name):
        Variation.__init__(self, name)
        self.removed_name = removed_name

    def create(self, unit):
        new_selections = [selection for selection in unit.selections]
        for new_selection in new_selections:
            selection.remove_cut(self.removed_name)
        return Unit(unit.dataset, new_selections, unit.actions, self)

class RemoveWeight(Variation):
    def __init__(self,
            name, removed_name):
        Variation.__init__(self, name)
        self.removed_name = removed_name

    def create(self, unit):
        new_selections = [selection for selection in unit.selections]
        for new_selection in new_selections:
            selection.remove_weight(self.removed_name)
        return Unit(unit.dataset, new_selections, unit.actions, self)


class AddCut(Variation):
    def __init__(self,
            name, cut):
        Variation.__init__(self, name)
        self.cut = cut

    def create(self, unit):
        new_selections = [selection for selection in unit.selections]
        new_selections.append(Selection(
            name = self.cut.name, cuts = [self.cut]))
        return Unit(unit.dataset, new_selections, unit.actions, self)


class AddWeight(Variation):
    def __init__(self,
            name, weight):
        Variation.__init__(self, name)
        self.weight = weight

    def create(self, unit):
        new_selections = [selection for selection in unit.selections]
        new_selections.append(Selection(
            name = self.weight.name, weights = [self.weight]))
        return Unit(unit.dataset, new_selections, unit.actions, self)


class SquareWeight(Variation):
    def __init__(self,
            name, weight_name):
        Variation.__init__(self, name)
        self.weight_name = weight_name

    def create(self, unit):
        new_selections = [selection for selection in unit.selections]
        for new_selection in new_selections:
            for weight in new_selection.weights:
                if weight.name == self.name:
                    weight.square()
        return Unit(unit.dataset, new_selections, unit.actions, self)
