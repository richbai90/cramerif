import importlib.resources
import importlib.util
import sys
from pathlib import Path

from matplotlib import colormaps as cm
from matplotlib.colors import LinearSegmentedColormap

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

RESOURCES_PATH = files('cramerif') / 'resources'

def _load_module(name: str):
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
        return None
    return module

def use(name: str):
    """
    Finds and registers a Crameri colormap by name.
    
    Args:
        name (str): The name of the colormap, with an optional _kind suffix
                    (e.g., 'batlow', 'batlow_discrete', 'batlow_categorical').
    """
    try:
        module = _load_module(name)
        if not module:
            return
        cmap = LinearSegmentedColormap.from_list(name, module.cm_data)
        
        cm.register(cmap=cmap)
        cm.register(cmap=cmap.reversed(), name=f"{name}_r")
        
        print(f"✅ Registered colormap '{name}' and its reversed version '{name}_r'.")

    except ImportError:
        print(f"❌ Error: Could not find the colormap module for '{name}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def LUT(name: str):
    """
    Finds a Crameri colormap by name and converts it a LUT
    Suitable for use by opencv.

    Args:
        name (str): The name of the colormap, with an optional _kind suffix
                    (e.g. 'batlow', 'batlow_discrete', 'batlow_categorical').
    """
    import cv2
    import numpy as np

    module = _load_module(name)
    if not module:
        return
    
    cm_data = module.cm_data
    # 2. Convert to Numpy Array (Float32)
    # Shape becomes (N, 1, 3) -> N rows, 1 column, 3 channels
    data = np.array(cm_data, dtype=np.float32).reshape(-1, 1, 3)

    # 3. Interpolate to 256 values
    # OpenCV LUTs MUST have exactly 256 entries. 
    # cv2.resize handles the interpolation linearly if your list is shorter/longer.
    # Note: cv2.resize arguments are (width, height), so we use (1, 256)
    if data.shape[0] != 256:
        data = cv2.resize(data, (1, 256), interpolation=cv2.INTER_LINEAR)
        # Reshape back to (256, 1, 3) just to be safe after resize
        data = data.reshape(256, 1, 3)

    # 4. Convert Range 0.0-1.0 to 0-255
    data = (data * 255).round()
    
    # 5. Clip and Cast to Uint8
    data = np.clip(data, 0, 255).astype(np.uint8)

    # 6. Convert RGB to BGR
    # Your data is likely RGB, but OpenCV uses BGR.
    # We use cv2.cvtColor to swap the channels efficiently.
    lut = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)

    return lut
