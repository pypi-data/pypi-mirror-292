import importlib.metadata

def print_version():
    print(f"fiver version {importlib.metadata.version("fiver")}")