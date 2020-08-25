from ROOT import RDataFrame
from .utils import rdf_from_dataset_helper

def get_dataframe(dataset):
    tchain, friend_tchains = rdf_from_dataset_helper(dataset)
    rdf = RDataFrame(tchain)
    setattr(rdf, 'tchain', tchain)
    setattr(rdf, 'friend_tchains', friend_tchains)
    return rdf
