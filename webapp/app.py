#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Tue 06 Feb 2018 11:49:21 CET

"""
from flask import Flask, render_template, request, redirect
from indicators import indicator_map

app = Flask(__name__)

m = indicator_map()
# cat = 'Environment'
# sub_cat = 'Emissions'
# keyword = 'CO2'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/license')
def license():
    return render_template('license.html')

@app.route('/vizapp', methods=['GET', 'POST'])
def vizapp():
    try:
        cat = request.form['category']
        bokeh = request.form['bokeh']
    except:
        cat = 'Environment'
        bokeh = 'yes'
    if len(cat) <= 1:
        cat = False
    print(cat)
    print(bokeh)
    if bokeh == 'yes':
        fig = m.make_heatmap(category=cat, annot=False, use_bokeh=True)
        return render_template('vizapp_bokeh.html', script=fig[0], div=fig[1])
    else:
        fig = m.make_heatmap(category=cat, annot=True)
        print(fig)
        return render_template('vizapp_simple.html', fig=fig)


if __name__ == '__main__':
    app.debug = True
    app.run(port=33507)
