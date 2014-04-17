import ROOT
from math import sqrt, tanh

##########################################################################################
# Pixel match window                                                                     #
##########################################################################################

def is_barrel(subDet):
    return (subDet==1)

class event:
    def __init__(self):
        self.electrons       = []
        self.tag_electrons   = []
        self.probe_electrons = []
    def passes_selections(self, window, region):
        for p_el in self.probe_electrons:
            if self.probe_electrons[i].passes_selections(window, region):
                return  True
        return False

class electron_object:
    def __init__(self, p4_in):
        self.phi1  = 0.0
        self.phi2  = 0.0
        self.dRz1   = 0.0
        self.dRz2   = 0.0
        self.charge = 0.0
        self.index  = -1
        self.helices = []
        self.is_tagged = False
        self.p4 = p4_in
    def add_helix(self, helix_in):
        self.helices.append(helix_in)
    def has_region(self, region):
        for helix in self.helices:
            if helix.region == region:
                return True
        return False
    def passes_selections(self, window, region):
        for helix in self.helices:
            result = helix.passes_selections(window, False)
            if region!='':
                result = (result and helix.region==region)
            if result:
                return True
        return False

    def calculate_charge(self):
        n_pos = 0
        n_neg = 0
        for helix in self.helices:
            if helix.charge>0:
                n_pos = n_pos + 1
            else:
                n_net = n_neg + 1
        if len(self.helices)==0:
            self.charge = 0
        elif n_pos > n_neg:
            self.charge =  n_pos/(n_pos+n_neg)
        elif n_neg > n_pos:
            self.charge = -n_neg/(n_pos+n_neg)
        else:
            self.charge = 0
        self.pick_best_helix()
        return self.charge

    def pick_best_helix(self):
        best_s = 1e6
        best_helix = False
        for helix in self.helices:
            if helix.s < best_s:
                best_s = helix.s
                best_helix = helix
        return best_helix

class electron_helix:
    def __init__(self, dPhi1_in, dPhi2_in, dRz1_in, dRz2_in, s2_in, charge_in, subDet1_in, subDet2_in):
        self.phi1    = dPhi1_in
        self.phi2    = dPhi2_in
        self.rz1     = dRz1_in
        self.rz2     = dRz2_in
        self.charge  = charge_in
        self.subDet1 = subDet1_in
        self.subDet2 = subDet2_in
    
        # Choose values based on sub detectors
        # Return 0 if the variable is not relevant (so that they always pass irrelevant selections)
        self.z1B = self.rz1 if(    is_barrel(self.subDet1) and     is_barrel(self.subDet2)) else 0
        self.r1I = self.rz1 if(    is_barrel(self.subDet1) and not is_barrel(self.subDet2)) else 0
        self.r1F = self.rz1 if(not is_barrel(self.subDet1) and not is_barrel(self.subDet2)) else 0
        
        self.z2B = self.rz2 if(    is_barrel(self.subDet1) and     is_barrel(self.subDet2)) else 0
        self.r2I = self.rz2 if(    is_barrel(self.subDet1) and not is_barrel(self.subDet2)) else 0
        self.r2F = self.rz2 if(not is_barrel(self.subDet1) and not is_barrel(self.subDet2)) else 0
        
        if   is_barrel(self.subDet1)==True  and is_barrel(self.subDet2)==True:
            self.region = 'B'
        elif is_barrel(self.subDet1)==True  and is_barrel(self.subDet2)==False:
            self.region = 'I'
        elif is_barrel(self.subDet1)==False and is_barrel(self.subDet2)==False:
            self.region = 'F'
        self.s_ = self.s()
        self.sB = self.s() if self.region=='B' else -1
        self.sI = self.s() if self.region=='I' else -1
        self.sF = self.s() if self.region=='F' else -1
        
    def passes_selections(self, window, debug):
        # 0 = success
        # other value gives first reason for rejecting helix
        success = 0 # true value
        if self.charge < 0:
            if self.phi1 < window.ePhiMin1:
                success = 1
            if self.phi1 > window.ePhiMax1:
                success = 2
        elif self.charge>0:
            if self.phi1 < window.pPhiMin1:
                success = 3
            if self.phi1 > window.pPhiMax1:
                success = 4
        if self.phi2 < window.phiMin2:
            success =  5
        if self.phi2 > window.phiMax2: 
            success =  6
        if self.r2F  < window.r2MinF :
            success =  7
        if self.r2F  > window.r2MaxF :
            success =  8
        if self.r2I   < window.rMinI  :
            success =  9
        if self.r2I   > window.rMaxI  :
            success = 10
        if self.z2B   < window.zMinB  :
            success = 11
        if self.z2B   > window.zMaxB  :
            success = 12
        if debug:
            return success
        return (success==0)
    def s(self):
        s_ = s(self.phi1, self.phi2, self.rz2, self.region)
        return tanh(s_/10)

# Why did I put these here?
s_a_phi1 = {}
s_a_phi2 = {}
s_a_RZ   = {}

# means of electrons from first 1000 events in Zee electrons that pass small window criteria
s_a_phi1['B'] = 0.006872
s_a_phi2['B'] = 0.0003655
s_a_RZ  ['B'] = 0.01221
s_a_phi1['I'] = 0.00875
s_a_phi2['I'] = 0.0007016
s_a_RZ  ['I'] = 0.02731
s_a_phi1['F'] = 0.007629
s_a_phi2['F'] = 0.0009636
s_a_RZ  ['F'] = 0.03975

def s(phi1, phi2, RZ, region):
    return sqrt( pow(phi1/s_a_phi1[region],2) + pow(phi2/s_a_phi1[region],2) + pow(RZ/s_a_RZ[region],2))
