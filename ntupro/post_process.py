import ROOT
from .run import RunManager


class Customizer:

    def __init__(self, source):
        self.histos = {}
        if isinstance(source, str):
            self.source_file = ROOT.TFile(source)
            names = [key.GetName() for key in self.source_file.GetListOfKeys()]
            for name in names:
                obj = self.source_file.Get(name)
                if isinstance(obj, (ROOT.TH1D, ROOT.TH1F)):
                    self.histos[name] = obj
        elif isinstance(source, RunManager):
            pass
        else:
            raise TypeError('type of source argument can be only str or RunManager')

    def load_style_macro(self, macro_name):
        """Load style macro with inside defined a function with the same name
        of the file itself.

        Args:
            macro_name (str): name of the macro; the file has to contain a void
                function with the same name of the file (e.g. 'setStyle.C' must
                define the function 'void setStyle() {}')
        """
        ROOT.gInterpreter.ProcessLine('#include "{}"'.format(macro_name))
        function_name = macro_name.split('.')[0]
        setattr(self, function_name, getattr(ROOT, function_name))
