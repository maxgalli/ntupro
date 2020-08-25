from copy import deepcopy

from .booking import Unit
from .booking import dataset_from_artusoutput
from .utils import Selection
from .utils import Variation

import logging
logger = logging.getLogger(__name__)



class ChangeDataset(Variation):
    """
    Variation that with the method create makes a deepcopy of
    the dataset inside the unit passed as argument and substitutes
    the directory attribute with folder_name.

    Args:
        name (str): name used to identify the instance of
            this class
        folder_name (str): part of the name of the TDirectoryFile
            in the new dataset following the prefix 'channel_' and
            preceding the suffix '/tree_name', e.g. 'NewFolder' in
            'mt_NewFolder/ntuple'

    Attributes:
        name (str): name used to identify the instance of
            this class
        folder_name (str): part of the name of the TDirectoryFile
            in the new dataset following the prefix 'channel_' and
            preceding the suffix '/tree_name', e.g. 'NewFolder' in
            'mt_NewFolder/ntuple'
    """
    def __init__(self,
            name, folder_name):
        Variation.__init__(self, name)
        self.folder_name = folder_name

    def create(self, unit):
        # A perfect copy of the daatset is exactly what
        # we need, thus using deepcopy is fine
        def change_folder(ntuple):
            folder, tree = ntuple.directory.split('/')
            ntuple.directory = '{}_{}/{}'.format(
                    folder.split('_')[0], self.folder_name, tree)
        new_dataset = deepcopy(unit.dataset)
        for ntuple in new_dataset.ntuples:
            change_folder(ntuple)
            for friend in ntuple.friends:
                change_folder(friend)
        return Unit(new_dataset, unit.selections, unit.actions, self)


class ReplaceCut(Variation):
    def __init__(self,
            name, replaced_name, cut):
        Variation.__init__(self, name)
        self.replaced_name = replaced_name
        self.cut = cut

    def create(self, unit):
        # Check that the name is present in at least one of the selections and raise an
        # error if not
        if not set([cut.name for selection in unit.selections for cut in selection.cuts \
                if cut.name == self.replaced_name]):
            raise NameError('Cut {} not found in any selection of this Unit'.format(self.replaced_name))
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
        # Check that the name is present in at least one of the selections and raise an
        # error if not
        if not set([weight.name for selection in unit.selections for weight in selection.weights \
                if weight.name == self.replaced_name]):
            raise NameError('Weight {} not found in any selection of this Unit'.format(self.replaced_name))
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
        # Check that the name is present in at least one of the selections and raise an
        # error if not
        if not set([cut.name for selection in unit.selections for cut in selection.cuts \
                if cut.name == self.removed_name]):
            raise NameError('Cut {} not found in any selection of this Unit'.format(self.removed_name))
        new_selections = [selection for selection in unit.selections]
        for new_selection in new_selections:
            new_selection.remove_cut(self.removed_name)
        return Unit(unit.dataset, new_selections, unit.actions, self)

class RemoveWeight(Variation):
    def __init__(self,
            name, removed_name):
        Variation.__init__(self, name)
        self.removed_name = removed_name

    def create(self, unit):
        # Check that the name is present in at least one of the selections and raise an
        # error if not
        if not set([weight.name for selection in unit.selections for weight in selection.weights \
                if weight.name == self.removed_name]):
            raise NameError('Weight {} not found in any selection of this Unit'.format(self.removed_name))
        new_selections = [selection for selection in unit.selections]
        for new_selection in new_selections:
            new_selection.remove_weight(self.removed_name)
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
        # Check that the name is present in at least one of the selections and raise an
        # error if not
        if not set([weight.name for selection in unit.selections for weight in selection.weights \
                if weight.name == self.weight_name]):
            raise NameError('Weight {} not found in any selection of this Unit'.format(self.weight_name))
        new_selections = [selection for selection in unit.selections]
        for new_selection in new_selections:
            for weight in new_selection.weights:
                if weight.name == self.name:
                    weight.square()
        return Unit(unit.dataset, new_selections, unit.actions, self)


class ReplaceCutAndAddWeight(Variation):
    def __init__(self,
            name, replaced_name, cut, weight):
        Variation.__init__(self, name)
        self.replace_cut = ReplaceCut(name, replaced_name, cut)
        self.add_weight = AddWeight(name, weight)

    def create(self, unit):
        unit = self.replace_cut.create(unit)
        return self.add_weight.create(unit)
