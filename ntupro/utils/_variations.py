class Variation:
    """Base class for variations. The main method
    of this kind of class is 'create', here only
    declared and reimplemented in every derived class.
    It applies the Variation object to a Unit object
    and returns a new Unit object.

    Attributes:
        name (str): name assigned to the variation
    """
    def __init__(self,
            name):
        self.name = name

    def create(self, unit):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
