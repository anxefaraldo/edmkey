## FkeyEDM (MIREX 16 submission)

Algorithm for automatic key detection in EDM.

### Dependencies

In order to run or compile the algorithm you need.

- Python >= 2.6
- Numpy >= 
- Essentia (http://essentia.upf.edu/)

Detailed instructions to build essentia can be found on the essentia site:

*http://essentia.upf.edu/documentation/installing.html*

### Compiling as executable

The script can be compiled onto an executable using pyinstaller. You can install it via pip,

$ pip install pyinstaller

and then, in the FkeyEDM folder, generate the executable with the following command:

$ pyinstaller FkeyEDM.py

The new FkeyEDM executable will be located in './dist/FkeyEDM'


### Extras

Additionally, we provide a simple python script to evaluate the results of the algorithm according to the MIREX competition.
