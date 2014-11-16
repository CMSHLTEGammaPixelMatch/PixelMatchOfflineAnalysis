from module_eff_rej import eff_rej_curve
from module_legend  import make_legend, fill_legend
from module_sample  import beam_names, beams, trigger_names, triggers, all_samples, trigger_names, triggers
from module_vars    import var_names, variables, region_names, regions
from module_plot    import plot_multiple_histograms, plot_multiple_graphs

##########################################################################################
# Latex snippets                                                                         #
##########################################################################################
def latex_var_table(vlatex, vnames, vtype, cname, type, histograms_in, objects_to_save):
    lines = []
    lines.append('\\begin{figure}[!bht]')
    lines.append('  \\begin{center}')
    lines.append('    \\begin{tabular}{cc}')
    image_counter = 0
    
    tname = trigger_names[0]
    caption = caption_var(vlatex, tname)
    if type=='eff':
        caption = caption_eff(vlatex, tname)
    
    for rname in region_names:
        for bname in beam_names:
            histograms = []
            for s in all_samples.samples:
                sname = s.name
                if bname in sname and tname in sname:
                    hname = 'h_%s_%s_%s_%s_%s'%(type, vnames[rname], sname, rname, cname)
                    histograms.append(histograms_in[hname])
            image_counter = image_counter+1
            suffix = '&' if image_counter%2==1 else '\\\\'
            legend = make_legend(0.1,0.85,0.55,0.7)
            fill_legend(legend, [bname,tname])
            figure_name = plot_multiple_histograms(histograms, legend, bname, tname, rname, vtype, cname, '', type, 'vanilla', objects_to_save)
            lines.append('      \\includegraphics[width=0.4\\textwidth]{%s} %s'%(figure_name, suffix))
    lines.append('    \\end{tabular}')
    lines.append('  \\caption{%s}'%caption)
    lines.append('  \\label{fig:%s_%s_%s}'%(type, vtype, cname))
    lines.append('  \\end{center}')
    lines.append('\\end{figure}')
    lines.append('\\clearpage')
    return '\n'.join(lines)

def latex_var_table_by_beforeAfter(vlatex, vnames, vtype, cname, type, histograms_in, objects_to_save):
    lines = []
    lines.append('\\begin{figure}[!bht]')
    lines.append('  \\begin{center}')
    lines.append('    \\begin{tabular}{cc}')
    image_counter = 0
    
    tname = trigger_names[0]
    caption = caption_var_by_beforeAfter(vlatex, tname)
    
    for rname in region_names:
        for bname in beam_names:
            histograms = []
            for s in all_samples.samples:
                sname = s.name
                if bname in sname and tname in sname:
                    aname = '_after'
                    hname = 'h_%s_%s_%s_%s_%s%s'%(type, vnames[rname], sname, rname, cname, aname)
                    histograms.append(histograms_in[hname])
            image_counter = image_counter+1
            suffix = '&' if image_counter%2==1 else '\\\\'
            legend = make_legend(0.1,0.85,0.55,0.7)
            fill_legend(legend, [bname,tname])
            figure_name = plot_multiple_histograms(histograms, legend, bname, tname, rname, vtype, cname, '_after', type, 'beforeAfter', objects_to_save)
            lines.append('      \\includegraphics[width=0.4\\textwidth]{%s} %s'%(figure_name, suffix))
    lines.append('    \\end{tabular}')
    lines.append('  \\caption{%s}'%caption)
    lines.append('  \\label{fig:%s_%s_%s_after}'%(type, vtype, cname))
    lines.append('  \\end{center}')
    lines.append('\\end{figure}')
    lines.append('\\clearpage')
    return '\n'.join(lines)
    
def latex_var_table_by_charge(vlatex, vnames, vtype, bname, type, histograms_in, objects_to_save):
    lines = []
    lines.append('\\begin{figure}[!bht]')
    lines.append('  \\begin{center}')
    lines.append('    \\begin{tabular}{cc}')
    image_counter = 0
    
    tname = trigger_names[0]
    caption = caption_var_by_charge(vlatex, tname)
    if type=='eff':
        caption = caption_eff_by_charge(vlatex, tname)
    
    for rname in region_names:
        for cname in ['ep','em']:
            histograms = []
            for s in all_samples.samples:
                sname = s.name
                if bname in sname and tname in sname:
                    hname = 'h_%s_%s_%s_%s_%s'%(type, vnames[rname], sname, rname, cname)
                    histograms.append(histograms_in[hname])
            image_counter = image_counter+1
            suffix = '&' if image_counter%2==1 else '\\\\'
            legend = make_legend(0.1,0.85,0.55,0.7)
            fill_legend(legend, [bname,tname])
            figure_name = plot_multiple_histograms(histograms, legend, bname, tname, rname, vtype, cname, '', type, 'charge', objects_to_save)
            lines.append('      \\includegraphics[width=0.4\\textwidth]{%s} %s'%(figure_name, suffix))
    lines.append('    \\end{tabular}')
    lines.append('  \\caption{%s}'%caption)
    lines.append('  \\label{fig:%s_%s_byCharge}'%(type, vtype))
    lines.append('  \\end{center}')
    lines.append('\\end{figure}')
    lines.append('\\clearpage')
    return '\n'.join(lines)

def latex_var_table_by_trigger(vlatex, vnames, vtype, bname, type, histograms_in, objects_to_save):
    lines = []
    lines.append('\\begin{figure}[!bht]')
    lines.append('  \\begin{center}')
    lines.append('    \\begin{tabular}{cc}')
    image_counter = 0
    
    cname = 'ea'
    caption = caption_var_by_trigger(vlatex)
    if type=='eff':
        caption = caption_eff_by_trigger(vlatex)
    
    for rname in region_names:
        for tname in trigger_names:
            histograms = []
            for s in all_samples.samples:
                sname = s.name
                if bname in sname and tname in sname:
                    hname = 'h_%s_%s_%s_%s_%s'%(type, vnames[rname], sname, rname, cname)
                    histograms.append(histograms_in[hname])
            image_counter = image_counter+1
            suffix = '&' if image_counter%2==1 else '\\\\'
            legend = make_legend(0.1,0.85,0.55,0.7)
            fill_legend(legend, [bname,tname])
            figure_name = plot_multiple_histograms(histograms, legend, bname, tname, rname, vtype, cname, '', type, 'trigger', objects_to_save)
            lines.append('      \\includegraphics[width=0.4\\textwidth]{%s} %s'%(figure_name, suffix))
    lines.append('    \\end{tabular}')
    lines.append('  \\caption{%s}'%caption)
    lines.append('  \\label{fig:%s_%s_byTrigger}'%(type, vtype))
    lines.append('  \\end{center}')
    lines.append('\\end{figure}')
    lines.append('\\clearpage')
    return '\n'.join(lines)

def latex_multieff(latex, vnames, vtype, cname, graphs_eff, objects_to_save):
    lines = []
    lines.append('\\begin{figure}[!bht]')
    lines.append('  \\begin{center}')
    lines.append('    \\begin{tabular}{cc}')
    image_counter = 0
    caption = 'The signal efficiency-fake rate curves as a function of $%s$ for %s electrons at $8\\tev$ (top) and $13\\tev$ (bottom) for events firing the %s trigger (left) and the %s trigger (right).'%(latex, regions['A'].name.lower(), triggers[trigger_names[0]].short_latex, triggers[trigger_names[1]].short_latex )
    
    for bname in beam_names:
        for tname in trigger_names:
            graphs = []
            legend = make_legend(0.3,0.4,0.9,0.2)
            for rname in region_names:
                gname = 'g_%s_%s_%s_%s'%(vnames[rname], bname, tname, rname)
                g = graphs_eff[gname]
                regions[rname].set_style(g)
                graphs.append(g)
                legend.AddEntry(g, regions[rname].ROOT_label, 'pl')
            
            image_counter = image_counter+1
            suffix = '&' if image_counter%2==1 else '\\\\'
            figure_name = plot_multiple_graphs(graphs, legend, objects_to_save, bname, tname, cname, vtype)
            lines.append('      \\includegraphics[width=0.4\\textwidth]{%s} %s'%(figure_name, suffix))
    lines.append('    \\end{tabular}')
    lines.append('  \\caption{%s}'%caption)
    lines.append('  \\label{fig:multieff_%s_%s}'%(vtype, cname))
    lines.append('  \\end{center}')
    lines.append('\\end{figure}')
    return '\n'.join(lines)

def caption_var(vlatex, tname):
    return 'The spectra of $%s$ for barrel electrons (top), intermediate electrons (middle), and forward electrons (bottom) at $8\\tev$ (left) and $13\\tev$ (right) for events firing the %s trigger.'%(vlatex, triggers[tname].short_latex )

def caption_eff(vlatex, tname):
    return 'Efficiency curves as a function of $%s$ for barrel electrons (top), intermediate electrons (middle), and forward electrons (bottom) at $8\\tev$ (left) and $13\\tev$ (right) for events firing the %s trigger.'%(vlatex, triggers[tname].short_latex )

def caption_var_by_charge(vlatex, tname):
    return 'The spectra of $%s$ for barrel electrons (top), intermediate electrons (middle), and forward electrons (bottom) for $e^+$ (left) and $e^-$ (right) for events firing the %s trigger.'%(vlatex, triggers[tname].short_latex )

def caption_var_by_beforeAfter(vlatex, tname):
    return 'The spectra of $%s$ for barrel electrons (top), intermediate electrons (middle), and forward electrons (bottom) for before (left) and after (right) a selection on $s$ for events firing the %s trigger.'%(vlatex, triggers[tname].short_latex )

def caption_eff_by_charge(vlatex, tname):
    return 'Efficiency curves as a function of $%s$ for barrel electrons (top), intermediate electrons (middle), and forward electrons (bottom) at $8\\tev$ (left) and $13\\tev$ (right) for events firing the %s trigger.'%(vlatex, triggers[tname].short_latex )

def caption_var_by_trigger(vlatex):
    return 'The spectra of $%s$ for barrel electrons (top), intermediate electrons (middle), and forward electrons (bottom) for events firing the %s trigger (left) and the %s trigger (right) at $8 \\tev$.'%(vlatex, triggers[trigger_names[0]].short_latex, triggers[trigger_names[1]].short_latex )

def caption_eff_by_trigger(vlatex, tname):
    return 'Efficiency curves as a function of $%s$ for barrel electrons (top), intermediate electrons (middle), and forward electrons (bottom) for events firing the %s trigger (left) and the %s trigger (right) at $8 \\tev$.'%(vlatex, triggers[trigger_names[0]].short_latex, triggers[trigger_names[1]].short_latex )

def caption_var_old(vname, rname):
    return 'The spectra of $%s$ for %s electrons at $8\\tev$ (top) and $13\\tev$ (bottom) for events firing the %s trigger (left) and the %s trigger (right).'%(variables[vname].latex, regions[rname].name.lower(), triggers[trigger_names[0]].short_latex, triggers[trigger_names[1]].short_latex )

def caption_eff_old(vname, rname):
    return 'Efficiency curves as a function of $%s$ for %s electrons at $8\\tev$ (top) and $13\\tev$ (bottom) for events firing the %s trigger (left) and the %s trigger (right).'%(variables[vname].latex, regions[rname].name.lower(), triggers[trigger_names[0]].short_latex, triggers[trigger_names[1]].short_latex )