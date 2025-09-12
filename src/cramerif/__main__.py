# src/cramerif/__main__.py

import numpy as np
import matplotlib.pyplot as plt
from . import use

def main():
    """
    Demonstrates the use of a cramerif colormap by registering it
    and displaying it in a plot.
    """
    print("🎨 Running cramerif demonstration...")

    # 1. Choose a colormap to demonstrate
    colormap_name = 'batlow'
    
    # 2. Register the colormap using your library's function
    use(colormap_name)
    
    # 3. Create some sample data
    data = np.random.rand(20, 20)
    
    # 4. Create a plot using the registered colormap
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(data, cmap=colormap_name)
    fig.colorbar(im, ax=ax)
    
    ax.set_title(f"Demonstration of '{colormap_name}' colormap")
    print(f"✅ Displaying plot with '{colormap_name}'. Close the plot to exit.")
    
    plt.show()

if __name__ == "__main__":
    main()
