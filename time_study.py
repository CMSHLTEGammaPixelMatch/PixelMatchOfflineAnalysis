import os.path, math, ROOT, sys

ROOT.gROOT.SetBatch(ROOT.kTRUE)

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

class timing_object:
    def __init__(self, parent, module, type):
        self.parent = parent
        self.module = module
        self.type   = type
        self.values = []
        self.min  = 1e6
        self.max  =   0
        self.mean =   0
        self.var  =   0
    def find_parameters(self, print_out):
        self.mean = 0
        s1 = 0
        s2 = 0
        for v in self.values:
            if v < self.min:
                self.min = v
            if v > self.max:
                self.max = v
            self.mean = self.mean + v
            s1 = s1 + v
            s2 = s2 + v*v
        n = len(self.values)
        self.mean = self.mean/n if n>0 else 0
        self.var  = (n*s2-s1*s1)/(n*(n-1)) if n>0 else 1
        
        if print_out:
            print '%s %s'%(self.module, self.type)
            print 'minimum : %.3g'%self.min
            print 'maximum : %.3g'%self.max
            print 'mean    : %.3g'%self.mean
            print 'variance: %.3g'%self.var
            print
    def make_histogram(self, h_in):
        hName = 'h_timing_%s_%s_%s'%(self.parent.name, self.module, self.type)
        h = h_in.Clone(hName)
        for v in self.values:
            h.Fill(v)
        self.histogram = h
        return h

class task_wrapper:
    def __init__(self, name, crab_name, nJobs):
        self.name      = name
        self.crab_name = crab_name
        self.nJobs     = nJobs
        
        self.timings = {}
        for module in module_names:
            self.timings[module] = {}
            for type in type_names:
                self.timings[module][type] = timing_object(self, module, type)
        
    def log_filename(self, i):
        return '%s/res/CMSSW_%d.stdout'%(self.crab_name, i)
    def parse_files(self):
        for i in range(0, self.nJobs):
            filename = self.log_filename(i)
            if not os.path.isfile(filename):
                continue
            f = open(filename,'r')
            for l in f:
                if 'TimeReport' not in l:
                    continue
                if 'PixelMatchFilter' not in l:
                    continue
                words = l.split()
                if len(words) != 8:
                    continue
                if 'PixelMatchFilterAnalysis' in l:
                    pass
                elif 'PixelMatchFilterS' in l:
                    self.timings['PixelMatchFilterS']['perEvent'    ].values.append(1e3*float(words[1]))
                    self.timings['PixelMatchFilterS']['perModuleRun'].values.append(1e3*float(words[3]))
                elif 'PixelMatchFilter' in l:
                    self.timings['PixelMatchFilter' ]['perEvent'    ].values.append(1e3*float(words[1]))
                    self.timings['PixelMatchFilter' ]['perModuleRun'].values.append(1e3*float(words[3]))
    def find_parameters(self, print_out):
        for m in self.timings:
            for t in self.timings[m]:
                self.timings[m][t].find_parameters(print_out)
    def get_min_max(self):
        self.min =  1e6
        self.max = -1e6
        for m in self.timings:
            for t in self.timings[m]:
                if self.timings[m][t].min < self.min:
                    self.min = self.timings[m][t].min
                if self.timings[m][t].max > self.max:
                    self.max = self.timings[m][t].max

class module_object:
    def __init__(self, name, color, marker, title):
        self.name   = name
        self.color  = color
        self.marker = marker
        self.title  = title

class type_object:
    def __init__(self, name, axis_title, upper):
        self.name = name
        self.axis_title = axis_title
        self.upper = upper

modules = {}
modules['PixelMatchFilter'        ] = module_object('PixelMatchFilter'         , ROOT.kRed   , 20, 'Pixel match filter (normal)'                     )
modules['PixelMatchFilterS'       ] = module_object('PixelMatchFilterS'        , ROOT.kBlue  , 25, 'Pixel match filter (including s^{2} calculation)')
module_names = [ 'PixelMatchFilter' , 'PixelMatchFilterS' ] #, 'PixelMatchFilterAnalysis' ]

types = {}
types['perEvent'    ] = type_object('perEvent'    , 'time per event'     , 0.05)
types['perModuleRun'] = type_object('perModuleRun', 'time per module run', 0.05)
type_names = [ 'perEvent' , 'perModuleRun' ]

legend = ROOT.TLegend(0.15,0.8,0.8,0.6)
legend.SetFillColor(ROOT.kWhite)
legend.SetBorderSize(0)
legend.SetShadowColor(0)

tasks = {}
tasks['QCD_Pt_30_80_13TeV_25ns_trigger_27'  ] = task_wrapper('QCD_Pt_30_80_13TeV_25ns_trigger_27'  , '../crab/crab_0_140314_145047', 117)
tasks['QCD_Pt_30_80_8TeV_50ns_trigger_27'   ] = task_wrapper('QCD_Pt_30_80_8TeV_50ns_trigger_27'   , '../crab/crab_0_140314_144623', 179)
tasks['DoubleElectron_trigger_27'           ] = task_wrapper('DoubleElectron_trigger_27'           , '../crab/crab_0_140314_144159',  59)
tasks['Zee_8TeV_50ns_trigger_27'            ] = task_wrapper('Zee_8TeV_50ns_trigger_27'            , '../crab/crab_0_140310_145620',  19)
tasks['Zee_8TeV_25ns_trigger_27'            ] = task_wrapper('Zee_8TeV_25ns_trigger_27'            , '../crab/crab_0_140314_145302',  19)
tasks['Zee_13TeV_25ns_trigger_27'           ] = task_wrapper('Zee_13TeV_25ns_trigger_27'           , '../crab/crab_0_140314_145414',  47)
tasks['ttbar_13TeV_25ns_trigger_27'         ] = task_wrapper('ttbar_13TeV_25ns_trigger_27'         , '../crab/crab_0_140314_145509', 490)

tasks['QCD_Pt_30_80_13TeV_25ns_trigger_18_7'] = task_wrapper('QCD_Pt_30_80_13TeV_25ns_trigger_18_7', '../crab/crab_0_140317_134519', 147)
tasks['QCD_Pt_30_80_8TeV_50ns_trigger_18_7' ] = task_wrapper('QCD_Pt_30_80_8TeV_50ns_trigger_18_7' , '../crab/crab_0_140317_133818', 117)
tasks['DoubleElectron_trigger_18_7'         ] = task_wrapper('DoubleElectron_trigger_18_7'         , '../crab/crab_0_140317_134644',  59)
tasks['Zee_8TeV_50ns_trigger_18_7'          ] = task_wrapper('Zee_8TeV_50ns_trigger_18_7'          , '../crab/crab_0_140317_121806',  19)
tasks['Zee_8TeV_25ns_trigger_18_7'          ] = task_wrapper('Zee_8TeV_25ns_trigger_18_7'          , '../crab/crab_0_140317_133729',  18)
tasks['Zee_13TeV_25ns_trigger_18_7'         ] = task_wrapper('Zee_13TeV_25ns_trigger_18_7'         , '../crab/crab_0_140318_175913',  47)
tasks['ttbar_13TeV_25ns_trigger_18_7'       ] = task_wrapper('ttbar_13TeV_25ns_trigger_18_7'       , '../crab/crab_0_140317_172322', 490)

task_names = ['QCD_Pt_30_80_13TeV_25ns_trigger_27' , 'QCD_Pt_30_80_8TeV_50ns_trigger_27' , 'DoubleElectron_trigger_27' , 'Zee_8TeV_50ns_trigger_27' , 'Zee_8TeV_25ns_trigger_27' , 'Zee_13TeV_25ns_trigger_27' , 'ttbar_13TeV_25ns_trigger_27'  , 'QCD_Pt_30_80_13TeV_25ns_trigger_18_7' , 'QCD_Pt_30_80_8TeV_50ns_trigger_18_7' , 'DoubleElectron_trigger_18_7' , 'Zee_8TeV_50ns_trigger_18_7' , 'Zee_8TeV_25ns_trigger_18_7' , 'Zee_13TeV_25ns_trigger_18_7' , 'ttbar_13TeV_25ns_trigger_18_7' ]

min  = 1e6
max  =   0
for tname in task_names:
    t = tasks[tname]
    t.parse_files()
    t.find_parameters(False)
    t.get_min_max()
    if t.min < min:
        min = t.min
    if t.max > max:
        max = t.max
        
hBase = {}
nBins =   20
lower =    0
for mname in module_names:
    hBase[mname] = {}
    for type in types:
        hName = 'hBase_%s_%s'%(mname, type) ;
        h = ROOT.TH1F(hName, '', nBins, lower, types[type].upper)
        h.GetXaxis().SetTitle('%s [ms]'%types[type].axis_title)
        h.GetYaxis().SetTitle('number of jobs')
        h.SetLineColor  (modules[mname].color)
        h.SetMarkerColor(modules[mname].color)
        h.SetMarkerStyle(modules[mname].marker)
        h.GetYaxis().SetLabelSize(0.025)
        hBase[mname][type] = h

for mname in module_names:
    print mname , hBase[mname][type_names[0]].GetLineColor()
    legend.AddEntry(hBase[mname][type_names[0]], modules[mname].title, 'p')

file = ROOT.TFile('timing.root','RECREATE')
for mname in module_names:
    for type in type_names:
        for t in task_names:
            h = tasks[t].timings[mname][type].make_histogram(hBase[mname][type])
            h.SetMaximum(2*h.GetMaximum())
            h.Write()
file.Write()

# Stuff for making labels
sample_names = [ 'QCD_Pt_30_80_13TeV_25ns' , 'QCD_Pt_30_80_8TeV_50ns' , 'DoubleElectron' , 'Zee_8TeV_50ns' , 'Zee_8TeV_25ns' , 'Zee_13TeV_25ns' , 'ttbar_13TeV_25ns' ]
sample_labels = {}
sample_labels['QCD_Pt_30_80_13TeV_25ns'] = ROOT.TLatex(0.2, 0.82, 'QCD P_{T}[30,80] 13 TeV 25 ns' )
sample_labels['QCD_Pt_30_80_8TeV_50ns' ] = ROOT.TLatex(0.2, 0.82, 'QCD P_{T}[30,80] 8 TeV 50 ns'  )
sample_labels['DoubleElectron'         ] = ROOT.TLatex(0.2, 0.82, 'DoubleElectron 8TeV 50ns'      )
sample_labels['Zee_8TeV_50ns'          ] = ROOT.TLatex(0.2, 0.82, 'Z#rightarrowee 8 TeV 50 ns'    )
sample_labels['Zee_8TeV_25ns'          ] = ROOT.TLatex(0.2, 0.82, 'Z#rightarrowee 8 TeV 25 ns'    )
sample_labels['Zee_13TeV_25ns'         ] = ROOT.TLatex(0.2, 0.82, 'Z#rightarrowee 13 TeV 25 ns'   )
sample_labels['ttbar_13TeV_25ns'       ] = ROOT.TLatex(0.2, 0.82, 't#bar{t} 13 TeV 25 ns'         )
for sname in sample_labels:
    l = sample_labels[sname]
    l.SetNDC()


sample_titles = {}
sample_titles['QCD_Pt_30_80_13TeV_25ns'] = 'QCD P_{T}[30,80] 13 TeV 25 ns'
sample_titles['QCD_Pt_30_80_8TeV_50ns' ] = 'QCD P_{T}[30,80] 8 TeV 50 ns'
sample_titles['DoubleElectron'         ] = 'DoubleElectron 8TeV 50ns'
sample_titles['Zee_8TeV_50ns'          ] = 'Z\\to ee 8 TeV 50 ns'
sample_titles['Zee_8TeV_25ns'          ] = 'Z\\to ee 8 TeV 25 ns'
sample_titles['Zee_13TeV_25ns'         ] = 'Z\\to ee 13 TeV 25 ns'
sample_titles['ttbar_13TeV_25ns'       ] = 't\\bar{t} 13 TeV 25 ns'

trigger_names  = [ 'trigger_27' , 'trigger_18_7' ]
trigger_titles = {}
trigger_titles['trigger_27'  ] = 'HLT_Ele27_WP80_v13'
trigger_titles['trigger_18_7'] = 'HLT_Ele17_Ele8_v19'
trigger_tlatex = {}
for tname in trigger_names:
    trigger_tlatex[tname] = ROOT.TLatex(0.05,0.95,trigger_titles[tname])
    trigger_tlatex[tname].SetTextSize(0.04)
    trigger_tlatex[tname].SetNDC()


canvas = ROOT.TCanvas('canvas', '', 100, 100, 600, 600)
for task in task_names:
    t = tasks[task]
    for type in type_names:
        hMax = 0
        max_value = 0
        for mname in module_names:
            h = t.timings[mname][type].histogram
            if h.GetMaximum() > max_value:
                max_value = h.GetMaximum()
                hMax = h
        if hMax==0:
            continue
        hMax.Draw('pe')
        for mname in module_names:
            t.timings[mname][type].histogram.Draw('pe:sames')
            legend.Draw()
            for trigger in trigger_names:
                if trigger in task:
                    trigger_tlatex[trigger].Draw()
            for sname in sample_labels:
                if sname in task:
                    sample_labels[sname].Draw()
        canvas.Print('plots/timing/%s_%s.eps'%(task, type))
        
        if 'ttbar' not in task:
            continue
        print task , type
        for bin in range(1,t.timings[module_names[0]][type].histogram.GetNbinsX()+1):
            string = '%3d:  '%bin
            for mname in module_names:
                string = '%s  %8.4g  '%(string, t.timings[mname][type].histogram.GetBinContent(bin))
            
t_27   = tasks['ttbar_13TeV_25ns_trigger_27'  ]
t_18_7 = tasks['ttbar_13TeV_25ns_trigger_18_7']
t_27   = tasks['DoubleElectron_trigger_27'    ]
t_18_7 = tasks['DoubleElectron_trigger_18_7'  ]
for type in type_names:
    for mname in module_names:
        print '%20s  %20s  %8.4g  %8.4g'%(mname , type , t_27.timings[mname][type].mean , math.sqrt(t_27.timings[mname][type].var))

sys.exit()
# Write summary table
lines = []
lines.append('\\begin{table}')
lines.append('  \\begin{center}')
lines.append('    \\begin{tabular}{c|ccc|ccc}')
lines.append('      \\hline')
lines.append('      Sample name & \\multicolumn{3}{c}{Single electron trigger} & \\multicolumn{3}{c}{Double electron trigger} \\\\')
lines.append('                  & Timing without $s^2$ ($\\mathrm{ms}$) & Timing with $s^2$ ($\\mathrm{ms}$) & $n_{jobs}$ & Timing without $s^2$ ($\\mathrm{ms}$) & Timing with $s^2$ ($\\mathrm{ms}$)  & $n_{jobs}$ \\\\')
lines.append('      \\hline')

for sname in sample_names:
    t_27   = tasks['%s_trigger_27'  %sname]
    t_18_7 = tasks['%s_trigger_18_7'%sname]
    
    mean_without_27    =           t_27.timings['PixelMatchFilter' ]['perEvent'].mean
    sigma_without_27   = math.sqrt(t_27.timings['PixelMatchFilter' ]['perEvent'].var )
    mean_with_27       =           t_27.timings['PixelMatchFilterS']['perEvent'].mean
    sigma_with_27      = math.sqrt(t_27.timings['PixelMatchFilterS']['perEvent'].var )
    n_27 = t_27.nJobs
        
    mean_without_18_7  =           t_18_7.timings['PixelMatchFilter' ]['perEvent'].mean
    sigma_without_18_7 = math.sqrt(t_18_7.timings['PixelMatchFilter' ]['perEvent'].var )
    mean_with_18_7     =           t_18_7.timings['PixelMatchFilterS']['perEvent'].mean
    sigma_with_18_7    = math.sqrt(t_18_7.timings['PixelMatchFilterS']['perEvent'].var )
    n_18_7 = t_18_7.nJobs
    
    sample_title = sample_titles[sname]
    
    lines.append( '      $%40s$ & $%8.4g \\pm %8.4g$ & $%8.4g \\pm %8.4g$ & $%d$ & $%8.4g \\pm %8.4g$ & $%8.4g \\pm %8.4g$ & $%d$ \\\\' %(sample_titles[sname], mean_without_27, sigma_without_27, mean_with_27, sigma_with_27, n_27, mean_without_18_7, sigma_without_18_7, mean_with_18_7, sigma_with_18_7, n_18_7) )

lines.append('      \\hline')
lines.append('    \\end{tabular}')
lines.append('  \\caption{Timing information (per event) for the variious samples with and without the calculation of $s^2$, for the single and double electron triggers.}')
lines.append('  \\label{tab:timing}')
lines.append('  \\end{center}')
lines.append('\\end{table}')

print '\n'.join(lines)
