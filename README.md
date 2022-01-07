# About
- pvpython postprocessor for bubble dynamics simulations
- Created to process the output of [ALPACA](https://gitlab.lrz.de/nanoshock/ALPACA) bubble simulations
- Compatible with [paraview](https://www.paraview.org/) 5.8.0
- Created by Daniel Nagy (Technical University of Budapest, [Sonochemistry Research Group](https://www.hds.bme.hu/research/BubbleDynamics/index.html))

# Versions
### 2D planar postprocessor 1.8 (`postprocessor.py`)
- Model: Circular bubbles

### 2D axisymmetric postprocessor 1.1 (`postprocessorAxis.py`) 
- Model: Axisymmetric bubble (symmetry is the y-axis)

### 3D postprocessor 1.0 (`postprocessor3D.py`) 
- Model: 3D bubbles

# Usage
`pvpython postprocessor.py inputfolder outputfolder`
- `postprocessor.py` could be any of the 3 scripts
- `inputfolder` ALPACA output folder, `.xdmf` files are searched under `inputfolder/domain/*.xdmf`
- `outputfolder` the folder where the output of the postprocessor is saved, `data.csv` is always saved under `outputfolder/data.csv`

## Optional arguments
- `--debug` prints debug information
- `--savewave pos` save the standing wave data (pressure, density, velocity) at the specified position. This generates extra output files (e.g. `wavePressureMiddle.csv`)
  -  `top` saves the data at the top of the domain
  -  `middle` saves the data at the middle of the domain
  -  `bottom` saves the data at the bottom of the domain
  -  `all` saves the data at all the previous positions
-  `--savepics` saves an image of the bubble in each step, image saved at `outputfolder/pics_#step.png`
-  `--pmin val` specifies the bottom of the pressure color bar on the saved image (e.g. `--pmin 0.5e5` sets the color bar min. to 0.5 bar)
-  `--pmax val` specifies the top of the pressure color bar on the saved image (e.g. `--pmax 1.5e5` sets the color bar max. to 1.5 bar)
-  `--nosavedata` does not create the `data.csv` file (can be used just to save the standing wave)
-  `--version` prints the current version

## Output

### `data.csv`
Contains the important bubble quantities for each timestep
- Column 1: step, the actual step number
- Column 2: time, the time instance of the step
- Column 3: bubble pressure
- Column 4: bubble density
- Column 5: bubble volume (model corrigated)
- Column 6: bubble radius (along x axis)
- Column 7: bubble radius (along y axis)
- Column 8: inlet pressure
- Column 9: inlet density
- Column 10: bubble mass (model corrigated)

### `wave*.csv`
Contains the information of the standing wave (e.g. PressureMiddle refers to the pressure wave at the middle of the domain). 
- Row 1: sampling positions
- Column 1: sampling time instances
- Row *i*, Column *j*: field variable at the *i-1*th time instance at the *j-1*th position
