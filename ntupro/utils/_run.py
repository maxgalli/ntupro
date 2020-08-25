from ROOT import TChain

import logging
logger = logging.getLogger(__name__)

class RDataFrameCutWeight:
    def __init__(self,
            frame, cuts = [], weights = []):
        self.frame = frame
        self.cuts = cuts
        self.weights = weights

    def __str__(self):
        return str((
            self.frame,
            self.cuts, self.weights))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.frame == other.frame and \
            self.cuts == other.cuts and \
            self.weights == other.weights

    def __hash__(self):
        return hash((
            self.frame, self.cuts, self.weights))

def rdf_from_dataset_helper(dataset):
    t_names = [ntuple.directory for ntuple in \
        dataset.ntuples]
    if len(set(t_names)) == 1:
        tree_name = t_names.pop()
    else:
        raise NameError(
            'Impossible to create RDataFrame with different tree names')
    chain = TChain()
    ftag_fchain = {}
    friend_tchains = []
    for ntuple in dataset.ntuples:
        chain.Add('{}/{}'.format(
            ntuple.path, ntuple.directory))
        for friend in ntuple.friends:
            if friend.tag not in ftag_fchain.keys():
                ftag_fchain[friend.tag] = TChain()
            ftag_fchain[friend.tag].Add('{}/{}'.format(
                friend.path, friend.directory))
    for ch in ftag_fchain.values():
        chain.AddFriend(ch)
        # Keep friend chains alive
        friend_tchains.append(ch)
    return (chain, friend_tchains)
