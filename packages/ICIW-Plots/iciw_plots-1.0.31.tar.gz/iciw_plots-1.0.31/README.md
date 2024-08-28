
# <p align="right">![](ICIW_Plots_Logo.png)</p>
## Installation

Install the package by running the following command:

```bash
pip install iciw-plots
```

or 
    
```bash
pip install iciw-plots -U
```

## Usage

Although I show the usage of the package in the context of a Jupyter notebook, the package can be used in any Python environment.
Also, the style has to be used only once, at the beginning of the plotting file or notebook.
**In this document I write it in nearly every box just to show th use. This is not necessary!**

### Use of the default style
The default style defines convenient presets for the following settings:
- Font size
- Font family
- Line width
- Marker size
- Color palette
- Grid style
- Legend style


```python
import matplotlib.pyplot as plt
import numpy as np

plt.style.use("ICIWstyle")

x = np.linspace(0, 2 * np.pi, 100)

for i in range(7):
    plt.plot(x, np.sin(x + (i * (4 * np.pi / 7))), label=f"Line {i}")

plt.legend()
plt.show()
```


    
![png](examples/examples_files/examples_3_0.png)
    


In addition to the default style, the package also provides different styles to be loaded additionally. 
These can be used to 
- enable rendering of texts in LaTeX format by using `ICIWlatex`
- disable the background when exporting the plot by using `ICIWnobg`
  
The latex style automatically imports the LaTex packages `amsmath`, `amssymb`, `siunitx` and `mchem` enabling the use of all latex math commands, SI unit rendering and chemical formulas.



```python
import matplotlib.pyplot as plt
plt.style.use(["ICIWstyle", "ICIWlatex"])

x = np.linspace(0, 2 * np.pi, 100)

for i in range(7):
    plt.plot(x, np.sin(x + (i * (4 * np.pi / 7))))


plt.xlabel(r"$t$ / \unit{\second}")
plt.ylabel(r"$c$ / \unit{\mole\per\metre\cubed}")
plt.legend(
    [
        r"\ce{A}",
        r"\ce{B}",
        r"\ce{AB}",
        r"\ce{AB2}",
        r"\ce{A2Be}",
        r"\ce{C2+}",
    ]
)

plt.show()
```


    
![png](examples/examples_files/examples_5_0.png)
    


### Sizes

The package provides default size options for the following publishers:
- ACS
- Elsevier
  
To make conversion between default matplotlib units (inches) and european units (cm) easier, the package provides the following conversion factors:
- `cm2inch`
- `mm2inch`


```python
from ICIW_Plots.figures import Elsevier_Sizes, ACS_Sizes
from ICIW_Plots import cm2inch

print(
    f"Width for Elsevier default single column wide plots:\n{Elsevier_Sizes.single_column}"
)
print(
    f"Width for Elsevier default double column wide plots:\n{Elsevier_Sizes.double_column}"
)
print(
    f"width for Elsevier defaultone and a half column wide plots:\n{Elsevier_Sizes.threehalf_column}"
)

print(f"Width for ACS default single column wide plots:\n{ACS_Sizes.single_column}")
print(f"Width for ACS default double column wide plots:\n{ACS_Sizes.double_column}")

fig = plt.figure(figsize=(Elsevier_Sizes.single_column["in"], 5 * cm2inch))
ax = fig.add_axes([0, 0, 1, 1])
plt.show()
```

    Width for Elsevier default single column wide plots:
    {'mm': 90, 'in': 3.54, 'cm': 9}
    Width for Elsevier default double column wide plots:
    {'mm': 190, 'in': 7.48, 'cm': 19}
    width for Elsevier defaultone and a half column wide plots:
    {'mm': 140, 'in': 5.51, 'cm': 14}
    Width for ACS default single column wide plots:
    {'mm': 82.55, 'in': 3.25, 'cm': 8.255}
    Width for ACS default double column wide plots:
    {'mm': 177.8, 'in': 7, 'cm': 17.78}
    


    
![png](examples/examples_files/examples_7_1.png)
    


### More Sizes and Axes
Oftentimes, I like to create square axis with a fixed width in the middle of a figure with fixed width. `matplotlib` makes this hard for the user. `ICIW-Plots` provides functions `make_square_ax` and `make_rect_ax` that do this for you.


```python
plt.style.use("ICIWstyle")
from ICIW_Plots.figures import Elsevier_Sizes
from ICIW_Plots import make_square_ax

fig = plt.figure(figsize=(Elsevier_Sizes.single_column["in"], 7 * cm2inch))
ax = make_square_ax(
    fig,
    ax_width=5 * cm2inch,
)
ax.plot(x, np.sin(x))
plt.show()
```

    c:\ProgramData\Anaconda3\envs\ML3\Lib\site-packages\ICIW_Plots\layout.py:74: UserWarning: Unscientific behavior. No xlabel provided.
      warnings.warn("Unscientific behavior. No xlabel provided.")
    c:\ProgramData\Anaconda3\envs\ML3\Lib\site-packages\ICIW_Plots\layout.py:79: UserWarning: Unscientific behavior. No ylabel provided.
      warnings.warn("Unscientific behavior. No ylabel provided.")
    


    
![png](examples/examples_files/examples_9_1.png)
    


As you can see, you even get a warning when you misbehave. Both functions take some arguments you can inspect via the mouseover in your IDE. Here is just an example of what you can do although it is unreasonable to do so:


```python
plt.style.use("ICIWstyle")
from ICIW_Plots.figures import Elsevier_Sizes
from ICIW_Plots import make_square_ax

fig = plt.figure(figsize=(Elsevier_Sizes.single_column["in"], 7 * cm2inch))
ax = make_square_ax(
    fig,
    ax_width=5 * cm2inch,
    # left_h=0.2,  # These arguments control the spacing of the axis
    # bottom_v=0.2, # not supplying them wil place the axes in the middle of the figure
    xlabel=r"$t$ / \unit{\second}",
    ylabel=r"$U$ / \unit{\volt}",
    title="This is a title",
    xscale="log",
)
ax.plot(x, np.sin(x))
plt.show()
```


    
![png](examples/examples_files/examples_11_0.png)
    



```python
import matplotlib.pyplot as plt

plt.style.use("ICIWstyle")

from ICIW_Plots.figures import Elsevier_Sizes

from ICIW_Plots import make_rect_ax


fig = plt.figure(figsize=(Elsevier_Sizes.double_column["in"], 7 * cm2inch))

ax = make_rect_ax(
    fig,
    ax_width=7.3 * cm2inch,
    ax_height=5 * cm2inch,
    # left_h=0.2,  # These arguments control the spacing of the axis
    # bottom_v=0.2, # not supplying them wil place the axes in the middle of the figure
    xlabel=r"$t$ / \unit{\second}",
    ylabel=r"$U$ / \unit{\volt}",
    title="This is a title",
    xscale="log",

)
ax.plot(x, np.sin(x))
plt.show()
```


    
![png](examples/examples_files/examples_12_0.png)
    


In jupyter notebooks the output appears cut to the "appropriate" size. In a python script, you will see the full figure with all the sizes and positions spaced correctly.

### Colors

`ICIW-Plots` defines the university colors. 


```python
import matplotlib.pyplot as plt
import ICIW_Plots.colors as ICIWcolors
plt.style.use("ICIWstyle")

fig, ax = plt.subplots()

ax.plot(x, np.sin(x), color=ICIWcolors.CRIMSON)
ax.plot(x, np.cos(x), color=ICIWcolors.CERULEAN)
ax.plot(x, np.log(x + 0.1), color=ICIWcolors.KELLYGREEN)
ax.plot(x, np.tanh(x), color=ICIWcolors.FLAME)
ax.plot(x, np.arcsinh(x), color=ICIWcolors.DRAB)

plt.legend(["crimson", "cerulean", "kellygreen", "flame", "drab"])

plt.show()
```


    
![png](examples/examples_files/examples_14_0.png)
    


All colors are available as colorbars as well.
Here is just an example for the cerulean colorbar:


```python
import matplotlib.pyplot as plt
import ICIW_Plots.colors as ICIWcolors

plt.style.use("ICIWstyle")

N = 100
x = np.linspace(-3.0, 3.0, N)
y = np.linspace(-2.0, 2.0, N)

X, Y = np.meshgrid(x, y)
Z1 = -(X**2) - Y**2
Z2 = -((X * 10) ** 2) - (Y * 10) ** 2
z = Z1 + 50 * Z2

fig, ax = plt.subplots()

cs = ax.contourf(X, Y, z, cmap=ICIWcolors.cerulean_cm, levels=10)
cbar = fig.colorbar(cs)

plt.show()
```


    
![png](examples/examples_files/examples_16_0.png)
    


### Cyclers

The package defines some functionality to do your own cyclers. Supported are:
- color cyclers from colormaps
  - all default matplotlib colormaps by name
  - all custom colormaps from `ICIW-Plots` by reference
- line style cyclers
  - all default linestyles by abbreviation (`-`,`--`,`.-`,`:`)
  - every custom linestyle by a dash tuple (e.g., `(0,(3,10,1,15))`)
- marker cyclers
  - all predefined markers by abbreviation (`o`,`s`,`^`,`v`,and so on)
  - every custom marker by a marker reference
  
Custom color cyclers take a colormap and sample `num_plots` points from them equidistantly spaced. `start` and `stop` are used to prevent very light or very dark colors from being used. The `cycler` is then added as the axes `prop_cycle`.


```python
import matplotlib.pyplot as plt
import ICIW_Plots.cyclers as ICIW_cyclers

fig, ax = plt.subplots()
x = np.linspace(-2 * np.pi, 2 * np.pi)
my_green_cycler = ICIW_cyclers.ICIW_colormap_cycler("Greens", 7, start=0.2)
ax.set_prop_cycle(my_green_cycler)
for i in range(7):
    ax.plot(x, np.sin(x + (i * (4 * np.pi / 7))))
plt.show()
```


    
![png](examples/examples_files/examples_18_0.png)
    



```python
import matplotlib.pyplot as plt
import ICIW_Plots.cyclers as ICIW_cyclers

fig, ax = plt.subplots()

my_blue_cycler = ICIW_cyclers.ICIW_colormap_cycler(
    ICIWcolors.cerulean_cm,
    7,
    start=0.1,
)
ax.set_prop_cycle(my_blue_cycler)
for i in range(7):
    ax.plot(x, np.sin(x + (i * (4 * np.pi / 7))))
plt.show()
```


    
![png](examples/examples_files/examples_19_0.png)
    


custom linestyle cyclers take a list of linestyles and a number of plots to cycle through. The `cycler` is then added as the axes `prop_cycle`.


```python
my_linestyle_cycler = ICIW_cyclers.ICIW_linestyle_cycler(3)

fig, ax = plt.subplots()

ax.set_prop_cycle(my_linestyle_cycler)
for j in range(3):
    ax.plot(x, x + j * 5)
```


    
![png](examples/examples_files/examples_21_0.png)
    


Note, that all lines have the same color, since matplotlib by default cycles through its default cycler containing the colors. By overwriting the default cycler by our linestyle cycler, all lines will have the same color.

We can combine different cyclers together by either
- inner product (pairwise combinations)
- outer product (unique combinations)


```python
fig, axs = plt.subplots(1, 2)

custom_c_cycler = ICIW_cyclers.ICIW_colormap_cycler("Greens", 3, start=0.5)
custom_l_cycler = ICIW_cyclers.ICIW_linestyle_cycler(3)

axs[0].set_title("Inner Product")
# this combination gives 3 different combinations of color and line style
# linestyle 1 and color 1, linestyle 2 and color 2, linestyle 3 and color 3
axs[0].set_prop_cycle(custom_c_cycler + custom_l_cycler)
for i in range(3):
    axs[0].plot(x, np.sin(x + (i * (4 * np.pi / 5))))

axs[1].set_title("Outer Product")
# this combination gives 9 different combinations of color and line style
# linestyle 1 and color 1, linestyle 2 and color 1, linestyle 3 and color 1 and so on
axs[1].set_prop_cycle(custom_c_cycler * custom_l_cycler)
for i in range(3):
    for j in range(3):
        axs[1].plot(x, i * x + j * 5)
```


    
![png](examples/examples_files/examples_23_0.png)
    

