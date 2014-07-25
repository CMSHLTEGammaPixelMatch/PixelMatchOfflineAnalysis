import string
import math
import ROOT
import module_vars, module_event
from module_vars   import region_names
from module_window import small_window

mZ_window_lower =  60
mZ_window_upper = 120
tag_and_probe = False

##########################################################################################
# Processes                                                                              #
##########################################################################################
class process_object:
    def __init__(self, name, color, marker, ROOT_title):
        self.name       = name
        self.color      = color
        self.marker     = marker
        self.ROOT_title = ROOT_title
        
        self.hBase = ROOT.TH1F('hBase_%s'%self.name,'',2,0,1)
        self.set_style(self.hBase)
    def set_style(self, h):
        h.SetLineColor(self.color)
        h.SetMarkerColor(self.color)
        h.SetMarkerStyle(self.marker)

processes = {}
processes['Zee'           ] = process_object('Zee'           , ROOT.kBlue , 22, 'Z#rightarrow ee' )
processes['QCD_Pt_30_80'  ] = process_object('QCD_Pt_30_80'  , ROOT.kRed  , 21, 'QCD p_{T}[30,80]')
processes['ttbar'         ] = process_object('ttbar'         , ROOT.kGreen, 23, 't#bar{t}'        )
processes['DoubleElectron'] = process_object('DoubleElectron', ROOT.kBlack, 20, 'DoubleElectron'  )
process_names = ['Zee','QCD_Pt_30_80','ttbar','DoubleElectron']

##########################################################################################
# Beams                                                                                  #
##########################################################################################
class beam_object:
    def __init__(self, name, year, energy, bunch_spacing):
        self.name          = name
        self.year          = year
        self.energy        = energy
        self.bunch_spacing = bunch_spacing
        self.filename      = '%sTeV_%sns'%(self.energy, self.bunch_spacing)
        self.ROOT_title    = '%d TeV %d ns'%(self.energy, self.bunch_spacing)
        
        self.TLatex = ROOT.TLatex(0.6,0.675,self.ROOT_title)
        self.TLatex.SetTextSize(0.05)
        self.TLatex.SetNDC()
        
        self.TLatex_eff_rej = ROOT.TLatex(0.6,0.125,self.ROOT_title)
        self.TLatex_eff_rej.SetTextSize(0.05)
        self.TLatex_eff_rej.SetNDC()
beams = {}
beams['beam_8_50' ] = beam_object('beam_8_50' , 2012,  8, 50)
beams['beam_13_25'] = beam_object('beam_13_25', 2015, 13, 25)
beam_names = ['beam_8_50','beam_13_25']

##########################################################################################
# Triggers                                                                               #
##########################################################################################
class trigger_object:
    def __init__(self, name, ROOT_title, short_latex, long_latex):
        self.name = name
        self.ROOT_title  = ROOT_title
        self.long_latex  = long_latex
        self.short_latex = short_latex
        
        self.short_latex = string.replace(short_latex, '_', '\_')
        self.long_latex  = string.replace(long_latex , '_', '\_')
        
        self.TLatex = ROOT.TLatex(0.05,0.95,self.ROOT_title)
        self.TLatex.SetTextSize(0.04)
        self.TLatex.SetNDC()

triggers = {}
triggers['trigger_27'  ] = trigger_object('trigger_27'  , 'HLT_Ele27_WP80_v13', 'HLT_Ele27_WP80_v13', 'HLT_Ele27_WP80_v13')
triggers['trigger_17_8'] = trigger_object('trigger_17_8', 'HLT_Ele17_Ele8_v19', 'HLT_Ele17_Ele8_v19', 'HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_v20')
trigger_names = ['trigger_27','trigger_17_8']


##########################################################################################
# Samples                                                                                #
##########################################################################################
class sample_object:
    def __init__(self, process_name, beam_name, trigger_name, crab_id, n_jobs):
        self.process = processes[process_name]
        self.beam    = beams[beam_name]
        self.trigger = triggers[trigger_name]
        self.name    = '%s_%s_%s'%(self.process.name, self.beam.name, self.trigger.name)
        self.crab_id = crab_id
        self.n_jobs  = n_jobs
        
        self.var_filename = '../output/CRAB/outfile_%s_%s_%s.root'%(self.process.name, self.beam.filename, self.trigger.name)
        self.var_rootfile = ROOT.TFile(self.var_filename)
        self.var_ttree = self.var_rootfile.Get('electrons')
            
        self.events = []
        
        self.n_s = {}
        self.s   = {}
        for r in module_vars.regions:
            self.n_s[r] = []
            self.s[r]   = []
        
        self.hBase = ROOT.TH1F('', '', 2, 0, 1)
        self.set_style(self.hBase)
        
        self.phi1 = {}
        self.phi2 = {}
        self.rz2  = {}
        self.n_el = {}
        for rname in region_names:
            self.phi1[rname] = []
            self.phi2[rname] = []
            self.rz2[rname]  = []
            self.n_el[rname] = 0
        self.histograms    = {}
        self.histograms_2D = {}
        self.histograms_2Deff = {}
        
    def set_style(self, h):
        self.process.set_style(h)
        h.GetXaxis().SetLabelSize(0.025)
        h.GetYaxis().SetLabelSize(0.025)
        h.GetYaxis().SetTitleOffset(1.3)
        h.GetXaxis().SetTitleOffset(1.3)
        
    def ROOT_title(self):
        return '%s %s'%(self.process.ROOT_title, self.beam.ROOT_title)
    
    def make_events(self, tag_window):
        tree = self.var_ttree
        nEvents = min(1000000000000,tree.GetEntries())
        #nEvents = min(1000,tree.GetEntries())
        
        self.n_el_0 = 0
        self.n_el_1 = 0
        self.n_el_2 = 0
        self.n_el_3 = 0
        self.n_el_4 = 0
        
        events = []
        
        for i_entry in range(0,nEvents):
            tree.GetEntry(i_entry)
            ev = module_event.event()
            ev.smallest_phi1 = {}
            ev.smallest_phi2 = {}
            ev.smallest_rz   = {}
            ev.smallest_s    = {}
            for rname in region_names:
                ev.smallest_phi1[rname] = 1e6
                ev.smallest_phi2[rname] = 1e6
                ev.smallest_rz  [rname] = 1e6
                ev.smallest_s   [rname] = 1e6
            
            if tree.el_pt.size()==0:
                self.n_el_0 += 1
            if tree.el_pt.size()==1:
                self.n_el_1 += 1
            if tree.el_pt.size()==2:
                self.n_el_2 += 1
            if tree.el_pt.size()==3:
                self.n_el_3 += 1
            if tree.el_pt.size()>=4:
                self.n_el_4 += 1
                
            if i_entry%10000==0:
                print '%8d / %8d'%(i_entry, nEvents)
                
            for i_el in range(0,tree.el_pt.size()):
                elp4 = ROOT.TLorentzVector()
                elp4.SetPtEtaPhiE(tree.el_pt.at(i_el), tree.el_eta.at(i_el), tree.el_phi.at(i_el), tree.el_E.at(i_el))
                el = module_event.electron_object(elp4)
                helix_neg = 0
                helix_pos = 0
                vec = tree.el_subDet1.at(i_el)
                n = len(vec)
                
                best_phi1 = 1e6
                best_phi2 = 1e6
                best_rz2  = 1e6
                
                for i_helix in range(0, n):
                    charge  = tree.el_matchCharge.at(i_el).at(i_helix)
                    subDet1 = tree.el_subDet1.at(i_el).at(i_helix)
                    subDet2 = tree.el_subDet2.at(i_el).at(i_helix)
                    if charge > 0:
                        dPhi1   = tree.el_dPhi1_pos.at(i_el).at(i_helix)
                        dPhi2   = tree.el_dPhi2_pos.at(i_el).at(i_helix)
                        dRz1    = tree.el_dRz1_pos .at(i_el).at(i_helix)
                        dRz2    = tree.el_dRz2_pos .at(i_el).at(i_helix)
                        s2      = tree.el_s2_pos  .at(i_el).at(i_helix)
                        helix_neg = helix_neg+1
                    else:
                        dPhi1   = tree.el_dPhi1_neg.at(i_el).at(i_helix)
                        dPhi2   = tree.el_dPhi2_neg.at(i_el).at(i_helix)
                        dRz1    = tree.el_dRz1_neg .at(i_el).at(i_helix)
                        dRz2    = tree.el_dRz2_neg .at(i_el).at(i_helix)
                        s2      = tree.el_s2_neg   .at(i_el).at(i_helix)
                        helix_neg = helix_neg+1
                        
                    helix = module_event.electron_helix(dPhi1, dPhi2, dRz1, dRz2, s2, charge, subDet1, subDet2)
                    
                    accept = helix.passes_selections(small_window, False)
                    if accept==False:
                        continue
                    self.phi1[helix.region].append(abs(helix.phi1))
                    self.phi2[helix.region].append(abs(helix.phi2))
                    self.rz2[helix.region] .append(abs(helix.rz2 ))
                    
                    ev.smallest_phi1[helix.region] = min(helix.phi1, ev.smallest_phi1[helix.region])
                    ev.smallest_phi2[helix.region] = min(helix.phi2, ev.smallest_phi2[helix.region])
                    ev.smallest_rz  [helix.region] = min(helix.rz2 , ev.smallest_rz  [helix.region])
                    ev.smallest_s   [helix.region] = min(helix.s_  , ev.smallest_s   [helix.region])
                    
                    el.add_helix(helix)
                el.calculate_charge()
                el.index = i_el
                ev.electrons.append(el)
                if el.passes_selections(tag_window,''):
                    ev.tag_electrons.append(el)
            
            for e1 in ev.electrons:
                for e2 in ev.tag_electrons:
                    if e1.index==e2.index:
                        continue
                    Zp4 = e1.p4 + e2.p4
                    e1.is_tagged = ( mZ_window_lower<Zp4.M() and Zp4.M()<mZ_window_upper )
                if e1.is_tagged==True or tag_and_probe==False:
                    ev.probe_electrons.append(e1)
            events.append(ev)
        print "Events with 0 electrons: %d"%self.n_el_0
        print "Events with 1 electron : %d"%self.n_el_1
        print "Events with 2 electrons: %d"%self.n_el_2
        print "Events with 3 electrons: %d"%self.n_el_3
        print "Events with 4 electrons: %d"%self.n_el_4
        
        for rname in region_names:
            self.n_el[rname] = len(self.phi1[rname])
        
        self.events = events
    
    def add_var_histogram(self, var, region):
        histos = []
        if var.region!='A' and var.region!=region:
            return False
        for cname in ['ep','em','ea']:
            for beforeAfter_name in ['','_after']:
                hName = 'h_var_%s_%s_%s_%s%s'%(var.name, self.name, region, cname, beforeAfter_name)
                h = var.hBase.Clone(hName)
                h.Sumw2()
                self.set_style(h)
                if var.region=='A' or var.region==region:
                    self.histograms[hName] = [h, var]
                histos.append(h)
                
                hName_2D = 'h2D_var_%s_%s_%s_%s%s'%(var.name, self.name, region, cname, beforeAfter_name)
                nBinsX = h.GetNbinsX()
                lowerX = h.GetXaxis().GetXmin()
                upperX = h.GetXaxis().GetXmax()
                if var.name=='phi1':
                    lowerX = -0.04
                    upperX =  0.04
                if var.name=='phi2':
                    lowerX = -0.002
                    upperX =  0.002
                if var.name=='z2B':
                    lowerX = -0.06
                    upperX =  0.06
                if var.name=='r2I':
                    lowerX = -0.05
                    upperX =  0.05
                if var.name=='r2F':
                    lowerX = -0.05
                    upperX =  0.05
                nBinsY =  20
                lowerY =   0
                upperY = 120
                h2D = ROOT.TH2F(hName_2D, '', nBinsX, lowerX, upperX, nBinsY, lowerY, upperY)
                h2D.GetXaxis().SetTitle(h.GetXaxis().GetTitle())
                h2D.GetYaxis().SetTitle('E_{T}(e) [GeV]')
                h2D.Sumw2()
                self.set_style(h2D)
                if var.region=='A' or var.region==region:
                    self.histograms_2D[hName_2D] = [h2D, var]
                
        return histos
    
    def fill_var_histograms(self, region, scut):
        counter = 0
        for ev in self.events:
            counter = counter + 1
            if counter%10000==0:
                print counter
            for el in ev.electrons:
                best_helix = 0
                best_s = 1e6
                for helix in el.helices:
                    if helix.region!=region:
                        continue
                    if helix.s_ < best_s:
                        best_s = helix.s_
                        best_helix = helix
                if best_helix!=0:
                    for hName in self.histograms:
                        if best_helix.region not in hName:
                            continue
                        q = best_helix.charge
                        if q>0 and '_ep' not in hName and '_ea' not in hName:
                            continue
                        if q<0 and '_em' not in hName and '_ea' not in hName:
                            continue
                        if 'after' in hName and helix.s_ > scut[self.trigger.name][region]:
                                continue
                        h_wrapper = self.histograms[hName]
                        h_wrapper[0].Fill(h_wrapper[1].get_helix_value(best_helix))
                        
                    for hName_2D in self.histograms_2D:
                        if best_helix.region not in hName_2D:
                            continue
                        q = best_helix.charge
                        if q>0 and '_ep' not in hName_2D and '_ea' not in hName_2D:
                            continue
                        if q<0 and '_em' not in hName_2D and '_ea' not in hName_2D:
                            continue
                        if 'after' in hName and helix.s_ > scut[self.trigger.name][region]:
                                continue
                        h2D_wrapper = self.histograms_2D[hName_2D]
                        h2D_wrapper[0].Fill(h2D_wrapper[1].get_helix_value(best_helix), el.p4.Pt())
    
    def make_2D_eff_histograms(self):
        for hName_2D in self.histograms_2D:
            h = self.histograms_2D[hName_2D][0]
            hName_2Deff = 'heff_%s'%hName_2D[1:]
            h_eff = h.Clone(hName_2Deff)
            for biny in range(1,h_eff.GetNbinsY()+1):
                for binx in range(1,h_eff.GetNbinsX()+1):
                    h_eff.SetBinContent(binx, biny, 0)
            
            debug_ = False
            if 'DoubleElectron' in hName_2D and '_ea' in hName_2D and 'phi1' in hName_2D and 'beam_8_50' in hName_2D and 'trigger_17_8' in hName_2D:
                debug_ = True
            debug_ = False
                
            grand_total = 0
            for biny in range(1,h.GetNbinsY()+1):
                for binx in range(1,h.GetNbinsX()+1):
                    grand_total = grand_total + h.GetBinContent(binx, biny)
                
            for biny in range(1,h.GetNbinsY()+1):
                # Get the total for that row in the histogram
                total = 0
                for binx in range(1,h.GetNbinsX()+1):
                    total = total + h.GetBinContent(binx, biny)
                
                for binx in range(1,1+h.GetNbinsX()/2):
                    n = 0
                    for bintmp in range(binx,h.GetNbinsX()+2-binx):
                        n = n + h.GetBinContent(bintmp, biny)
                    eff = 0
                    if total>0:
                        eff = n/total
                    h_eff.SetBinContent(binx,biny,eff)
                    if debug_:
                        print '%4d %4d %8f %5d'%(binx , biny , eff , total)
            
            for binx in range(1+h.GetNbinsX()/2,h.GetNbinsX()+1):
                total = 0
                for biny in range(1,h.GetNbinsY()+1):
                    for bintmp in range(h.GetNbinsX()+1-binx,binx+1):
                        total = total + h.GetBinContent(bintmp, biny)
                eff = total/grand_total
                for biny in range(1,h.GetNbinsY()+1):
                    h_eff.SetBinContent(binx,biny,eff)
                    if debug_:
                        print '%4d %4d %8f'%(binx , biny , eff)
                
            self.histograms_2Deff[hName_2Deff] = [h_eff,self.histograms_2D[hName_2D][1]]
        
    
    def make_eff_histogram(self, var, region):
        histos = []
        for cname in ['ep','em','ea']:
            hName = 'h_eff_%s_%s_%s_%s'%(var.name, self.name, region, cname)
            h = var.hBase_eff.Clone(hName)
            if var.region!='A' and var.region!=region:
                return histos
            h.Sumw2()
            self.set_style(h)
            for bin in range(1, h.GetNbinsX()+1):
                x_max = h.GetBinCenter(bin)
                n_pass = 0
                for ev in self.events:
                    accept = False
                    for el in ev.electrons:
                        for helix in el.helices:
                            if helix.region!=region:
                                continue
                            if helix.charge>0 and cname=='em':
                                continue
                            if helix.charge<0 and cname=='ep':
                                continue
                            if abs(var.get_helix_value(helix)) < x_max:
                                accept = True
                                break
                        if accept:
                            break
                    if accept:
                        n_pass += 1
                h.SetBinContent(bin, n_pass)
                h.SetBinError(bin, math.sqrt(n_pass))
            denom = h.GetMaximum()
            if denom < 1e-3:
                denom = 1
            for bin in range(1, h.GetNbinsX()+1):
                eff = h.GetBinContent(bin)/denom
                err = math.sqrt(eff*(1-eff)/denom)
                h.SetBinContent(bin,eff)
                h.SetBinError  (bin,err)
            histos.append(h)
        return histos
        
class sample_container:
    def __init__(self, samples_in):
        self.samples = samples_in
    def pick_samples(self, substr):
        results = []
        for s in self.samples:
            accept = False
            if substr in s.name:
                accept = True
            elif substr in s.process.name:
                accept = True
            elif substr in s.beam.name:
                accept = True
            if accept:
                results.append(s)
        return results

##########################################################################################
# Add information about the samples and CRAB jobs here                                   #
##########################################################################################
all_samples = sample_container([])
all_samples.samples.append( sample_object('Zee'           , 'beam_8_50' , 'trigger_27'  , '140310_145620',  19) )
all_samples.samples.append( sample_object('QCD_Pt_30_80'  , 'beam_8_50' , 'trigger_27'  , '140314_144623', 179) )
all_samples.samples.append( sample_object('DoubleElectron', 'beam_8_50' , 'trigger_27'  , '140314_144159',  59) )

all_samples.samples.append( sample_object('Zee'           , 'beam_8_50' , 'trigger_17_8', '140317_121806',  19) )
all_samples.samples.append( sample_object('QCD_Pt_30_80'  , 'beam_8_50' , 'trigger_17_8', '140317_133818', 117) )
all_samples.samples.append( sample_object('DoubleElectron', 'beam_8_50' , 'trigger_17_8', '140317_134644',  59) )

all_samples.samples.append( sample_object('Zee'           , 'beam_13_25', 'trigger_27'  , '140314_145414',  47) )
all_samples.samples.append( sample_object('QCD_Pt_30_80'  , 'beam_13_25', 'trigger_27'  , '140314_145047', 117) )
all_samples.samples.append( sample_object('ttbar'         , 'beam_13_25', 'trigger_27'  , '140314_145509', 490) )

all_samples.samples.append( sample_object('Zee'           , 'beam_13_25', 'trigger_17_8', '140318_175913',  47) )
all_samples.samples.append( sample_object('QCD_Pt_30_80'  , 'beam_13_25', 'trigger_17_8', '140317_134519', 147) )
all_samples.samples.append( sample_object('ttbar'         , 'beam_13_25', 'trigger_17_8', '140317_172322', 490) )

