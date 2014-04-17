import ROOT
from math import sqrt
from module_legend import make_legend, fill_legend
from module_sample import beam_names, beams, trigger_names, triggers, all_samples, trigger_names, triggers
from module_vars   import region_names, regions

##########################################################################################
# CMS labels                                                                             #
##########################################################################################

CMS_label_texts = {}
CMS_label_texts['normal'        ] = 'CMS'
CMS_label_texts['internal'      ] = 'CMS internal'
CMS_label_texts['workInProgress'] = 'CMS work in progress'
CMS_labels = {}
for t in CMS_label_texts:
    CMS_labels[t] = ROOT.TLatex(0.65, 0.945, CMS_label_texts[t])
    CMS_labels[t].SetNDC()
CMS_label = CMS_labels['internal']

cw = 600
ch = 600

def make_canvas(cname):
    canvas = ROOT.TCanvas('canavs_%s'%cname, '', 100, 100, cw, ch)
    canvas.SetGridx()
    canvas.SetGridy()
    return canvas

##########################################################################################
# Plot things                                                                            #
##########################################################################################
def plot_multiple_histograms(histos, legend, bname, tname, rname, vname, cname, type, objects_to_save):
    height_scale = 2.0 if type=='var' else 1.6
    best_h = -1
    max_height =  0
    for h in histos:
        if h.GetSumOfWeights()<1e-6:
            continue
        if type=='var':
            h.Scale(1.0/h.GetSumOfWeights())
        h.SetMinimum(0)
        height = h.GetMaximum() + 2*sqrt(h.GetMaximum())
        if height > max_height:
            max_height = height
            best_h = h
    if best_h==-1:
        return
    best_h.SetMaximum(height_scale*best_h.GetMaximum())
    
    canvas_name = 'h_multi%s_%s_%s_%s_%s_%s'%(type, vname, bname, tname, rname, cname)
    canvas_tmp = make_canvas(canvas_name)
    file_name = '../plots/%ss/%s'%(type, canvas_name)
    print_name = '%s.eps'%file_name
    best_h.Draw('pe')
    for h in histos:
        h.Draw('pe:sames')
    best_h.Draw('axis:sames')
    legend.Draw()
    triggers[tname].TLatex.Draw()
    regions[rname] .draw_label()
    beams[bname]   .TLatex.Draw()
    CMS_label.Draw()
    
    canvas_tmp.Print(print_name)
    objects_to_save.append(canvas_tmp)
    return file_name

def plot_multiple_graphs(graphs, legend, objects_to_save, bname, tname, cname, label):
    mg = ROOT.TMultiGraph('mg_%s_%s_s'%(bname, tname), '')
    for g in graphs:
        mg.Add(g)
    
    cname = 'g_multieff_%s_%s_%s_%s'%(label, bname, tname, cname)
    canvas_tmp = make_canvas(cname)
    mg.Draw('ALP')
    mg.GetXaxis().SetTitle('QCD P_{T}[30,80] relative efficiency')
    mg.GetYaxis().SetTitle('Z#rightarrowee relative efficiency')
    mg.GetXaxis().SetTitleOffset(1.25)
    mg.GetYaxis().SetTitleOffset(1.25)
    mg.Draw('ALP')
    legend.Draw()
    triggers[tname].TLatex.Draw()
    beams[bname].TLatex_eff_rej.Draw()
    CMS_label.Draw()
    file_name = '../plots/eff_rej/g_multieff_%s_%s_%s'%(label, bname, tname)
    
    print_name = '%s.eps'%file_name
    canvas_tmp.Print(print_name)
    objects_to_save.append(canvas_tmp)
    objects_to_save.append(mg)
    return file_name