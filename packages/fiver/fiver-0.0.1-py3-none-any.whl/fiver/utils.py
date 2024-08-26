import argparse, os, platform

class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts

def path_fiverdb():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    path_db = os.path.join(current_directory, "fiverdb.json")
    return path_db

def is_lunix():
    os_name = platform.system()
    if os_name == "Linux":
        return True
    return False