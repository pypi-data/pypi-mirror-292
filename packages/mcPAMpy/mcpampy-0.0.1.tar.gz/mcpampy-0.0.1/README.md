# mcPAModelpy - membrane-constrained Protein Allocation Model reconstruction in Python

## What is mcPAModelpy?
mcPAModelpy is an extension of the basic framework PAModelpy - powertools to explore the metabolic potential of microorganism.
mcPAModelpy possess the basic features of PAModelpy such as:
- protein-reaction associations
- infrastructure to include isoenzymes and promiscuous enzymes
- protein sectors
- specialized objects to build protein allocation models
- the possibility to perform a computatinal efficient sensitivity analysis

**AND** the possibility to include a membrane sector to the model. 

The addition of membrane sector would allow the user to constraint the model further by limiting the space where membrane
proteins are located, hence more accuracy in the model's prediction. 

## Installation
PAModelpy is a PiPy package which allows for easy installation with pip:

pip install mcPAModelpy

Note that the package has been tested with the Gurobi selver

## Code structure:
- EnzymeSectors: The objects which are used to store the data of the different enzyme sectors which are added to the
genome-scale model
- PAModel: Proteome Allocation (PA) model class. 
This class builds on to the cobra.core.Model class from the COBRApy toolbox with functions to build enzyme sectors, to add enzyme kinetics parameters and in the future to perform a sensitivity analysis on the enzyme variables.
- Enzyme: Different classes which relate enzymes to the model with enzyme constraints and variables.
- CatalyticEvent: A class which serves as an interface between reactions and enzyme. 
This allows for easy lookup of Protein-Reaction assocations.
- PAMValidator: Functions to validate the model predictions with physiology data 
and giving a graphical overview. The script uses data for E.coli (found in ./Data/Ecoli_physiology) by default.
- **NEW** MembraneSector: An object which is used to store the data of the cell membrane and membrane proteins which are
added to the genome-scale model.

## Enzymatic and sectors data 
Enzymatic and sectors data are stored inside an excel data 
named 'mcPAM_iML1515_EnzymaticData.xlsx'

## Tutorial
### Import statements
To build a mcPAModel, all import statements from the original PAModel need to be included:

```
#importing the packages and scripts

import os
from cobra.io import read_sbml_model, load_matlab_model
import sys
import pandas as pd

#load PAMpy modules
from PAModelpy.EnzymeSectors import ActiveEnzymeSector, TransEnzymeSector, UnusedEnzymeSector
from PAModelpy.PAModel import PAModel
from PAModelpy.PAMValidator import PAMValidator
from PAModelpy.configuration import Config
```

Additionally, an import statements for the MembraneSector needs to be included:

`from mcPAModelpy.MembraneSector import MembraneSector`

### Building a mcPAModel 
The first step of building a mcPAModel includes building the original sectors (active, unused, and translational sectors) as described in 

https://github.com/iAMB-RWTH-Aachen/PAModelpy/blob/main/Examples/PAModel_example_script.ipynb

In a similar manner as the other sectors, the membrane sector is built as described below:


```
# building membrane sector 
enzyme_info_path = 'insert the path where "mcPAM_iML1515_EnzymaticData" is stored'
membrane_info = pd.read_excel(enzyme_info_path, sheet_name='Membrane')

area_avail_0 = membrane_info[membrane_info.Parameter == 'area_avail_0'].loc[1,'Value']
area_avail_mu = membrane_info[membrane_info.Parameter == 'area_avail_mu'].loc[2,'Value']
alpha_numbers_dict = active_enzyme_info.set_index(keys='uniprotID').loc[:, 'alpha_numbers'].to_dict()
enzyme_location = active_enzyme_info.set_index(keys='uniprotID').loc[:, 'Location'].to_dict()
cog_class = active_enzyme_info.set_index(keys='uniprotID').loc[:, 'COG_group'].to_dict()

membrane_sector = MembraneSector(area_avail_0=[area_avail_0],
                                 area_avail_mu=[area_avail_mu],
                                 alpha_numbers_dict=alpha_numbers_dict,
                                 enzyme_location=enzyme_location)
```

After the sectors are built, mcPAM with the genome-scale information 
and the information about the enzyme and membrane sectors are loaded:

```
pamodel = PAModel(id_or_model=model,
                   p_tot=0.258,
                   active_sector=active_enzyme_sector,
                   translational_sector=translation_enzyme_sector,
                   unused_sector=unused_protein_sector,
                   membrane_sector=membrane_sector,
                   sensitivity = True,
                   configuration=config
                   )
```
## License
Copyright institute of Applied Microbiology, RWTH Aachen University, Aachen, Germany (2023)

PAModelpy is free of charge open source software, which can be used and modified for your particular purpose under the MIT or Apache 2.0 of the users choice.

Please note that according to these licenses, the software is provided 'as is', WITHOUT WARRANTY OF ANY KIND, without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.