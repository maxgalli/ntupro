from .utils import Dataset
from .utils import Selection
from .utils import Ntuple
from .utils import Cut
from .utils import Weight
from .utils import Action
from .utils import Count
from .utils import Histogram
from .utils import Variation

from ROOT import gROOT
gROOT.SetBatch(True)
from ROOT import TFile

import os
import re
import json
import itertools

import logging
logger = logging.getLogger(__name__)



def dataset_from_artusoutput(
        dataset_name,
        file_names,
        folder,
        files_base_directory,
        friends_base_directories):
    """Create a Dataset object from a list containing the names
    of the ROOT files (e.g. [root_file1, root_file2, (...)]):
        ntuple1: /file_base_dir/root_file1/folder/ntuple
            friend1: /friend1_base_dir/root_file1/folder/ntuple
            friend2: /friend2_base_dir/root_file1/folder/ntuple
        ntuple2: /file_base_dir/root_file2/folder/ntuple
            friend1: /friend1_base_dir/root_file2/folder/ntuple
            friend2: /friend2_base_dir/root_file2/folder/ntuple
        ntuple3: /file_base_dir/root_file3/folder/ntuple
            friend1: /friend1_base_dir/root_file3/folder/ntuple
            friend2: /friend2_base_dir/root_file3/folder/ntuple
        (...)

    Args:
        dataset_name (str): Name of the dataset
        file_names (list): List containing the names of the .root
            files
        folder (str): Name of the TDirectoryFile in each .root file
        files_base_directory (str): Path to the files base directory (directories)
        friends_base_directories (str, list): List of paths to
            the friends base directory (directories)

    Returns:
        dataset (Dataset): Dataset object containing TTrees
    """
    def get_full_tree_name(folder, path_to_root_file, tree_name):
        root_file = TFile(path_to_root_file)
        if root_file.IsZombie():
            raise FileNotFoundError('File {} does not exist, abort'.format(path_to_root_file))
        if folder not in root_file.GetListOfKeys():
            raise NameError('Folder {} does not exist in {}\n'.format(folder, path_to_root_file))
        root_file.Close()
        full_tree_name = '/'.join([folder, tree_name])
        return full_tree_name

    def add_tagged_friends(friends):
        """ Tag friends with the name of the different directories
        in the artus name scheme, e.g.:
        /common_path/MELA/ntuple -> tag: MELA
        /common_path/SVFit/ntuple -> tag: SVFit
        Since when we compare two ntuples (with full path) only one
        directory changes in this scheme (see MELA vs SVFit), we
        create a list called 'tags' with these two strings; then we
        assign this string to friend.tag, if it's None
        """
        for f1, f2 in itertools.combinations(friends, 2):
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

    # E.g.: file_base_dir/file_name/file_name.root
    root_files = [os.path.join(files_base_directory, f, "{}.root".format(f)) for f in file_names]

    # E.g.: file_base_dir/file_name1/file_name1.root/folder/ntuple
    #       file_base_dir/file_name1/file_name2.root/folder/ntuple
    ntuples = []
    for root_file, file_name in zip(root_files, file_names):
        tdf_tree = get_full_tree_name(folder, root_file, 'ntuple')
        friends = []
        for friends_base_directory in friends_base_directories:
            friend_path = os.path.join(friends_base_directory, file_name, "{}.root".format(file_name))
            tdf_tree_friend = get_full_tree_name(folder, friend_path, 'ntuple')
            if tdf_tree != tdf_tree_friend:
                raise Exception("Extracted wrong TDirectoryFile from friend which is not the same than the base file.")
            friends.append(Ntuple(friend_path, tdf_tree_friend))
        ntuples.append(Ntuple(root_file, tdf_tree, add_tagged_friends(friends)))

    return Dataset(dataset_name, ntuples)


def dataset_from_files(dataset_name, tree_name, file_names):
    """Create a Dataset object from a list containing the names
    of the ROOT files (e.g. [root_file1, root_file2, (...)]):
    E.g.:
        my_dataset = dataset_from_files('my_dataset', 'tree_name', ['f1.root', 'f2.root'])

    Args:
        dataset_name (str): Name of the dataset
        tree_name (str): Name of the tree spanned through multiple files
        file_names (list): List containing the names of the .root
            files

    Returns:
        dataset (Dataset): Dataset object containing TTrees
    """
    def return_existent_tuple(file_name, tree_name):
        # Use TFile.Open() instead of TFile() in order to deal with
        # files accessed from remote
        root_file = TFile.Open(file_name)
        if root_file.IsZombie():
            raise FileNotFoundError('File {} does not exist, abort'.format(file_name))
        if tree_name not in root_file.GetListOfKeys():
            raise NameError('Tree {} does not exist in {}\n'.format(tree_name, file_name))
        root_file.Close()
        return Ntuple(file_name, tree_name)

    if not isinstance(file_names, list):
        raise TypeError('A list containing file names is required')

    ntuples = [return_existent_tuple(file_name, tree_name) for file_name in file_names]

    return Dataset(dataset_name, ntuples)


class Unit:
    """
    Building element of a minimal analysis flow, consisting
    of a dataset, a set of selections to apply on the data
    and a set of actions.

    Args:
        dataset (Dataset): Set of TTree objects to run the
            analysis on
        selections (list): List of Selection-type objects
        actions (Action): Actions to perform on the processed
            dataset, can be 'Histogram' or 'Count'
        variation (Variation): Variations applied, meaning
            that this selection is the result of a variation
            applied on other selections

    Attributes:
        dataset (Dataset): Set of TTree objects to run the
            analysis on
        selections (list): List of Selection-type objects
        actions (Action): Actions to perform on the processed
            dataset, can be 'Histogram' or 'Count'
        variation (Variation): Variations applied, meaning
            that this selection is the result of a variation
            applied on other selections
    """
    def __init__(
            self,
            dataset, selections, actions,
            variation = None):
        self.__set_dataset(dataset)
        self.__set_selections(selections)
        self.__set_actions(actions, variation)

    def __str__(self):
        layout = '\n'.join([
            'Dataset: {}'.format(self.dataset.name),
            'Selections: {}'.format(self.selections.__repr__()),
            'Actions: {}'.format(self.actions.__repr__())])
        return layout

    def __set_dataset(self, dataset):
        if not isinstance(dataset, Dataset):
            raise TypeError('not a Dataset object.')
        self.dataset = dataset

    def __set_selections(self, selections):
        if not isinstance(selections, list):
            raise TypeError('not a list object.')
        for selection in selections:
            if not isinstance(selection, Selection):
                raise TypeError('not a Selection object.')
        self.selections = selections

    def __set_actions(self, actions, variation):
        if not isinstance(actions, list):
            raise TypeError('not a list object.')
        for action in actions:
            if not isinstance(action, Action):
                raise TypeError('not an Action object.')
        self.actions = [self.__set_new_action(action, variation) \
                for action in actions]

    def __set_new_action(self, action, variation):
        if variation is None:
            name = '#'.join([self.dataset.name,
                '-'.join([selection.name for selection in self.selections]),
                action.name, 'Nominal'])
        else:
            if not isinstance(variation, Variation):
                raise TypeError('not a Variation object.')
            self.variation = variation
            name = action.name.replace('Nominal', self.variation.name)
        if isinstance(action, Histogram):
            if action.edges:
                return Histogram(name, action.variable, action.edges, action.expression)
            else:
                return Histogram(name, action.variable,
                        (action.nbins, action.low, action.up), action.expression)
        elif isinstance(action, Count):
            return Count(name, action.variable)

    def __eq__(self, other):
        return self.dataset == other.dataset and \
            self.selections == other.selections and \
            self.actions == other.actions

    def __hash__(self):
        return hash((
            self.dataset, tuple(self.selections),
            tuple(self.actions)))


class UnitManager:
    """
    Manager of all the Unit objects that are created.
    It can both be initialized with a variable amount of Unit
    objects as arguments or with no arguments, with the above mentioned
    objects added in a second time with the function 'book'.

    Attributes:
        booked_units (list): List of the booked units, updated during
            initialization or with the function 'book'
    """

    booked_units = []

    def book(self, units, variations = None):
        for unit in units:
            if unit not in self.booked_units:
                self.booked_units.append(unit)
        if variations:
            for variation in variations:
                logger.debug('Applying variation {}'.format(variation))
                for unit in units:
                    self.apply_variation(unit, variation)
        for action1, action2 in itertools.combinations([j for i in [
            unit.actions for unit in self.booked_units] for j in i], 2):
            if action1.name == action2.name:
                raise NameError('Caught two actions with same name ({}, {})'.format(
                    action1.name, action2.name))

    def apply_variation(self, unit, variation):
        new_unit = variation.create(unit)
        self.booked_units.append(new_unit)
