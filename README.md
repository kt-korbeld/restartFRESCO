# restartFRESCO
A python script for rerunning cancelled FRESCO energy calculations. 

The script was written on Python 3.9.6 and makes use of numpy 1.23.3, but will likely work with older or newer versions of either.
It assumes the scripts and software required for FRESCO are properly set up and names for input or output files have not been modified. 

Running the script only requires the location of the executable as input. (This is either Foldx or Rosetta, depending on the calculations). 
Simply copy the script into the directory where the original `todolist` script is located and run the script together with the location of the executable. 
This should look something like this:

```
python3 restartFRESCO.py ~/frescoSoft/foldx5mac/foldx_20221231
```

The script generates a small bash script called `todolistRerun` which reruns the energy calculations for the missing mutations.
This new script should be run in the background by running:

```
./todolistRestart &
```
Or run with a jobscript when working on the Peregrine cluster. The script will automatically append the results of the rerun to the original output files, and the pdbs back to the original directory. It only appends the output files used by the DistributeRosetta/Foldx Phase2 scripts, but not, in the case of Foldx, the Raw_...fxout or Pdblist_...fxout files. 

The appending of the original files at the end is automatically done by the python script. The bash script calls the python script to do this once the calculations have finished. This appending step affects the original files, so if you are cautious and want to guarantee that the rerun was succesful before appending, you can turn this off by changing the variable `AUTOMATIC` to False in the script. The appending can then be run seperately by using:
```
python3 restartFRESCO.py Phase2 fx
```
for Foldx or 
```
python3 restartFRESCO.py Phase2 ro
```
for Rosetta. 

Note: When running this script on the Habrok cluster, the easiest way to make sure numpy is installed for python 3 is by loading in the scipy package, which also includes numpy:

```
module load SciPy-bundle
```
