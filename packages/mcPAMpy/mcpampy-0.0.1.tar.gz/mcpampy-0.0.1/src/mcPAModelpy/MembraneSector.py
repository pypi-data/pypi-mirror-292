import math
from warnings import warn
from copy import copy, deepcopy
from cobra import Object

from .configuration import Config
from .EnzymeSectors import EnzymeSector


class MembraneSector(EnzymeSector):
    # class with all the information on the cell membrane and memrbane proteins
    def __init__(
            self,
            area_avail_0, #μm2
            area_avail_mu, #μm2/h
            alpha_numbers_dict: {},
            enzyme_location: {},
            configuration=Config):

        self.id = 'membrane'
        self.area_avail_0 = area_avail_0[0]  # amount of the available membrane area at zero growth [μm2]
        self.area_avail_mu = area_avail_mu[0] # increase in membrane area per growth rate unit [μm2*h] (the slope)
        self.alpha_numbers_dict = alpha_numbers_dict # a dictionary containing proteins with uniprotID and the associated transmembrane segment information in the form of alpha helix number
        self.enzyme_location = enzyme_location # a dictionary containing the subcellular location for each protein
        self.area_alpha = math.pi * math.pow((0.0046 / 2), 2)  # area per alpha helix unit [um]
        self.cdw_per_cell = 0.28 * 1e-12 # dry weight of a single cell 0.28 pg
        self.n_a = 6.02 * 1e23 # avogadro number
        self.max_membrane_area = 0.57 # percentage of membrane area that is available for membrane proteins
        self.unit_factor = 1e-3 * self.cdw_per_cell * self.n_a # factor for conversion from [mmol/gcdw] (enyzme concentration) to [μm2] (membrane area)

        #Defining the slope and intercept
        self.intercept = self.area_avail_0 #μm2
        self.slope = self.area_avail_mu #μm2/h

    def add(self, model):
        self.model = model
        print("Add membrane protein sector \n")
        model.add_membrane_constraint()
        model.membrane_sector = self
        return model


