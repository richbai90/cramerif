import sys
import importlib.util
from pathlib import Path
from matplotlib import cm

# Get a path-like object to the resources folder within the cramerif package.
RESOURCES_PATH = importlib.resources.files('cramerif') / 'resources'

def use(name: str):
    """
    Finds and executes the Python script to register a Crameri colormap.
    
    Args:
        name (str): The name of the colormap (e.g., 'batlow_discrete').
    """
    try:
        # --- 1. Find the Correct Module File Path (Your logic is great) ---
        base_name, kind = name.split('_')
        module_dir = RESOURCES_PATH / base_name
        module_name = base_name

        if kind == 'discrete':
            module_dir = module_dir / 'DiscretePalettes'
        elif kind == 'categorical':
            module_dir = module_dir / 'CategoricalPalettes'
            # categorical names have an 'S' suffix
            module_name = f'{base_name}S'
        
        module_file = module_dir / f"{module_name}.py"
        
        if not module_file.exists():
            print(f"❌ Error: Colormap file not found at '{module_file}'.")
            return

        # --- 2. Load the Module Directly from the File Path ---
        # Create a unique name for the module to avoid import cache conflicts
        unique_module_name = f"cramerif.resources.{base_name}.{kind}"
        
        spec = importlib.util.spec_from_file_location(unique_module_name, module_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[unique_module_name] = module
            spec.loader.exec_module(module)
            cmap = getattr(module, f'{module_name}_map')
            cm.register_cmap(cmap=cmap)
            cm.register_cmap(cmap=cmap.reversed(), name=f"{module_name}_r")
            print(f"✅ Executed registration for colormap '{name}'.")
        else:
            print(f"❌ Error: Could not create a module spec for '{module_file}'.")

    except ValueError:
        print(f"❌ Error: Invalid colormap name format. Expected 'name_kind', e.g., 'batlow_discrete'. Got '{name}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
