import logging
from rich.logging import RichHandler
from rich.console import Console

from .booking import Ntuple
from .booking import Dataset
from .booking import Cut
from .booking import Weight
from .booking import Selection
from .booking import Histogram
from .booking import dataset_from_artusoutput
from .booking import dataset_from_files
from .booking import Unit
from .booking import UnitManager
from .optimization import GraphManager
from .run import RunManager
from .variations import ReplaceCut
from .inspect import get_dataframe
from .post_process import Customizer


def setup_logger(level="INFO", logfile=None):
    """Setup a logger that uses RichHandler to write the same message both in stdout
    and in a log file called logfile. Level of information can be customized and
    dumping a logfile is optional.
    """
    logger = logging.getLogger()

    # Set up level of information
    possible_levels = ["INFO", "DEBUG"]
    if level not in possible_levels:
        raise ValueError("Passed wrong level for the logger. Allowed levels are: {}".format(
            ', '.join(possible_levels)))
    logger.setLevel(getattr(logging, level))

    formatter = logging.Formatter("%(message)s")

    # Set up stream handler (for stdout)
    stream_handler = RichHandler(show_time=False, rich_tracebacks=True)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Set up file handler (for logfile)
    if logfile:
        file_handler = RichHandler(
                show_time=False,
                rich_tracebacks=True,
                console=Console(file=open(logfile, "wt"))
                )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger