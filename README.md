# PyGOrilla
Python wrapper for GOrilla

Usage options:
  1. python.exe pyGOrilla.py \<input filename\>
  
  Such that \<input file\> contains sorted list of gene names.
  
  2. python.exe pyGOrilla.py \<input folder\>
  
  Such that \<input folder\> contains multiple files with sorted list of gene names, where the files have a blank file extention (e.g. "filename.").
  
  3. In python code:
  
  from pyGOrilla import GOrillaEvaluator
  
  GOr = GOrillaEvaluator() # note, this constructor can take parameters. See code for documentation.
  
  restable = GOrillaEvaluator.evaluate(genelist, outputfile)
  
  
  Enjoy
