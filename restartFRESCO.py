import os, sys
import numpy as np
import shutil

#set to true to get more information
DEBUG = False
#set to true to automatically append results to original output file
AUTOMATIC = True
#one can add additional flags to the todolist if neccesary
FXFLAGS = []
ROFLAGS = []

#define functions
#---------------------------------------------------------------------------------------------------------------------------

def ReadFile(filename):
    '''
    takes in file and returns a list
    with all lines in the file
    '''
    with open(filename) as file:
        #skip first line to get all data
        return file.read().splitlines()

def CheckError(conditional, errormessage):
    '''
    Takes in conditional statement (Bool) and error message (str).
    Prints error message and quits if conditional is True
    '''
    #print message and end script if condition is met
    if conditional:
        print('-------- ERROR -------- '+errormessage)
        sys.exit()

def CheckFileExtension(name, extension):
    '''
    takes in a filename (str) and list of expected extensions (list),
    adds correct extension if filename misses extension,
    and checks for correct extension if the filename has an extension
    '''
    #only split the last occurrence of '.', i.e the file extension
    name = name.rsplit('.', 1)
    #if no extension, use first in list of allowed extensions
    if len(name) == 1:
        return '.'.join([name[0],extension[0]])
    #if allowed extension, use that extension
    elif len(name) == 2 and name[1] in extension:
        return '.'.join(name)
    #if no allowed extension, give error
    else:
        CheckError(True, '.{} file {} does not have allowed extensions {}'.format(extension[0], '.'.join(name), extension))

def MatchFile(directory, expressions):
    '''
    read all files in a given directory and
    checks if it matches a list of expressions
    returns the first match
    '''
    content =  os.listdir('./{}/'.format(directory))
    for file in content:
        containsall =  all([(i in file) for i in expressions])
        if containsall:
            return file
    return ''

# read input and get list of directories
#---------------------------------------------------------------------------------------------------------------------------

#initializing some variables
fx_or_ro = ''
execloc = ''
reruns = 0

if DEBUG:
    print(sys.argv)

CheckError(len(sys.argv) < 2, 'No arguments were given.')
#check if set to phase2, and assign variables accordingly
if sys.argv[1] == 'Phase2':
    fx_or_ro = sys.argv[2]
#if set to phase1, only argument should be the directory of rosetta or foldx executable
elif 'foldx' in sys.argv[1].lower() and os.path.exists(sys.argv[1]):
    CheckFileExtension(sys.argv[1], ['pdb', 'ent', 'brk'])
    execloc = sys.argv[2]
    fx_or_ro = 'fx'  
elif 'ddg_monomer' in sys.argv[1].lower() and os.path.exists(sys.argv[1]):
    CheckFileExtension(sys.argv[1], ['pdb', 'ent', 'brk'])
    execloc = sys.argv[2]
    fx_or_ro = 'ro'
else:
    CheckError(True, 'no executable for either Foldx or Rosetta was found')

#figure out how many subdirectories there are
dir_list = os.listdir('.')
subdir_list = [i for i in dir_list if 'Subdirectory' in i]
subdir_list.sort()
CheckError(len(subdir_list) == 0, 'no directories called Subdirectory were present')
print('found {} directories called Subdirectory'.format(len(subdir_list)))
print('\n')

#check for Phase2 before doing the rest of the script
if sys.argv[1] == 'Phase2':
    for subdir in subdir_list:
        if fx_or_ro == 'fx':
            # Check if a Rerun folder exists
            subdir_content = os.listdir('./{}/'.format(subdir))
            if not any('Rerun' in element for element in subdir_content):
                continue
                
            #read output from rerun
            rerundir = '{0}/Rerun{0}/'.format(subdir)
            outfile = MatchFile(rerundir, ['Average', '.fxout'])
            out = ReadFile(rerundir+outfile)[9:]
            difrerun = len(ReadFile(subdir + '/' + outfile)[9:])
            #split off filename and increase by given amount
            newname = np.array([i.split('\t', 1)[0].rsplit('_', 1) for i in out])
            newname[:,1] = newname[:,1].astype(int)+difrerun
            newname = np.char.add(np.char.add(newname[:, 0], len(newname) * ['_']), newname[:, 1])
            #combine data with renamed filename
            newdata = np.array([i.split('\t', 1)[1] for i in out])
            newout = np.char.add(np.char.add(newname, len(newdata)*['\t']), newdata)
            newout = np.char.add(newout, len(newout)*['\n'])
            #write to original output file
            with open('./{}/{}'.format(subdir, outfile), 'a') as file:
                file.writelines(newout)
            print('adding missing mutants to Foldx output file in {}'.format(subdir))
            
            #copy all new pdbs into original directory
            pdblist = MatchFile(rerundir, ['_', '.pdb'], givefirst=False)
            for pdb in pdblist:
                #split pdb name by underscore, get new name with proper count, annd move
                splitpdb = pdb.rsplit('_', 2)
                if len(splitpdb) >= 3:
                    newpdb = splitpdb[0]+'_'+str(int(splitpdb[1])+difrerun)+'_'+splitpdb[2]
                    shutil.move('{0}/{1}'.format(rerundir, pdb), '{0}/{1}'.format(subdir, newpdb))
                    if DEBUG:
                        print(pdb, ' renamed to ', newpdb)
            print('moved and renamed pdb files in {}'.format(subdir))
            
        elif fx_or_ro == 'ro':
            # Check if a Rerun folder exists
            subdir_content = os.listdir('./{}/'.format(subdir))
            if not any('Rerun' in element for element in subdir_content):
                continue
                
            #read output from rerun
            rerundir = '{0}/Rerun{0}/'.format(subdir)
            outfile = 'ddg_predictions.out'
            out = ReadFile(rerundir+outfile)[1:]
            newout = np.char.add(out, len(out)*['\n'])
            #write to original output file
            with open('./{}/{}'.format(subdir, outfile), 'a') as file:
                file.writelines(newout)
            print('adding missing mutants to Rosetta output file in {}'.format(subdir))
        else:
            CheckError(True, 'Neither fx or ro was specified for Phase2')
    print('Rerun complete!')
    sys.exit()
   
#initialize list of lines that will eventually be written to a new todolist script
todolist = []

#giant for loop going over each directory and setting up the files/directories for a rerun
#---------------------------------------------------------------------------------------------------------------------------
for subdir in subdir_list:

    #read mutant file for Rosetta
    if os.path.exists('./{}/RosettaFormatMutations.mut'.format(subdir)):
        #check if this file should even exist and read data into list
        if fx_or_ro == 'fx':
            print('Found a Rosetta mutant file in {}, but specified executable is for Foldx'.format(subdir))
            print('\n')
            continue
        print('Found a Rosetta mutant file in {}'.format(subdir))
        mut_in = ReadFile('./{}/RosettaFormatMutations.mut'.format(subdir))[1:]
        #get the the nr of subunits given in mut file between each mutation by looking for all lines of 1 char long.
        subunits = list(set([int(i) for i in mut_in if len(i) == 1]))[0]
        #get an array of mutants by taking all lines longer than 1 char and removing the whitespaces
        mut_in = np.array([i.replace(' ', '') for i in mut_in if len(i) > 1])
    
    #read mutant file for Foldx
    elif os.path.exists('./{}/individual_list.txt'.format(subdir)):
        #check if this file should even exist and read data into list
        if fx_or_ro == 'ro':
            print('Found a Foldx mutant file in {}, but specified executable is for Rosetta'.format(subdir))
            print('\n')
            continue
        print('Found a Foldx mutant file in {}'.format(subdir))
        mut_in = ReadFile('./{}/individual_list.txt'.format(subdir))
        #get all unique subunit names for each mutant on each line
        subunits = list(set(np.array([[j[1] for j in i.split(',')] for i in mut_in]).flatten()))
        subunits.sort()
        #split entry for each subunit into list, only take first one, and take only resnr and amino acid.
        mut_in = np.array([i.split(',')[0][0]+i.split(',')[0][2:] for i in mut_in])
    
    #skip directory if no mutant file exists
    else:
        print('{} does not contain an mutant file from either Rosetta or Foldx'.format(subdir))
        print('\n')
        continue
    
    #Read output file for Rosetta
    if os.path.exists('./{}/ddg_predictions.out'.format(subdir)):
        #check if this file should even exist and read data into list
        if fx_or_ro == 'fx':
            print('Found a Rosetta output file in {}, but specified executable is for Foldx'.format(subdir))
            print('\n')
            continue
        print('Found a Rosetta output file in {}'.format(subdir))
        energy_list = ReadFile('./{}/ddg_predictions.out'.format(subdir))
        #skip first line for rosetta output, and ignore empty lines
        energy_list = [i.split() for i in energy_list[1:] if len(i)> 1]
        #output file contains res names of calculated mutants, so take this column
        mut_out = np.array(energy_list)[:, 1]
    
    #Read output file for Foldx'
    elif len(MatchFile(subdir, ['Average', '.fxout'])) != 0:
        #check if this file should even exist and read data into list
        if fx_or_ro == 'ro':
            print('Found a Foldx output file in {}, but specified executable is for Rosetta'.format(subdir))
            print('\n')
            continue
        print('Found a Foldx output file in {}'.format(subdir))
        energy_list = ReadFile('./{}/{}'.format(subdir, MatchFile(subdir, ['Average', '.fxout'])))
        #skip first 9 lines for foldx output, these are header + column names
        energy_list = [i.split() for i in energy_list[9:]]
        # output file does not contain res names, so get indices from pdb names and use on mut_in
        mut_out = mut_in[np.array([int(i[0].rsplit('_')[-1])-1 for i in energy_list])]
    
    #skip directory if no output files are present
    else:
        print('{} does not contain an output file from either Rosetta or Foldx'.format(subdir))
        print('\n')
        continue

    #get the missing mutants by taking the set difference between muts in and out
    missingmuts = mut_in[~np.isin(mut_in, mut_out)]
    if DEBUG:
        print('in:\n', mut_in)
        print('out\n', mut_out)
        print('missing\n,', missingmuts)
    
    #print some information
    print('Found {} mutations, of which {} have been calculated'.format(len(mut_in), len(mut_out)))
    if len(missingmuts) == 0:
        print('No missing mutations in {} have been found'.format(subdir))
        print('\n')
        continue
    else:
        print('{} mutations are missing in {}'.format(len(missingmuts), subdir))
        reruns+=1

    #create directory for rerun files
    if not os.path.exists('./{0}/Rerun{0}'.format(subdir)):
        os.mkdir('./{0}/Rerun{0}'.format(subdir))
    else:
        print('Rerun{} already exists, new files will overwrite existing files with the same name'.format(subdir))

    #if foldx, copy or create all files required for a rerun in new directory
    if fx_or_ro == 'fx':
        #make backup of original output file 
        shutil.copy('./{0}/{1}'.format(subdir, MatchFile(subdir, ['Average', '.fxout'])), './{0}/Average_backup.fxout'.format(subdir))
        shutil.copy('./{0}/rotabase.txt'.format(subdir), './{0}/Rerun{0}/rotabase.txt'.format(subdir))
        shutil.copy('./{0}/list.txt'.format(subdir), './{0}/Rerun{0}/list.txt'.format(subdir))
        shutil.copy('./{0}/{1}'.format(subdir, pdbname), './{0}/Rerun{0}/{1}'.format(subdir, pdbname))
        #write out the missing mutations in the right format
        with open('./{0}/Rerun{0}/individual_list.txt'.format(subdir), 'w') as listfile:
            new_individuallist = []
            for mut in missingmuts:
                #add mutant for each subunit
                new_muts = [str(mut[0])+str(sub)+str(mut[1:].replace(';', '')) for sub in subunits]
                #join into writable string
                new_muts = ','.join(new_muts)+';\n'
                new_individuallist.append(new_muts)
            listfile.writelines(new_individuallist)
        #add lines to todolist
        todolist.append('cd {0}/Rerun{0}/\n'.format(subdir))
        todolist.append('{0} --command=BuildModel --pdb={1}  --mutant-file=individual_list.txt '
                        '--numberOfRuns=5 {} > LOG&\n'.format(execloc, pdbname, ' '.join(FXFLAGS)))
        todolist.append('cd ../..\n')

    #if rosetta, copy or create all files required for a rerun in new directory
    if fx_or_ro == 'ro':
        #make backup of original output file 
        shutil.copy('./{0}/ddg_predictions.out'.format(subdir), './{0}/ddg_predictions_backup.out'.format(subdir))
        print('Found pdb in LOG file: {0}'.format(pdbname))
        shutil.copy('./{0}/FLAGrow3'.format(subdir), './{0}/Rerun{0}/FLAGrow3'.format(subdir))
        shutil.copy('./{0}/{1}'.format(subdir, pdbname), './{0}/Rerun{0}/{1}'.format(subdir, pdbname))
        #write out the missing mutations in the right format
        with open('./{0}/Rerun{0}/RosettaFormatMutations.mut'.format(subdir), 'w') as mutfile:
            new_muts = []
            new_muts.append('total {0}\n'.format(subunits*len(missingmuts)))
            for mut in missingmuts:
                #add nr of subunits
                new_muts.append(str(subunits)+'\n')
                #add mutants
                new_muts.append(subunits*'{0} {1} {2}\n'.format(mut[0], mut[1:-1], mut[-1]))
            mutfile.writelines(new_muts)
        #add lines to todolist
        todolist.append('cd {0}/Rerun{0}/\n'.format(subdir))
        todolist.append('{0} @FLAGrow3 -in:file:s {1} -ddg::mut_file '
                        'RosettaFormatMutations.mut {2} >LOG&\n'.format(execloc, pdbname, ' '.join(ROFLAGS)))
        todolist.append('cd ../..\n')
    
    #for clarity, print whiteline between each directory
    print('\n')

# writing the todolistRerun file
#---------------------------------------------------------------------------------------------------------------------------
print('All directories have been checked for missing mutants.')

todolist.append('wait\n')
if AUTOMATIC:
    todolist.append('python3 {0} Phase2 {1}\n'.format(sys.argv[0], fx_or_ro))

#write everything to the new todolist script
with open('./todolistRerun', 'w') as todo:
    todo.writelines(todolist)

os.chmod("./todolistRerun", 0o777)

print('In total {} out of {} directories have missing mutants'.format(reruns, len(subdir_list)))
print('A new script called \'todolistRerun\' has been created in order to start the missing calculations ')
print('Run this script in the background using \'./todolistRerun &\'')
print('After the calculations finish it will automatically add the results to the original output files')
