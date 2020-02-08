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
        return str((
            self.frame,
            self.cuts, self.weights))

    def __eq__(self, other):
        return self.frame == other.frame and \
            self.cuts == other.cuts and \
            self.weights == other.weights

    def __hash__(self):
        return hash((
            self.frame, self.cuts, self.weights))
