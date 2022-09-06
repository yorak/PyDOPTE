import os, sys
cmd_folder = os.path.dirname(os.path.abspath(__file__))
main_module_folder = os.path.dirname(cmd_folder)
if main_module_folder not in sys.path:
    sys.path.insert(0, main_module_folder)

