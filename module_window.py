##########################################################################################
# Track and track window                                                                 #
##########################################################################################
class track_window:
    def __init__(self, ePhiMin1_in, ePhiMax1_in, pPhiMin1_in, pPhiMax1_in, phiMin2_in, phiMax2_in, r2MinF_in, r2MaxF_in, rMinI_in, rMaxI_in, zMinB_in, zMaxB_in):
        self.ePhiMin1 = ePhiMin1_in
        self.ePhiMax1 = ePhiMax1_in
        self.pPhiMin1 = pPhiMin1_in
        self.pPhiMax1 = pPhiMax1_in
        self.phiMin2  = phiMin2_in 
        self.phiMax2  = phiMax2_in 
        self.r2MinF   = r2MinF_in  
        self.r2MaxF   = r2MaxF_in  
        self.rMinI    = rMinI_in   
        self.rMaxI    = rMaxI_in   
        self.zMinB    = zMinB_in   
        self.zMaxB    = zMaxB_in   
    def clone(self):
        tw = track_window(self.ePhiMin1, self.ePhiMax1, self.pPhiMin1, self.pPhiMax1, self.phiMin2, self.phiMax2, self.r2MinF, self.r2MaxF,  self.rMinI, self.rMaxI, self.zMinB, self.zMaxB)
        return tw

tag_window         = track_window(-0.04, 0.02, -0.02, 0.04, -0.002, 0.002, -0.075, 0.075, -0.1, 0.1, -0.045, 0.045)
small_window       = track_window(-0.08, 0.04, -0.04, 0.08, -0.004, 0.004, -0.150, 0.150, -0.2, 0.2, -0.090, 0.090)
large_window       = track_window(-0.10, 0.05, -0.05, 0.10, -0.008, 0.008, -0.300, 0.300, -0.2, 0.2, -0.200, 0.200)
extra_large_window = track_window(-0.15, 0.15, -0.15, 0.15, -0.012, 0.012, -0.500, 0.500, -0.5, 0.5, -0.400, 0.400)
largest_window     = track_window(-0.15, 0.15, -0.15, 0.15, -0.120, 0.120, -0.500, 0.500, -0.5, 0.5, -0.400, 0.400)
