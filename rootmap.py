import sys
from pathlib import Path


#
# rootmap best jump shortcut to find root folder
# make sure to use it if needed to access files in other folders
#
def find_and_inject_root():

    root_dir = Path(__file__).resolve().parent

    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    return root_dir


ROOT = find_and_inject_root()

###
# directly use example:
# from rootmap import ROOT
# root = os.path.join(ROOT, "")
###
