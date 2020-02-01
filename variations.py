class ChangeDataset:
    def __init__(self, dataset):
        self.dataset = dataset

    def __str__(self):
        return '(D-' + self.dataset + ')'

class Replace:
    def __init__(self,
            name, expression):
        self.name = name
        self.expression = expression

    def __str__(self):
        layout = '(' + self.name \
                + ', ' + self.expression \
                + ')'
        return layout

class ReplaceCut(Replace):
    def __init__(self,
            name, cut, expression):
        Replace.__init__(self, name, expression)
        self.cut = cut

class ReplaceWeight(Replace):
    def __init__(self,
            name, cut, expression):
        Replace.__init__(self, name, expression)
        self.weight = weight

class RemoveCut:
    def __init__(self, cut):
        self.cut = cut

    def __str__(self):
        return '(x-' + self.cut + ')'

class RemoveCut:
    def __init__(self, weight):
        self.weight = weight

    def __str__(self):
        return '(x-' + self.weight + ')'
