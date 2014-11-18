import ROOT
import numpy
from module_sample import beam_names, beams, trigger_names, triggers, all_samples
from module_vars   import region_names, regions, variables

##########################################################################################
# Efficiency-rejection curves                                                            #
##########################################################################################
class eff_target:
    def __init__(self, type, target):
        self.type   = type
        self.value  = 0
        self.cut    = -999
        self.target = target
        self.actual = -999
    def seek_value(self, sig, bkg, x):
        if   self.type=='sig':
            best_dSigEff = 1e6
            for i in range(0, len(sig)):
                dSigEff = abs(sig[i]-self.target)
                if dSigEff < best_dSigEff:
                    best_dSigEff = dSigEff
                    self.value  = bkg[i]
                    self.actual = sig[i]
                    self.cut    =   x[i]
        elif self.type=='bkg':
            best_dBkgEff = 1e6
            for i in range(0, len(sig)):
                dBkgEff = abs(bkg[i]-self.target)
                if dBkgEff < best_dBkgEff:
                    best_dBkgEff = dBkgEff
                    self.value  = sig[i]
                    self.actual = bkg[i]
                    self.cut    =   x[i]

cw = 600
ch = 600

def make_canvas(cname):
    canvas = ROOT.TCanvas('canavs_%s'%cname, '', 100, 100, cw, ch)
    canvas.SetGridx()
    canvas.SetGridy()
    return canvas

class eff_rej_curve:
    def __init__(self, bname, tname, rname, vname, pname_sig, pname_bkg, eff_target_values_sig, eff_target_values_bkg   , histograms_eff):
        self.beam    =     beams[bname]
        self.trigger =  triggers[tname]
        self.region  =   regions[rname]
        self.var     = variables[vname]
        self.name = '%s_%s_%s_%s'%(vname, bname, tname, rname)
        
        self.sig_eff_targets = []
        self.bkg_eff_targets = []
        for etvs in eff_target_values_sig:
            self.sig_eff_targets.append(eff_target('sig', etvs))
        for etvb in eff_target_values_bkg:
            self.bkg_eff_targets.append(eff_target('bkg', etvb))
        
        hName_sig = 'h_eff_%s_%s_%s_%s_%s_ea'%(vname, pname_sig, bname, tname, rname)
        hName_bkg = 'h_eff_%s_%s_%s_%s_%s_ea'%(vname, pname_bkg, bname, tname, rname)
        self.h_sig = histograms_eff[hName_sig]
        self.h_bkg = histograms_eff[hName_bkg]
        
        self.eff_sig = [0]
        self.eff_bkg = [0]
        self.x_value = [0]
        
        for bin in range(1, self.h_sig.GetNbinsX()+1):
            self.eff_sig.append(self.h_sig.GetBinContent(bin))
            self.eff_bkg.append(self.h_bkg.GetBinContent(bin))
            self.x_value.append(self.h_bkg.GetBinCenter(bin) )
        
        for e in self.sig_eff_targets:
            e.seek_value(self.eff_sig, self.eff_bkg, self.x_value)
        for e in self.bkg_eff_targets:
            e.seek_value(self.eff_sig, self.eff_bkg, self.x_value)
        
        self.arr_eff_sig = numpy.array(self.eff_sig, 'd')
        self.arr_eff_bkg = numpy.array(self.eff_bkg, 'd')
        self.n = len(self.eff_sig)
        
        self.graph = ROOT.TGraph(self.n, self.arr_eff_bkg, self.arr_eff_sig)
        self.graph.GetXaxis().SetTitle('relative background efficiency')
        self.graph.GetYaxis().SetTitle('relative signal efficiency')
        self.graph.SetMarkerStyle(20)
        self.graph.SetName('g_rejeff_%s'%self.name)
        
        self.print_name = '../plots/eff_rej/h_rejeff_%s_%s_%s_%s_%s_%s.eps'%(vname, pname_sig, pname_bkg, bname, tname, rname)
    def plot(self, objects_to_save):
        cname = 'canavs_%s'%self.name
        canvas_tmp = make_canvas(cname)
        self.graph.Draw('ALP')
        canvas_tmp.Print(self.print_name)
        
    def latex_table_rows(self, type):
        lines = []
        type_latex       = 'signal'     if type=='sig' else 'background'
        other_type_latex = 'backgorund' if type=='sig' else 'signal'
        other_type       = 'bkg' if type=='sig' else 'sig'
        eff_targets = self.sig_eff_targets if type=='sig' else self.bkg_eff_targets
        lines.append('\\begin{table}[!bht]')
        lines.append('  \\begin{center}')
        lines.append('    \\begin{tabular}{cccc}')
        lines.append('      \\hline')
        lines.append('      Target %s efficiency & $%s$ & $\\varepsilon_{%s}$ & $\\varepsilon_{%s}$ \\\\ '%(type_latex, self.var.latex, type, other_type))
        lines.append('      \\hline')
        for e in eff_targets:
            lines.append('      $\\varepsilon_{%s}^{target} = %5.3f$ & $%8.4f$ & $%5.3f$ & $%5.3f$ \\\\'%(type, e.target, e.cut, e.actual , e.value))
        lines.append('      \\hline')
        lines.append('    \\end{tabular}')
        lines.append('    \\caption{Signal and background efficiencies for targeted %s efficiencies as a function of $%s$ for %s electrons at $%d\\tev %d\\ns$ for events firing the %s trigger.}'%(type_latex, self.var.latex, self.region.name.lower(), self.beam.energy, self.beam.bunch_spacing, self.trigger.short_latex))
        lines.append('    \\label{tab:eff_rej_%s}'%self.name)
        lines.append('  \\end{center}')
        lines.append('\\end{table}')
        return '\n'.join(lines)
    
def make_large_latex_table(bname, type, curves, vnames, v_summary, v_caption, v_power):
    eff_target_values_sig = [ 0.5 , 0.9 , 0.95 , 0.99 , 0.995 ]
    eff_target_values_bkg = [ 0.1 ,  0.3 ,  0.5 , 0.7 , 0.9 ]
    target_values = eff_target_values_sig if type=='sig' else eff_target_values_bkg
    cols = 'c|ccccc|ccccc'

    beam = beams[bname]
    lines = []
    lines.append('\\begin{table}[!bht]')
    lines.append('  \\begin{center}')
    lines.append('    \\begin{tabular}{%s}'%cols)
    lines.append('      \\hline')
    
    t1 = triggers[trigger_names[0]]
    t2 = triggers[trigger_names[1]]
    
    other_type       = 'bkg'        if type=='sig' else 'sig'
    type_latex       = 'signal'     if type=='sig' else 'background'
    other_type_latex = 'background' if type=='sig' else 'signal'
    
    caption = 'Efficiencies for signal and background for targeted %s efficiencies, as a function of $%s$ for $%s \\tev %s \\ns.$'%(type_latex, v_summary, beam.energy, beam.bunch_spacing)
    lines.append('      & \\multicolumn{%d}{c}{%s} & \\multicolumn{%d}{c}{%s} \\\\'%(len(target_values), t1.short_latex, len(target_values),  t2.short_latex) )
    for rname in region_names:
        lines.append('      \\hline')
        lines.append('      & \\multicolumn{%d}{c}{%s electrons} \\\\'%(2*len(target_values), regions[rname].name) )
        lines.append('      \\hline')
        
        var = variables[vnames[rname]]
        str = ''
        for trigger in [t1,t2]:
            cname = '%s_%s_%s_%s'%(var.name, bname, trigger.name, rname)
            c = curves[cname]
            for i in range(0,len(target_values)):
                cut = c.sig_eff_targets[i].cut if type=='sig' else c.bkg_eff_targets[i].cut
                if v_power!=0:
                    str = '%s & $<%.2f$'%(str, cut*pow(10,v_power))
                else:
                    str = '%s & $<%.2g$'%(str, cut)
        if v_power!=0:
            str = '      $|%s|\\times 10^{%d}$ %s \\\\'%(var.latex, v_power, str)
        else:
            str = '      $|%s|$ %s \\\\'%(var.latex, str)
        lines.append(str)
        
        str = ''
        for esig in target_values:
            str = '%s & $%.1f\\%%$'%(str, 100*esig)
        lines.append('      Target $\\varepsilon_{%s}$ %s %s \\\\'%(type,str,str))
        
        str = ''
        for trigger in [t1,t2]:
            cname = '%s_%s_%s_%s'%(var.name, bname, trigger.name, rname)
            c = curves[cname]
            for i in range(0,len(target_values)):
                value = c.sig_eff_targets[i].actual if type=='sig' else c.bkg_eff_targets[i].actual
                str = '%s & $%.1f\\%%$'%(str, 100*value)
        lines.append('      Actual $\\varepsilon_{%s} $ %s \\\\'%(type,str))
        
        str = ''
        for trigger in [t1,t2]:
            cname = '%s_%s_%s_%s'%(var.name, bname, trigger.name, rname)
            c = curves[cname]
            for i in range(0,len(target_values)):
                value = c.sig_eff_targets[i].value if type=='sig' else c.bkg_eff_targets[i].value
                str = '%s & $%.1f\\%%$'%(str, 100*value)
        lines.append('      Actual $\\varepsilon_{%s}$ %s \\\\'%(other_type,str))
        
    lines.append('      \\hline')
    lines.append('    \\end{tabular}')
    lines.append('    \\caption{%s}'%caption)
    lines.append('    \\label{tab:eff_rej_%s_%s_%s}'%(v_caption, bname, type))
    lines.append('  \\end{center}')
    lines.append('\\end{table}')
    return '\n'.join(lines)
    
    