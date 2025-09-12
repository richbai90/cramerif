import sys
import importlib.util
from pathlib import Path
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

RESOURCES_PATH = importlib.resources.files('cramerif') / 'resources'

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
            kind = 'continuous'  # Assign a default kind

        module_dir = RESOURCES_PATH / base_name
        module_name = base_name
        
        if kind == 'discrete':
            module_dir = module_dir / 'DiscretePalettes'
        elif kind == 'categorical':
            module_dir = module_dir / 'CategoricalPalettes'
            module_name = f'{base_name}S'
        
        module_file = module_dir / f"{module_name}.py"
        
        if not module_file.exists():
            print(f"❌ Error: Colormap file not found at '{module_file}'.")
            return

        unique_module_name = f"cramerif.resources.{base_name}.{kind}"
        
        spec = importlib.util.spec_from_file_location(unique_module_name, module_file)
        if not (spec and spec.loader):
            print(f"❌ Error: Could not create module spec for '{module_file}'.")
            return
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[unique_module_name] = module
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'cm_data'):
            print(f"❌ Error: The file '{module_file}' does not contain a 'cm_data' variable.")
            return

        cmap = LinearSegmentedColormap.from_list(name, module.cm_data)
        
        cm.register_cmap(cmap=cmap)
        cm.register_cmap(cmap=cmap.reversed(), name=f"{name}_r")
        
        print(f"✅ Registered colormap '{name}' and its reversed version '{name}_r'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
