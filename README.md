<img src="docs/images/logo.jpeg">

Based on [ROOT](https://ph-root-2.cern.ch/) [RDataFrame](https://root.cern/doc/master/classROOT_1_1RDataFrame.html), NTupro is an innovative Python package which takes care of optimizing HEP analyses.  

## Motivation
Cut-based analyses in HEP foresee a series of operations that are more or less common:

* a dataset is accessed;
* cuts are performed on one or more variables;
* the variables of interest, whose events passed the above mentioned selections, are plotted.

This series of operations make what we can call a minimal analysis flow unit. In a typical HEP analysis, given the amount of datasets, cuts and plots that we want to produce, we have to handle hundreds of thousands of these units. Two basic examples of analysis units are here shown.
<img src="docs/images/basic_units.png">
To produce their results, many physicists use the so called [TTree::Draw](https://root.cern.ch/doc/master/classTTree.html) approach: it is simple because it allows not to write the **event loop** explicitly, but it has the drawback that the analysis units are run *sequentially*. This leads to the following weak spots:

* same datasets (e.g. Dataset-X above) are fetched and decompressed multiple times;
* same subsets of cuts (e.g. Selection-A above) are applied many times on different datasets;
* the event loop is run once per histogram.

Implementing a clean and friendly API to [RDataFrame](https://root.cern/doc/master/classROOT_1_1RDataFrame.html), NTupro allows to write minimal analysis flow units and automatically optimizes them, performing common operations only once, like in the following.
<img src="docs/images/optimized_basic_units.png">
  
## Structure  
  
## Examples  
  
## Tests  
Before merging, check that all the tests are green by running  
  
```bash  
$ python -m unittest -v  
```
