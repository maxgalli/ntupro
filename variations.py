class ReplaceCut:
    def __init__(self,
            name, cut, expression):
        self.name = name
        self.cut = cut
        self.expression = expression

    def __str__(self):
        layout = '(' + self.name \
                + ', ' + self.expression \
                + ')'
        return layout

