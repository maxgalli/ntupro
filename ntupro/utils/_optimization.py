import logging
logger = logging.getLogger(__name__)

class Node:
    def __init__(self,
            name, kind, unit_block, *children):
        self.name = name
        self.kind = kind
        self.unit_block = unit_block
        self.children = [
            child for child in children]

    def __str__(self):
        return '|Name: {}, Type: {}, Children: {}|'.format(
                self.name, self.kind, str(len(self.children)))

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and \
            self.kind == other.kind and \
            self.unit_block == other.unit_block

    def __hash__(self):
        return hash((
            self.name, self.kind, self.unit_block))

