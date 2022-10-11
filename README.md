# restartFRESCO
A python script for rerunning cancelled FRESCO energy calculations. 

Copy the script into the directory where the original todolist script is located. 
The only input it requires is the location of the executable (either foldx or rosetta, depending on the calculations). 
This should look like:

```
python restartFRESCO.py ~/frescoSoft/foldx5mac/foldx_20221231
```

Like FRESCO itself, the script generates a small bash script called `todolistRerun` which reruns the energy calculations for the missing mutations.
The script will automatically append the results of the rerun to the original output files. This script should be run in the background by running:

```
./todolistRestart &
```

It only appends the output file used by the DistributeRosetta/Foldx Phase2 scripts, but not, in the case of Foldx, for the Raw_...fxout or Pdblist_...fxout files. The script requires the numpy library to be installed, and in order for the todolistRerun script to work, python must callable with the allias 'python', which might cause an error if python is callable with 'python3' instead. 

