
# coding: utf-8

# In[66]:


import numpy as np

from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.models import HoverTool, ColumnDataSource, FactorRange

from indicators import dataframe_map, INX


# In[67]:


colormap = ["#1f78b4", "#33a02c", "#e31a1c", "#6a3d9a"]

data = dataframe_map.copy() #dataframe_trim_bin.loc[:, INX]#.values
data = data.fillna(0)

xname_a = data.columns.tolist()
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
        
        this_cat = node1.split(' - ')[0]
        if this_cat != old_cat:
            col_inx += 1
        if col_inx >= len(colormap):
            col_inx = 0
        old_cat = this_cat

        alpha.append(min(counts[i,j]/4.0, 0.9) + 0.1)

        if counts[i,j] == 0:
            color.append('#FFFFFF')
        else:
            color.append(colormap[col_inx])
        #if node1['group'] == node2['group']:
        #    color.append(colormap[node1['group']])
        #else:
        #    color.append('lightgrey')


# In[68]:


source = ColumnDataSource(data=dict(
    xname=xname,
    yname=yname,
    colors=color,
    alphas=alpha,
    count=counts.flatten(),
))

p = figure(title="Indicators",
           x_axis_location="above", tools="hover,save",
           x_range = xname_a, y_range = yname_a
          )

p.plot_width = len(xname_a) * 25
p.plot_height = len(yname_a) * 25
p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "5pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = np.pi/3

p.rect('xname', 'yname', 1, 1, source = source,
       color = 'colors', alpha = 'alphas', line_color = None,
       hover_line_color = 'grey', hover_color = 'colors'
      )

p.select_one(HoverTool).tooltips = [
    ('group', '@yname'),
    ('framework', '@xname'),
    ('count', '@count'),
]

#output_notebook()
output_file("les_mis.html", title="indicators")

show(p) # show the plot

