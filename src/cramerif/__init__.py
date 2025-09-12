import sys
import importlib.util
import importlib.resources
from pathlib import Path
from matplotlib import colormaps as cm
from matplotlib.colors import LinearSegmentedColormap

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

RESOURCES_PATH = files('cramerif') / 'resources'

def use(name: str):
    """
    Finds and registers a Crameri colormap by name.
    
    Args:
        name (str): The name of the colormap, with an optional _kind suffix
                    (e.g., 'batlow', 'batlow_discrete', 'batlow_categorical').
    """
    try:
        if '_' in name and name.rsplit('_', 1)[1] in ['discrete', 'categorical']:
            base_name, kind = name.rsplit('_', 1)
        else:
            base_name = name
            kind = 'continuous'

        # Construct the module path for a direct import
        module_path = f"cramerif.resources.{base_name}"
        if kind == 'discrete':
            module_path += f".DiscretePalettes.{base_name}"
        elif kind == 'categorical':
            module_path += f".CategoricalPalettes.{base_name}S"
        else:
            module_path += f".{base_name}"

        # Import the module directly
        module = importlib.import_module(module_path)
        
        if not hasattr(module, 'cm_data'):
            print(f"❌ Error: The module '{module_path}' does not contain a 'cm_data' variable.")
            return

        cmap = LinearSegmentedColormap.from_list(name, module.cm_data)
        
        cm.register(cmap=cmap)
        cm.register(cmap=cmap.reversed(), name=f"{name}_r")
        
        print(f"✅ Registered colormap '{name}' and its reversed version '{name}_r'.")

    except ImportError:
        print(f"❌ Error: Could not find the colormap module for '{name}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
