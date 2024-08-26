from pathlib import Path
import os



FIM_SCRIPTS_DIR = Path(__file__).parent.absolute()
FUTILITY_DIR = FIM_SCRIPTS_DIR.parent.absolute()
OUTSIDE_DIR = FUTILITY_DIR.parent.absolute()
FUNPACKED_FITS = FUTILITY_DIR.joinpath('funpacked_fits')
INJECTED_FITS = FUTILITY_DIR.joinpath('injected_fits')
FIM_DATA_DIR = FIM_SCRIPTS_DIR.joinpath('fim_data')
CAT_DIR = FIM_DATA_DIR.joinpath('catalogs')


if not os.path.exists(FUNPACKED_FITS):
    os.mkdir(FUNPACKED_FITS)

if not os.path.exists(FIM_DATA_DIR):
    os.mkdir(FIM_DATA_DIR)
if not os.path.exists(INJECTED_FITS):
    os.mkdir(INJECTED_FITS)
if not os.path.exists(CAT_DIR):
    os.mkdir(CAT_DIR)
