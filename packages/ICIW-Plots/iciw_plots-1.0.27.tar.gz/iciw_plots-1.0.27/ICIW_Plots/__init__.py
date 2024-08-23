__name__ = "ICIW_Plots"
from ICIW_Plots.layout import *
from ICIW_Plots.figures import *
import matplotlib.pyplot as plt


cm2inch = 1 / 2.54
mm2inch = 1 / 25.4


def write_styles_to_configdir():
    import matplotlib as mpl
    import os
    import glob
    import logging
    import shutil
    import warnings

    logger = logging.getLogger(__name__)
    logger.log(logging.INFO, "Trying to install ICIW styles.")
    # Find all style files
    stylefiles = glob.glob("ICIW_Plots/*.mplstyle", recursive=True)
    # Find stylelib directory (where the *.mplstyle files go)
    mpl_stylelib_dir = os.path.join(matplotlib.get_configdir(), "stylelib")
    logger.log(logging.INFO, "Stylelib directory is: " + mpl_stylelib_dir)
    if not os.path.exists(mpl_stylelib_dir):
        logger.log(logging.INFO, "Creating stylelib directory.")
        os.makedirs(mpl_stylelib_dir)
    # Copy files over
    logger.log(logging.INFO, f"Copying styles into{mpl_stylelib_dir}")
    for stylefile in stylefiles:
        shutil.copy(
            stylefile, os.path.join(mpl_stylelib_dir, os.path.basename(stylefile))
        )
    else:
        logger.log(logging.INFO, "Styles installed.")
        return

    warnings.warn("Could not install ICIW styles.")


if not "ICIWstyle" in plt.style.available:
    write_styles_to_configdir()
