##########################################################################################
# Banner                                                                                 #
##########################################################################################

##########################################################################################
# Python modules                                                                         #
##########################################################################################
import numpy
import math

##########################################################################################
# Other modules                                                                          #
##########################################################################################
from module_latex   import latex_var_table, latex_multieff, latex_var_table_by_beforeAfter, latex_var_table_by_charge, latex_var_table_by_trigger
from module_sample  import beam_names, beams, trigger_names, triggers, all_samples
from module_vars    import var_names, variables, region_names, regions
from module_eff_rej import eff_rej_curve, make_large_latex_table
from module_window  import small_window
from module_et      import et_plot_wrapper, et_latex

print_pngs = True
print_epss = True

##########################################################################################
# ROOT and style                                                                         #
##########################################################################################
import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine('.L Loader.C+')

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetFillStyle(ROOT.kWhite)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetFrameBorderMode(ROOT.kWhite)
ROOT.gStyle.SetFrameFillColor(ROOT.kWhite)
ROOT.gStyle.SetCanvasBorderMode(ROOT.kWhite)
ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
ROOT.gStyle.SetPadBorderMode(ROOT.kWhite)
ROOT.gStyle.SetPadColor(ROOT.kWhite)
ROOT.gStyle.SetStatColor(ROOT.kWhite)
ROOT.gStyle.SetErrorX(0)

cw = 600
ch = 600
canvas = ROOT.TCanvas('canvas','',100,100,cw,ch)
canvas.SetGridx()
canvas.SetGridy()
canvas.SetFillColor(ROOT.kWhite)
canvas.SetBorderMode(0)

canvas_log = ROOT.TCanvas('canvas_log','',100,100,cw,ch)
canvas_log.SetGridx()
canvas_log.SetGridy()
canvas_log.SetFillColor(ROOT.kWhite)
canvas_log.SetBorderMode(0)
canvas_log.SetLogy()

##########################################################################################
# Make histograms                                                                        #
##########################################################################################
histograms_eff   = {}
histograms_eff_s = {}
histograms_var   = {}
graphs_eff       = {}

for s in all_samples.samples:
    if 'Zee' not in s.name:
        continue
    print s.name
    s.make_events(small_window)
region_names = ['B','I','F']

h2DBase_s_eta = {}
h2DBase_s_s = {}
for rname in region_names:
    h2DBase_s_eta[rname] = ROOT.TH2D('h2DBase_s%s_eta'%rname, '', 100, -3, 3, 100, -0.1, 0.1)
    h2DBase_s_eta[rname].GetXaxis().SetTitle('#eta_{SC}')
    h2DBase_s_eta[rname].GetYaxis().SetTitle('tanh(s_{%s}/10)'%rname)
    
    h2DBase_s_s[rname] = {}
    for r in region_names:
        h2DBase_s_s[rname][r] = ROOT.TH2D('h2DBase_s%s_s%s'%(rname,r), '', 100, 0.0, 0.05, 100, 0.0, 0.05)
        h2DBase_s_s[rname][r].GetXaxis().SetTitle('tanh(s_{%s}/10)'%rname)
        h2DBase_s_s[rname][r].GetYaxis().SetTitle('tanh(s_{%s}/10)'%r)
        
file_out = ROOT.TFile('s_vs_eta.root','RECREATE')
h2D_s_s        = {}
h2D_s_eta      = {}
h2D_DeltaS_eta = {}
for rname in region_names:
    h2D_s_eta[rname] = h2DBase_s_eta[rname].Clone('h2D_s%s_eta'%rname)
    h2D_DeltaS_eta[rname] = {}
    h2D_s_s[rname]        = {}
    for r in region_names:
        h2D_DeltaS_eta[rname][r] = h2DBase_s_eta[rname].Clone('h2D_DeltaS%s%s_eta'%(rname,r))
        h2D_DeltaS_eta[rname][r].GetYaxis().SetTitle('tanh(s_{%s}/10)-tanh(s_{%s}/10)'%(rname,r))
        h2D_s_s[rname][r] = h2DBase_s_s[rname][r].Clone('h2D_s%s_s%s'%(rname,r))

h_region_bitmap = ROOT.TH1F('h_region_bitmap', '', 8, -0.5, 7.5)
h_region_bitmap.GetXaxis().SetBinLabel(1,'none')
h_region_bitmap.GetXaxis().SetBinLabel(2,'B'   )
h_region_bitmap.GetXaxis().SetBinLabel(3,'I'   )
h_region_bitmap.GetXaxis().SetBinLabel(4,'BI'  )
h_region_bitmap.GetXaxis().SetBinLabel(5,'F'   )
h_region_bitmap.GetXaxis().SetBinLabel(6,'BF'  )
h_region_bitmap.GetXaxis().SetBinLabel(7,'IF'  )
h_region_bitmap.GetXaxis().SetBinLabel(8,'BIF' )

for s in all_samples.samples:
    if 'Zee' not in s.name:
        continue
    print s.name
    for ev in s.events:
        for el in ev.electrons:
            best_s = {}
            for rname in region_names:
                best_s[rname] = 1e6
            for hel in el.helices:
                r = hel.region
                if hel.s_ < best_s[r]:
                    best_s[r] = hel.s_
            for rname in region_names:
                h2D_s_eta[rname].Fill(el.p4.Eta(), math.tanh(best_s[rname]/10))
                for r in region_names:
                    h2D_DeltaS_eta[rname][r].Fill(el.p4.Eta(), math.tanh(best_s[rname]/10)-math.tanh(best_s[r]/10))
            bitmap = 0
            if best_s['B'] < 1e5:
                bitmap += 1
            if best_s['I'] < 1e5:
                bitmap += 2
            if best_s['F'] < 1e5:
                bitmap += 4
            h_region_bitmap.Fill(bitmap)
            
            for rname in region_names:
                for r in region_names:
                    h2D_s_s[rname][r].Fill(math.tanh(best_s[rname]/10),math.tanh(best_s[r]/10))
file_out.Write()

