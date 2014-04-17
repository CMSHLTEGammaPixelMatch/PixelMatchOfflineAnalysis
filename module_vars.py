import ROOT

##########################################################################################
# Regions                                                                                #
##########################################################################################
class region_object:
    def __init__(self, letter, name, ROOT_label, rz_name, color, marker):
        self.letter     = letter
        self.name       = name
        self.rz_name    = rz_name
        self.ROOT_label = ROOT_label
        self.color      = color
        self.marker     = marker
        
        self.TLatex1 = ROOT.TLatex(0.6, 0.82, name)
        self.TLatex1.SetTextSize(0.05)
        self.TLatex1.SetNDC()
        self.TLatex2 = ROOT.TLatex(0.6, 0.77, 'electrons')
        self.TLatex2.SetTextSize(0.05)
        self.TLatex2.SetNDC()
        
        self.TLatex1_eff_rej = ROOT.TLatex(0.6, 0.27, name)
        self.TLatex1_eff_rej.SetTextSize(0.05)
        self.TLatex1_eff_rej.SetNDC()
        self.TLatex2_eff_rej = ROOT.TLatex(0.6, 0.22, 'electrons')
        self.TLatex2_eff_rej.SetTextSize(0.05)
        self.TLatex2_eff_rej.SetNDC()
        
    def draw_label(self):
        self.TLatex1.Draw()
        self.TLatex2.Draw()
    def draw_label_eff_rej(self):
        self.TLatex1_eff_rej.Draw()
        self.TLatex2_eff_rej.Draw()
    
    def set_style(self, g):
        g.SetLineColor(self.color)
        g.SetMarkerColor(self.color)
        g.SetMarkerStyle(self.marker)

regions = {}
regions['B'] = region_object('B', 'Barrel'      , 'Barrel electrons'      , 'zB', ROOT.kRed  , 24)
regions['I'] = region_object('I', 'Intermediate', 'Intermediate electrons', 'rI', ROOT.kBlue , 25)
regions['F'] = region_object('F', 'Forward'     , 'Forward electrons'     , 'rF', ROOT.kBlack, 26)
regions['A'] = region_object('A', 'All'         , 'All electrons'         , ''  , ROOT.kGreen, 27)
region_names = ['B','I','F']

def get_region(subdet1, subdet2):
    if   subdet1==1 and subdet2==1:
        return 'B'
    elif subdet1==1 and subdet2!=1:
        return 'I'
    elif subdet1!=1 and subdet2!=1:
        return 'F'
    return 'X'

##########################################################################################
# Variables                                                                              #
##########################################################################################
class variable_object:
    def __init__(self, name, ROOT_title, latex, nBins, lower, upper, nBins_eff, region, type):
        self.name       = name
        self.type       = type
        self.latex      = latex
        self.nBins      = nBins
        self.nBins_eff  = nBins_eff
        self.lower      = lower
        self.upper      = upper
        self.region     = region
        self.ROOT_title = ROOT_title
        
        self.hBase = ROOT.TH1F('hBase_%s'%self.name, '', self.nBins, self.lower, self.upper)
        self.hBase.GetXaxis().SetTitle(self.ROOT_title)
        self.hBase.GetYaxis().SetTitle('superclusters [normalised]')
        
        self.binWidth_eff = self.upper/(self.nBins_eff)
        self.lower_eff =       0.5*self.binWidth_eff
        self.upper_eff = upper+0.5*self.binWidth_eff
        
        self.hBase_eff = {}
        h = ROOT.TH1F('hBase_eff_%s'%self.name, '', self.nBins_eff, self.lower_eff, self.upper_eff)
        h.GetXaxis().SetTitle(self.ROOT_title)
        h.GetYaxis().SetTitle('relative efficiency')
        self.hBase_eff = h
        
        self.name_eff = name
        if   self.name == 'z2B':
            self.name_eff = 'zB'
        elif self.name == 'r2I':
            self.name_eff = 'rI'
        
        
    def get_helix_value(self, helix):
        if hasattr(helix, self.name):
            return getattr(helix, self.name)
        return -999

##########################################################################################
# Variable delcarations                                                                  #
##########################################################################################
variables = {}
variables['phi1'] = variable_object('phi1', '#Delta#phi_{1}' , '\\Delta\\phi_1' , 100,  -0.08,  0.08, 100, 'A', 'phi')
variables['phi2'] = variable_object('phi2', '#Delta#phi_{2}' , '\\Delta\\phi_2' , 100, -0.004, 0.004, 100, 'A', 'phi')
variables['z1B' ] = variable_object('z1B'  , '#Deltaz_{B,1}' , '\\Delta z_{B,1}', 100,  -4.00,  4.00, 100, 'B', 'rz' )
variables['r1I' ] = variable_object('r1I'  , '#Deltar_{I,1}' , '\\Delta r_{I,1}', 100,  -6.00,  6.00, 100, 'I', 'rz' )
variables['r1F' ] = variable_object('r1F'  , '#Deltar_{F,1}' , '\\Delta r_{F,1}', 100,  -4.00,  4.00, 100, 'F', 'rz' )
variables['z2B' ] = variable_object('z2B'  , '#Deltaz_{B,2}' , '\\Delta z_{B,2}', 100,  -0.09,  0.09, 100, 'B', 'rz' )
variables['r2I' ] = variable_object('r2I'  , '#Deltar_{I,2}' , '\\Delta r_{I,2}', 100,  -0.20,  0.20, 100, 'I', 'rz' )
variables['r2F' ] = variable_object('r2F'  , '#Deltar_{F,2}' , '\\Delta r_{F,2}', 100,  -0.15,  0.15, 100, 'F', 'rz' )
variables['sB'  ] = variable_object('sB'   , 'tanh(s_{B}/10)', '\\tanh{s_B/10}' , 100,       0,    1, 100, 'B', 's'  )
variables['sI'  ] = variable_object('sI'   , 'tanh(s_{I}/10)', '\\tanh{s_I/10}' , 100,       0,    1, 100, 'I', 's'  )
variables['sF'  ] = variable_object('sF'   , 'tanh(s_{F}/10)', '\\tanh{s_F/10}' , 100,       0,    1, 100, 'F', 's'  )

var_names = ['phi1' , 'phi2' , 'z2B' , 'r2I' , 'r2F' , 'sB' , 'sI' , 'sF']
var_names_phi_rz = ['phi1' , 'phi2' , 'zB' , 'rI' , 'rF' ]


