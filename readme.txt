=================================================
= MIREX SUBMISSION 2016 *** KEY ESTIMATION TASK =
=================================================

Algorithm name: edmkey_1
    
Authors:        Ángel Faraldo, Emilia Gómez, Sergi Jordà, 
                Martin Hermant, Perfecto Herrera. 

Submitted by:   Ángel Faraldo, PhD Student
                Music Technology Group, 
                Universitat Pompeu Fabra
                Roc Boronat 138
                08018 Barcelona
                Spain

Contact:        angel.faraldo@upf.edu



DEPENDENCIES
============

In order to run this algorithm you need:

- Python 2.7
  ----------

- Numpy
  -----
  In Ubuntu, it should be as easy as typing:
  
    $ sudo apt-get install python-numpy

- Essentia
  -------- 
  You need a special fork of essentia containing the modified
  key estimation algorithms:

    <http://www.github.com/angelfaraldo/essentia>



STEPS PRIOR TO RUNNING THE ALGORITHM:
====================================

1) If you do not have the file "edmkey.zip," you can download it 
   from <http://www.github.com/angelfaraldo/edmkey/tree/submission1>

2) Once you have the zip file, you can move it to a convenient
   location and extract its contents.

3) Then, enter the edmkey directory.


    $ mv '/home/user/Downloads/edmkey.zip' '/home/user/edmkey.zip'
    $ cd ~
    $ unzip edmkey.zip
    $ cd edmkey


RUNNING THE ALGORITHM:
=====================

For a regular, file by file analysis, as advised in the Mirex 2016 Wiki, 
once in the edmkey folder, you should type the following line, where 
%input is the full path to an audio file %output is the full path of a
textfile that will be created with the key estimation:


    $ python edmkey.py %input %output


However, if you have the audio files on a single directory, you can call
the algorithm with the --batch_mode [-b] option, and the program will analyse
all audio files inside the input subfolder and it will create homonym textfiles
on the specified output subfolder. If the output directory does not exist,
it will create one.


    $ python edmkey.py -b %input_dir %output_dir


If you want to see the progress of the analysis on the command line,
you can call the algorithm with the --verbose [-v] flag:


    $ python edmkey.py -v -b %input_dir %output_dir
    
    or
    
    $ python edmkey.py -v %input %output
 

At any moment, you can access help on the command line with the --help flag:

    $ python edmkey.py -h 

    usage: edmkey.py [-h] [-b] [-v] input output

    Key Estimation Algorithm

    positional arguments:
      input             file (dir if in --batch_mode) to analyse
      output            file (dir if in --batch_mode) to write results to

    optional arguments:
      -h, --help        show this help message and exit
      -b, --batch_mode  batch analyse a whole directory
      -v, --verbose     print progress to console


