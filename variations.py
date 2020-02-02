class ChangeDataset:
    def __init__(self,
            var_name, folder_name):
        self.name = var_name
        self.folder_name = folder_name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Replace:
    def __init__(self,
            var_name, replaced_name):
        self.name = var_name
        self.replaced_name = replaced_name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class ReplaceCut(Replace):
    def __init__(self,
            var_name, replaced_name, cut):
        Replace.__init__(self, var_name, replaced_name)
        self.cut = cut

class ReplaceWeight(Replace):
    def __init__(self,
            var_name, replaced_name, weight):
        Replace.__init__(self, var_name, replaced_name)
        self.weight = weight

class Remove:
    def __init__(self,
            var_name, removed_name):
        self.name = var_name
        self.removed_name = removed_name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class RemoveCut(Remove):
    pass

class RemoveWeight(Remove):
    pass

class Add:
    def __init__(self, var_name):
        self.name = var_name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class AddCut(Add):
    def __init__(self,
            var_name, cut):
        Add.__init__(self, var_name)
        self.cut = cut

class AddWeight(Add):
    def __init__(self,
            var_name, weight):
        Add.__init__(self, var_name)
        self.weight = weight

