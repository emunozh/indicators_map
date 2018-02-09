#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Tue 06 Feb 2018 13:36:58 CET

"""
import numpy as np

from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.models import HoverTool, ColumnDataSource, FactorRange
from bokeh.embed import components

COLORMAP = ["#1f78b4", "#33a02c", "#e31a1c", "#6a3d9a"]

def _make_bokeh_hm(dataframe_map, show_plot = False, post_title = ""):
    data = dataframe_map.copy()
    data = data.fillna(0)

    xname_a = data.columns.tolist()
    if isinstance(data.index.get_values()[0], str):
        yname_a = [i for i in data.index]
    else:
        yname_a = ["{} - {}".format(*i) for i in data.index.get_values()]
    counts = data.as_matrix()

    xname = []
    yname = []
    color = []
    alpha = []
    old_cat = "Unknown"
    col_inx = -1
    for i, node1 in enumerate(yname_a):
        for j, node2 in enumerate(xname_a):
            xname.append(node2)
            yname.append(node1)

            if '-' in node1:
                this_cat = node1.split(' - ')[0]
                alpha.append(min(counts[i,j]/4.0, 0.9) + 0.1)
            else:
                this_cat = "no"
                alpha.append(counts[i,j])
            if this_cat != old_cat:
                col_inx += 1
            if col_inx >= len(COLORMAP):
                col_inx = 0
            old_cat = this_cat


            if counts[i,j] == 0:
                color.append('#FFFFFF')
            else:
                color.append(COLORMAP[col_inx])

    source = ColumnDataSource(data=dict(
        xname=xname,
        yname=yname,
        colors=color,
        alphas=alpha,
        count=counts.flatten(),
    ))

    if len(post_title) >= 1:
        fig_title = "Inficators for ctaegory: {}".format(post_title)
    else:
        fig_title = "Inficators"

    p = figure(title=fig_title,
               x_axis_location="above", tools="hover,save",
               x_range = xname_a, y_range = yname_a
              )

    p.plot_width = len(xname_a) * 30
    p.plot_height = len(yname_a) * 30
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "10pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi/3

    p.rect('xname', 'yname', 1, 1, source = source,
           color = 'colors', alpha = 'alphas', line_color = None,
           hover_line_color = 'grey', hover_color = 'colors'
          )

    p.select_one(HoverTool).tooltips = [
        ('group', '@yname'),
        ('framework', '@xname'),
        ('count', '@count')]

    if show_plot:
        output_file("heatmap.html", title="indicators")
        show(p) # show the plot
        return(False)
    else:
        return(components(p))

def main():
    from indicators import indicator_map
    m = indicator_map()
    _ = _make_bokeh_hm(m._get_map(), show_plot = True)


if __name__ == "__main__":
    main()
