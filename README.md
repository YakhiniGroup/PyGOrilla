# PyGOrilla
Python wrapper for [GOrilla](http://cbl-gorilla.cs.technion.ac.il/)

GOrilla: a tool for discovery and visualization of enriched GO terms in ranked gene lists
E Eden, R Navon, I Steinfeld, D Lipson, Z Yakhini - BMC bioinformatics, 2009

## Installation:
pip install pyGOrilla

## Usage options:
  from pyGOrilla import GOrillaEvaluator
  
  GOr = GOrillaEvaluator() # note, this constructor can take parameters. See code for documentation.
  
  restable = GOrillaEvaluator.evaluate_list(genelist, outputfile (optional))
  
  GOrillaEvaluator.evaluate_file_folder(inputpath)

  
  Enjoy!
