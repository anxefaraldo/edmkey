=================================================
  MIREX SUBMISSION 2016 *** KEY ESTIMATION TASK 
=================================================

Algorithm name: edmkey
    
Authors:        Ángel Faraldo, Emilia Gómez, Sergi Jordà, 
                Martin Hermant, Perfecto Herrera. 

Submitted by:   Ángel Faraldo, PhD Student
                Music Technology Group, 
                Universitat Pompeu Fabra
                Roc Boronat 138
                08018 Barcelona
                Spain

Contact:        angel.faraldo@upf.edu


PACKAGE DESCRIPTION
===================

We provide a zip folder containing this readme file, an executable file
and a subfolder 'dist' containing all the libraries and dependencies. 
These are built statically and are provided within the zip, so you should
not worry about installing or compiling additional sources, as well as 
about messing with other uncompatible versions. 

We have tested the executable on a fresh install of Ubuntu 16.10 (x86_64)
Should you experience any problems running the algorithm, please do not 
hesitate to contact us.
   

STEPS PRIOR TO RUNNING THE ALGORITHM:
====================================

1) If you do not have the file "edmkey.zip," you can download it 
   from <http://www.github.com/angelfaraldo/edmkey/tree/submission1>

2) Once you have the zip file, you can move it to a convenient
   location and extract its contents.
   
3) Last, access the edmkey directory.


    $ mv '/home/user/Downloads/edmkey.zip' '/home/user/edmkey.zip'
    $ cd ~
    $ unzip edmkey.zip
    $ cd edmkey


RUNNING THE ALGORITHM:
=====================

For a regular, file by file analysis, as advised in the MIREX 2016 Wiki, 
once in the edmkey folder, you should type the following line (where 
%input is the full path to an audio file and %output is the full path of a
textfile that will be created with the key estimation):


    $ ./edmkey %input %output


However, if you have all your audio files on a single directory, you can call
the algorithm with the --batch_mode [-b] option, and the program will analyse
all audio files inside the input subfolder and it will create homonym textfiles
on the specified output subfolder. If the output directory does not exist,
it will create one:


    $ ./edmkey -b %input_dir %output_dir


If you want to see the progress of the analysis on the command line,
you can call the algorithm with the --verbose [-v] flag:


    $ ./edmkey -v -b %input_dir %output_dir
    
    or
    
    $ ./edmkey -v %input %output
 

At any moment, you can obtain some help on the command line with the --help flag:


    $ ./edmkey -h 

    usage: edmkey.py [-h] [-b] [-v] input output

    Key Estimation Algorithm

    positional arguments:
      input             file (dir if in --batch_mode) to analyse
      output            file (dir if in --batch_mode) to write results to

    optional arguments:
      -h, --help        show this help message and exit
      -b, --batch_mode  batch analyse a whole directory
      -v, --verbose     print progress to console
      
      
