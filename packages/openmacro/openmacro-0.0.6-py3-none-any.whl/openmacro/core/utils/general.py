import subprocess
import importlib.util
import toml
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

def is_installed(package):
    spec = importlib.util.find_spec(package)
    return spec is not None


def lazy_import(package,
                name: str = '', 
                prefixes: str = ("pip install ", "py -m pip install "),
                install= False,
                void = False,
                optional=True):
    
    if package in sys.modules:
        return sys.modules[package]

    spec = importlib.util.find_spec(name or package)
    if spec is None:
        if optional:
            return None
        elif install:
            for prefix in prefixes:
                print(f"Module '{package}' is missing, proceeding to install.")
                try: subprocess.run(prefix + package, shell=True, check=True)
                except subprocess.CalledProcessError: continue
                break
            raise ImportError(f"Failed to install module '{name or package}'")
        else:
            raise ImportError(f"Module '{name or package}' cannot be found")
        
    if void:
        return None

    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)

    return module

def lazy_imports(packages: list[str | tuple[str]], 
                 prefix: str = "pip install ",
                 user_install = False,
                 void = False):
    
    libs = []
    for package in packages:
        if not isinstance(package, str):
            package = (package[0], None) if len(package) == 1 else package
        else:
            package = (package, None)
            
        if (pack := lazy_import(*package, prefix=prefix, user_install=user_install, void=void)):
            libs.append(pack)

    if void:
        return None
    
    return tuple(libs)

def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(value, dict) and isinstance(dict1[key], dict):
                merge_dicts(dict1[key], value)  # Recursively merge child dictionaries
            else:
                dict1[key] = value  # Overwrite with the new value
        else:
            dict1[key] = value  # Add new key-value pairs
    return dict1

def load_settings(file: str | Path = None, settings=None, section=None, verbose=False):
    if settings is None:
        config_default = Path(ROOT_DIR, "config.default.toml")
        with open(config_default, "r") as f:
            settings = toml.load(f)
            
        if file:
            config = Path(file)
            if config.is_file():
                with open(config, "r") as f:
                    if (setting := toml.load(f)):
                        settings = merge_dicts(settings, setting)
            elif verbose:
                print("config.toml not found, using config.defaults.toml instead!")

    return settings.get(section, settings) if section else settings