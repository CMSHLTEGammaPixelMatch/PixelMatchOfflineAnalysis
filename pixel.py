##########################################################################################
# Banner                                                                                 #
##########################################################################################

##########################################################################################
# Python modules                                                                         #
##########################################################################################
import numpy

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

scut = {} 
scut[trigger_names[0]] = {'B':0.34,'I':0.38,'F':0.29}
scut[trigger_names[1]] = {'B':0.32,'I':0.39,'F':0.32}

for s in all_samples.samples:
    print s.name
    s.make_events(small_window)

for s in all_samples.samples:
    print s.name
    for rname in region_names:
        for vname in var_names:
            var = variables[vname]
            h_var = s.add_var_histogram(var, rname)
            if h_var:
                for h in h_var:
                    histograms_var[h.GetName()] = h
        s.fill_var_histograms(rname, scut)
        for vname in var_names:
            var = variables[vname]
            h_eff = s.make_eff_histogram(var, rname)
            if h_eff:
                for h in h_eff:
                    histograms_eff[h.GetName()] = h
    s.make_2D_eff_histograms()
    
    s.make_nPixelMatch_histogram(canvas)

##########################################################################################
# Get means of signal parameters for s variables                                         #
##########################################################################################
sum_phi1 = {}
sum_phi2 = {}
sum_rz2  = {}
n        = {}
for rname in region_names:
    sum_phi1[rname] = 0
    sum_phi2[rname] = 0
    sum_rz2 [rname] = 0
    n       [rname] = 0
    for sample in all_samples.samples:
        sum_phi1[rname] += sum(sample.phi1[rname])
        sum_phi2[rname] += sum(sample.phi2[rname])
        sum_rz2 [rname] += sum(sample.rz2 [rname])
        n[rname] += sample.n_el[rname]
    print '== %s == '%rname
    print 'm(phi1) = %8.4g'%(sum_phi1[rname]/n[rname])
    print 'm(phi2) = %8.4g'%(sum_phi2[rname]/n[rname])
    print 'm(rz2 ) = %8.4g'%(sum_rz2 [rname]/n[rname])
    print 'n = %d'%n[rname]

##########################################################################################
# Print histograms                                                                       #
##########################################################################################
print_suffixes = []
if print_pngs:
    print_suffixes.append('png')
if print_epss:
    print_suffixes.append('eps')

for suffix in print_suffixes:
    for hName in histograms_var:
        canvas.Clear()
        print_name = '../plots/vars/%s.%s'%(hName,suffix)
        histograms_var[hName].Draw('pe')
        canvas.Print(print_name)
    
    for s in all_samples.samples:
        for hName_2D in s.histograms_2D:
            canvas.Clear()
            print_name = '../plots/vars/%s.%s'%(hName_2D,suffix)
            s.histograms_2D[hName_2D][0].Draw('colz')
            canvas.Print(print_name)
        for hName_2Deff in s.histograms_2Deff:
            canvas.Clear()
            print_name = '../plots/vars/%s.%s'%(hName_2Deff,suffix)
            s.histograms_2Deff[hName_2Deff][0].Draw('colz')
            canvas.Print(print_name)

    for hName in histograms_eff:
        canvas.Clear()
        print_name = '../plots/effs/%s.%s'%(hName,suffix)
        histograms_eff[hName].Draw('pe')
        canvas.Print(print_name)

##########################################################################################
# Make ROC curves                                                                        #
##########################################################################################
objects_to_save = []

eff_rej_curves = {}
pname_sig = 'Zee'
pname_bkg = 'QCD_Pt_30_80'
eff_target_values_sig = [ 0.5 , 0.9 , 0.95 , 0.99 , 0.995 ]
eff_target_values_bkg = [ 0.1 ,  0.3 ,  0.5 , 0.7 , 0.9 ]
for bname in beams:
    for tname in triggers:
        for rname in region_names:
            if rname=='A':
                continue
            for vname in var_names:
                ename = '%s_%s_%s_%s'%(vname, bname, tname, rname)
                vregion = variables[vname].region
                if vregion!='A' and vregion!=rname:
                    continue
                erc = eff_rej_curve(bname, tname, rname, vname, pname_sig, pname_bkg, eff_target_values_sig, eff_target_values_bkg, histograms_eff)
                erc.plot(objects_to_save)
                eff_rej_curves[ename] = erc
                graphs_eff['g_%s'%ename] = eff_rej_curves[ename].graph

##########################################################################################
# Print canvases                                                                         #
##########################################################################################

var_groups = [ 
  [ {'B':'phi1','I':'phi1','F':'phi1'}, '\\phi_1', 'phi1', 3 , '\\Delta\\phi_1'] ,
  [ {'B':'phi2','I':'phi2','F':'phi2'}, '\\phi_2', 'phi2', 3 , '\\Delta\\phi_2'] ,
  [ {'B':'z2B' ,'I':'r2I' ,'F':'r2F' }, 'rz_2'   , 'rz'  , 3 , '\\Delta r/z'   ] ,
  [ {'B':'sB'  ,'I':'sI'  ,'F':'sF'  }, 's'      , 's'   , 0 , 's'             ] ,
]

# Main variable plots
for cname in ['ep','em','ea']:
    snippets = []
    for v in var_groups:
        snippets.append(latex_var_table(v[4], v[0], v[2], cname, 'var', histograms_var, objects_to_save))
    file = open('../note/snippets/vars_plots_%s.tex'%cname,'w')
    file.write('\n\n'.join(snippets))

for cname in ['ep','em','ea']:
    snippets = []
    for v in var_groups:
        snippets.append(latex_var_table_by_beforeAfter(v[4], v[0], v[2], cname, 'var', histograms_var, objects_to_save))
    file = open('../note/snippets/vars_plots_%s_beforeAfter.tex'%cname,'w')
    file.write('\n\n'.join(snippets))

# Main variable plots by charge
snippets = []    
for v in var_groups:
    snippets.append(latex_var_table_by_charge(v[4], v[0], v[2], beam_names[0], 'var', histograms_var, objects_to_save))
file = open('../note/snippets/vars_plots_byCharge.tex','w')
file.write('\n\n'.join(snippets))

# Main variable plots by trigger
snippets = []    
for v in var_groups:
    snippets.append(latex_var_table_by_trigger(v[4], v[0], v[2], beam_names[0], 'var', histograms_var, objects_to_save))
file = open('../note/snippets/vars_plots_byTrigger.tex','w')
file.write('\n\n'.join(snippets))

# Main variable efficiency plots
for cname in ['ep','em','ea']:
    for v in var_groups:
        snippets = []
        snippets.append(latex_var_table(v[4], v[0], v[2], cname, 'eff', histograms_eff, objects_to_save))
        file = open('../note/snippets/effs_plots_%s_%s.tex'%(cname, v[2]),'w')
        file.write('\n\n'.join(snippets))

# Main efficiency vs rejection plots
for cname in ['ep','em','ea']:
    for v in var_groups:
        snippets = []
        snippets.append(latex_multieff(v[4], v[0], v[2], cname, graphs_eff, objects_to_save))
        file = open('../note/snippets/eff_rej_plots_%s_%s.tex'%(cname,v[2]),'w')
        file.write('\n\n'.join(snippets))

##########################################################################################
# Efficiency tables                                                                      #
##########################################################################################
snippets = []
for type in ['sig','bkg']:
    for bname in beams:
        for tname in triggers:
            for rname in region_names:
                if rname=='A':
                    continue
                for vname in var_names:
                    ename = '%s_%s_%s_%s'%(vname, bname, tname, rname)
                    if ename in eff_rej_curves:
                        snippets.append(eff_rej_curves[ename].latex_table_rows(type))
                        snippets.append('\\clearpage')
    file = open('../note/snippets/eff_rej_tables_%s.tex'%type,'w')
    file.write('\n\n'.join(snippets))

for v in var_groups:
    snippets = []
    for type in ['sig','bkg']:
        for bname in beam_names:
            snippets.append(make_large_latex_table(bname, type, eff_rej_curves, v[0], v[1], v[2], v[3]))
    file = open('../note/snippets/eff_rej_tables_%s.tex'%v[2],'w')
    file.write('\n\n'.join(snippets))

##########################################################################################
# ET spectra                                                                             #
##########################################################################################
et_plots = {}
scut = {'B':0.06,'I':0.07,'F':0.06}
for s in all_samples.samples:
    #if 'Zee' not in s.name:
    #    continue
    for rname in region_names:
        epw = et_plot_wrapper(s, rname)
        epw.fill(scut[rname], objects_to_save)
        epw.print_canvas(objects_to_save)
        et_plots['%s_%s'%(s.name,rname)] = epw

snippets = []    
for rname in regions:
    if rname=='A':
        continue
    snippets.append(et_latex(et_plots, rname))
    snippets.append('\\clearpage')
file = open('../note/snippets/et_plots.tex','w')
file.write('\n\n'.join(snippets))

#for s in all_samples.samples:
#    s.hNPixelMatch.Draw()
#    canvas.Print('../plots/vars/h_nPixelMatch%s.eps'%s.name)

##########################################################################################
# Write everything to file                                                               #
##########################################################################################
ROOT_file = ROOT.TFile('objects.root','RECREATE')
ROOT_file.cd()
print len(objects_to_save)
for object in objects_to_save:
    if object:
        object.Write()
        print 'Saving object to file: %s'%object.GetName()
ROOT_file.Write()
ROOT_file.Close()


