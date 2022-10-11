# restartFRESCO
A python script for rerunning cancelled FRESCO energy calculations. 

The script makes use of the numpy library for python.
Other than that it assumes the scripts and software required for FRESCO are properly set up. 

The only input is the location of the executable. (This is either Foldx or Rosetta, depending on the calculations). 
Simply copy the script into the directory where the original `todolist` script is located and run the script together with the location of the executable. 
This should look something like this:

```
python restartFRESCO.py ~/frescoSoft/foldx5mac/foldx_20221231
```

The script generates a small bash script called `todolistRerun` which reruns the energy calculations for the missing mutations.
This new script should be run in the background by running:

```
./todolistRestart &
```

The script will automatically append the results of the rerun to the original output files.
It only appends the output files used by the DistributeRosetta/Foldx Phase2 scripts, but not, in the case of Foldx, the Raw_...fxout or Pdblist_...fxout files. 

The appending of the original files at the end is also done by the python script. The bash script simply calls the python script to do this once the calculations have finished. If the calculations finish but this last appending step goes wrong, you can manually run this part of the script using:
```
python restartFRESCO.py Phase2 fx
```
for Foldx or 
```
python restartFRESCO.py Phase2 ro
```
for Rosetta.
