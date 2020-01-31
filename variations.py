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
