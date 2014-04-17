from module_sample import all_samples
import ROOT

##########################################################################################
# Legends                                                                                #
##########################################################################################
def make_legend(x1, y1, x2, y2):
    legend = ROOT.TLegend(x1,y1,x2,y2)
    legend.SetShadowColor(ROOT.kWhite)
    legend.SetFillColor(ROOT.kWhite)
    legend.SetBorderSize(0)
    return legend
def fill_legend(legend, filters):
    for s in all_samples.samples:
        sname = s.name
        accept = True
        for f in filters:
            if f not in sname:
                accept = False
                break
        if accept:
            legend.AddEntry(s.hBase, s.process.ROOT_title, 'pe')