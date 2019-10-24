# PyGOrilla
Python wrapper for [GOrilla](http://cbl-gorilla.cs.technion.ac.il/)

GOrilla: a tool for discovery and visualization of enriched GO terms in ranked gene lists
E Eden, R Navon, I Steinfeld, D Lipson, Z Yakhini - BMC bioinformatics, 2009

## Usage options:
  1. python.exe pyGOrilla.py \<input filename\>
  
  Such that \<input file\> contains sorted list of gene names.
  
  2. python.exe pyGOrilla.py \<input folder\>
  
  Such that \<input folder\> contains multiple files with sorted list of gene names, where the files have a blank file extention (e.g. "filename.").
  
  3. In python code:
  
  from pyGOrilla import GOrillaEvaluator
  
  GOr = GOrillaEvaluator() # note, this constructor can take parameters. See code for documentation.
  
  restable = GOrillaEvaluator.evaluate(genelist, outputfile)
  
  
  Enjoy
