import ROOT
from module_legend import make_legend, fill_legend
from module_sample import beam_names, beams, trigger_names, triggers, all_samples, trigger_names, triggers
from module_vars   import region_names, regions

hBase_pt = ROOT.TH1F('hBase_pt', '', 100, 0, 150)
hBase_pt.GetXaxis().SetTitle('E_{T}(e) [GeV]')
hBase_pt.GetYaxis().SetTitle('superclusters per GeV')
hBase_pt.GetYaxis().SetLabelSize(0.03)
hBase_pt.GetYaxis().SetTitleOffset(1.1)
hBase_pt.SetMarkerStyle(20)
hBase_pt.Sumw2()

hBase_pt_pass = hBase_pt.Clone('hBase_pt_pass')
hBase_pt_all  = hBase_pt.Clone('hBase_pt_all' )
hBase_pt_pass.SetLineColor(ROOT.kRed)
hBase_pt_pass.SetMarkerColor(ROOT.kRed)
hBase_pt_pass.SetMarkerStyle(20)
hBase_pt_all .SetLineColor(ROOT.kBlack)
hBase_pt_all .SetMarkerColor(ROOT.kBlack)
hBase_pt_all .SetMarkerStyle(22)

legend = ROOT.TLegend(0.5,0.7,0.85,0.55)
legend.SetFillColor(0)
legend.SetBorderSize(0)
legend.SetShadowColor(ROOT.kWhite)
legend.AddEntry(hBase_pt_all , '2011-2012 pixel window', 'pl')
legend.AddEntry(hBase_pt_pass, '#varepsilon=50% s cut' , 'pl')

ratio_label = ROOT.TLatex(0.13,0.65,'Ratio')
ratio_label.SetTextSize(0.15)
ratio_label.SetNDC()

##########################################################################################
# ET plots                                                                               #
##########################################################################################
class et_plot_wrapper:
    def __init__(self, sample, rname):
        self.sname = sample.name
        self.rname = rname
        self.name  = 'et_%s_%s'%(self.sname, self.rname)
        self.sample = sample
        self.region = regions[rname]
        self.h_pt_pass = hBase_pt_pass.Clone('h_pt_pass_%s_%s'%(self.sname, rname))
        self.h_pt_all  = hBase_pt_all .Clone('h_pt_all_%s_%s' %(self.sname, rname))
        
    def fill(self, scut, objects_to_save):
        for ev in self.sample.events:
            same_region = False
            for el in ev.electrons:
                pt = el.p4.Pt()
                accept = False
                for helix in el.helices:
                    if helix.region!=self.rname:
                        continue
                    same_region = True
                    if helix.s_<scut:
                        accept = True
                        break
                if accept:
                    self.h_pt_pass.Fill(pt)
                if same_region:
                    self.h_pt_all.Fill(pt)
            
        max = -1e6
        for bin in range(1,self.h_pt_pass.GetNbinsX()+1):
            bin1 = self.h_pt_pass.GetBinContent(bin)+2*self.h_pt_pass.GetBinError(bin)
            bin2 = self.h_pt_all .GetBinContent(bin)+2*self.h_pt_all .GetBinError(bin)
            if bin1 > max:
                max = bin1
            if bin2 > max:
                max = bin2
        max = 1.2*max
        self.h_pt_pass.SetMaximum(max)
        self.h_pt_all.SetMaximum(max)
        
        h1Name = self.h_pt_pass.GetName()
        self.hRatio = self.h_pt_pass.Clone( '%s_ratio'%h1Name )
        self.hRatio.Divide(self.h_pt_all)
        self.hRatio.GetXaxis().SetTitle('')
        self.hRatio.GetYaxis().SetTitle('')
        self.hRatio.GetXaxis().SetLabelSize(0.0)
        self.hRatio.GetYaxis().SetLabelSize(0.1)
        self.hRatio.SetMinimum(-0.5)
        self.hRatio.SetMaximum( 2.0)
        self.hRatio.SetMarkerColor(ROOT.kBlack)
        self.hRatio.SetLineColor(ROOT.kBlack)
        
        # Now perform a fit to see what kind of efficiency curve we get for the signal
        self.fit = ROOT.TF1('ET_ratio_fit_%s'%self.name, 'pol2')
        self.fit.SetParameters(0,0,0)
        self.hRatio.Fit(self.fit)
        
        self.a_value = self.fit.GetParameter(0)
        self.a_error = self.fit.GetParError(0)
        self.b_value = self.fit.GetParameter(1)
        self.b_error = self.fit.GetParError(1)
        self.c_value = self.fit.GetParameter(2)
        self.c_error = self.fit.GetParError(2)
      
        print 'y = %10.6f (%10.6f) + %10.6f (%10.6f)x + %10.6f (%10.6f)x^2'%(self.a_value, self.a_error, self.b_value, self.b_error, self.c_value, self.c_error)
        objects_to_save.append(self.fit)
        
    def print_canvas(self, objects_to_save):
        canvas = ROOT.TCanvas('canvas_ratio_%s'%self.name, '', 100, 100, 600, 800)
        y = 0.8
        pad1 = ROOT.TPad('pad1', 'The pad 80% of the height', 0.0, 1.0-y, 1.0,   1.0, ROOT.kWhite)
        pad2 = ROOT.TPad('pad2', 'The pad 20% of the height', 0.0,   0.0, 1.0, 1.0-y, ROOT.kWhite)
        pad1.SetGridx()
        pad1.SetGridy()
        pad2.SetGridy()
        pad1.Draw()
        pad2.Draw()
                
        pad1.cd()
        self.h_pt_all.Draw('pe')
        self.h_pt_pass.Draw('pe:sames')
        self.h_pt_all.Draw('pe:sames')
        
        regions[self.rname].draw_label('ea')
        legend.Draw()
        self.sample.trigger.TLatex.Draw()
        
        pad2.cd()
        self.hRatio.Draw('pe')
        
        ratio_label.Draw()
        
        self.plot_name = '../plots/et/h_pt_50_%s_%s.eps'%(self.sname,self.rname)
        canvas.Update()
        canvas.Print(self.plot_name)
        objects_to_save.append(canvas)
        objects_to_save.append(self.h_pt_all)
        objects_to_save.append(self.h_pt_pass)
        objects_to_save.append(self.hRatio)
        return self.plot_name

def et_latex(epws, rname):
    lines = []
    lines.append('\\begin{figure}[!bht]')
    lines.append('  \\begin{center}')
    lines.append('    \\begin{tabular}{cc}')
    image_counter = 0
    t1 = triggers[trigger_names[0]]
    t2 = triggers[trigger_names[1]]
    caption = 'The $E_T$ spectra of %s electrons passing a $\\varepsilon_{sig}=50\\%%$ $s$ selection at $8 \\tev 50 \\ns$ (top) and $13 \\tev 25 \\ns$ (bottom) for events firing the %s trigger (left) and the %s trigger (right) for $Z\to ee$ samples.  The stability of the selections can be seen in the ratio plots.'%(regions[rname].name.lower(),  t1.short_latex,  t2.short_latex)
    for bname in beam_names:
        for tname in trigger_names:
            ename = 'Zee_%s_%s_%s'%(bname, tname, rname)
            image_counter = image_counter+1
            suffix = '&' if image_counter%2==1 else '\\\\'
            figure_name = epws[ename].plot_name
            lines.append('      \\includegraphics[width=0.4\\textwidth]{%s} %s'%(figure_name, suffix))
    lines.append('    \\end{tabular}')
    lines.append('  \\caption{%s}'%caption)
    lines.append('  \\label{fig:pt_%s}'%(rname))
    lines.append('  \\end{center}')
    lines.append('\\end{figure}')
    return '\n'.join(lines)
