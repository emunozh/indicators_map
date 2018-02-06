#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
#Created by Esteban.

Sun 21 Jan 2018 01:15:06 PM CET

"""

import os
from os import path
import time
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from wordcloud import WordCloud, STOPWORDS
# internal
from plot import _make_bokeh_hm

class indicator_map():
    """Main class for the construction of heatmaps and tag-cluds."""

    def __init__(self,
            file_name = "Indicator matching",
            credentials = "credentials.json",
            tail = -650,
            cat_main = "Category",
            add_stopwords = list(),
            cat_second = "Abstract Indicator Name",
            figures_folder = "static/FIGURES",
            mask_file = "static/circular.png"):
        # make credential for Google API
        credentials_file = path.join(os.getcwd(), credentials)
        print('using {} as credentials'.format(credentials_file))
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        self.gc = gspread.authorize(credentials)
        # Class variables
        self.cat_main = cat_main
        self.cat_second = cat_second
        self.cat_all = [self.cat_main, self.cat_second]
        self.file_name = file_name
        self.cf = credentials
        self.mask_file = mask_file
        self.tail = tail
        self.add_stopwords = add_stopwords
        self.figures_folder = figures_folder

        start = time.clock()
        print("Fetching data from gdoc", end="... ")
        self._get_data()
        elapsed = time.clock(); print("OK  {0:0.2f}s".format(elapsed - start))
        start = time.clock()
        self._get_bin()
        elapsed = time.clock(); print("OK  {0:0.2f}s".format(elapsed - start))
        start = time.clock()
        print("Mapping data", end="... ")
        dataframe_map = self._get_map()
        dataframe_map_cat = self.dataframe_trim_bin.groupby([self.cat_main]).sum()
        self.dataframe_map_cat_rel = dataframe_map_cat.div(dataframe_map_cat.sum()).mul(100)
        elapsed = time.clock(); print("OK  {0:0.2f}s".format(elapsed - start))

        self.CE = ['Geng 2012', 'Ghisellini 2015', 'Haas 2015', 'Su 2013', 'EEA 2016']
        self.INX = [i for i in self.dataframe_trim.columns if i not in self.cat_all]

        self.wc = self._create_wc()

    def _get_data(self, worksheet=0, start_row=1):
        wks = self.gc.open(self.file_name).get_worksheet(worksheet)
        dataframe = pd.DataFrame(wks.get_all_records())
        self.dataframe_trim = dataframe.iloc[0:self.tail, start_row:]

    def _get_bin(self):
        self.dataframe_trim_bin = self.dataframe_trim.applymap(lambda x: 1 if x != '' else np.nan)
        self.dataframe_trim_bin.loc[:, self.cat_main] = self.dataframe_trim.loc[:, self.cat_main]
        self.dataframe_trim_bin.loc[:, self.cat_second] = self.dataframe_trim.loc[:, self.cat_second]

    def _get_map(self):
        # dataframe_trim_bin_inx = self.dataframe_trim_bin.copy()
        # dataframe_trim_bin_inx = dataframe_trim_bin_inx.set_index(self.cat_all)
        dataframe_map = self.dataframe_trim_bin.groupby(self.cat_all).sum()
        return(dataframe_map)

    def get_indicator(self,
            category = False, subcategory = False,
            keyword = False, inx = False, data = False,
            only_text = False, return_raw = False):
        """
        TODO write documentations
        """
        if isinstance(data, bool):
            data = self.dataframe_trim
        if isinstance(inx, bool):
            inx = self.INX
        if category:
            data = data.loc[data.loc[:, self.cat_main] == category]
        if subcategory:
            data = data.loc[data.loc[:, self.cat_second] == subcategory]
        text_data = [i for i in data.loc[:, inx].stack().tolist() if len(i) > 0]

        if keyword:
            text_data = [i for i in text_data if keyword in i]

        if only_text:
            text = '\n'.join(text_data)
            return(text)
        if return_raw:
            return(data)

        cat = list()
        subcat = list()
        for j in range(len(text_data)):
            cat_data = data.loc[
                [text_data[j] in data.loc[i, :].tolist() for i in data.index],
                self.cat_all].stack().tolist()
            cat.append(cat_data[0])
            subcat.append(cat_data[1])

        text_df = pd.DataFrame({'Category': cat, 'Subcategory': subcat, 'Indicator': text_data})
        text_df = text_df.set_index(['Category', 'Subcategory'])
        return(text_df)

    def get_subcategories(self,
            category = False,
            subcategory = False, keyword = False, inx = False,
            data = False):
        """
        TODO write documentations
        """
        if isinstance(data, bool):
            data = self.dataframe_trim_bin
        if isinstance(inx, bool):
            inx = self.INX
        if category:
            data = data.loc[data.loc[:, self.cat_main] == category]
        SC = [sc for sc in data.loc[:, self.cat_second]]
        SC = pd.Series(SC).unique()
        return(SC)

    def make_heatmap(self,
            category = False, subcategory = False, keyword = False, inx = False,
            data = False, use_bokeh = False, show_plot = False,
            h = 10, w = 20, name = "cat_", **kwargs):
        """
        TODO write documentations
        """
        # get defaults
        if 'cmap' not in kwargs:
            kwargs['cmap'] = 'Spectral_r'
        if 'cbar' not in kwargs:
            kwargs['cbar'] = False
        if 'annot' not in kwargs:
            kwargs['annot'] = True
        if 'square' not in kwargs:
            kwargs['square'] = True
        title = "Number of indicators"
        if isinstance(inx, bool):
            inx = self.INX
        if isinstance(data, bool):
            data = self.dataframe_trim_bin
        # select data
        if category:
            data = data.loc[data.loc[:, self.cat_main] == category]
            name += category
            title = "Number of indicators per category"
        if subcategory:
            data = data.loc[data.loc[:, self.cat_second] == subcategory]
            kwargs['mask'] = np.array(Image.open(path.join(d, self.mask_file)))
            title = "Number of indicators per sub-category"
        # group data
        if category:
            data = data.groupby([self.cat_second]).sum()
        else:
            data = data.groupby([self.cat_main]).sum()
        data = data.loc[:, inx]
        # make plot
        if use_bokeh:
            # make data relative
            data = data.div(data.sum())
            if category:
                bokeh_figure = _make_bokeh_hm(data, show_plot = show_plot, post_title = category)
            else:
                bokeh_figure = _make_bokeh_hm(data, show_plot = show_plot)
            return(bokeh_figure)
        else:
            # make data relative
            data = data.div(data.sum()).mul(100)
            data[data == 0] = np.nan
            fig, ax = plt.subplots(figsize=(w, h))
            sns.heatmap(data, ax = ax, **kwargs)
            data[data >= 1] = 1
            a = data.sum(axis=1).sort_values(ascending=False)[0:4]
            b = "\n".join(["{} ({})".format(a.index[e], int(i)) for e, i in enumerate(a)][0:3])
            ax.set_title("{} {}\n\n{}\n".format(title, category, b))
            fig.tight_layout()
            fig_path = "{}/heatmap_{}.png".format(self.figures_folder, name)
            plt.savefig(fig_path, dpi=300)
            return(fig_path)

    def _create_wc(self, data = False, **kwargs):
        if 'max_words' not in kwargs:
            kwargs['max_words'] = 2000
        if 'background_color' not in kwargs:
            kwargs['background_color'] = "white"
        if 'mask' not in kwargs:
            d = os.getcwd()
            print(d)
            mask_path = path.join(d, self.mask_file)
            print('using {} as mask'.format(mask_path))
            kwargs['mask'] = np.array(Image.open(mask_path))
        if isinstance(data, bool):
            data = self.dataframe_map_cat_rel

        stopwords = set(STOPWORDS)
        stopwords.add("per")
        stopwords.add("mean")
        stopwords.add("data")
        stopwords.add("rate")
        stopwords.add("total")
        stopwords.add("percentage")
        stopwords.add("average")
        stopwords.add("number")
        stopwords.add("row")
        stopwords.add("ratio")
        for i in data.index:
            stopwords.add(i)
            stopwords.add(i.lower())
            stopwords.add(i[0:-1])
            stopwords.add(i[0:-1].lower())
        for i in self.add_stopwords:
            stopwords.add(i)

        wc = WordCloud(stopwords=stopwords, **kwargs)
        return(wc)

    def make_tagcloud(self,
        category = False, subcategory = False, keyword = False,
        data = False, inx = False,
        h = 10, w = 10,
        name = "cat_"):
        """
        TODO write documentations
        """
        if isinstance(inx, bool):
            inx = self.INX
        if isinstance(data, bool):
            data = self.dataframe_trim
        # select data
        text = self.get_indicator(
            category = category, subcategory = subcategory, keyword = keyword,
            inx = inx, data = data, only_text = True)
        self.wc.generate(text)
        file_name = "{}/tagcloud_{}.png".format(self.figures_folder, name)
        self.wc.to_file(path.join(os.getcwd(), file_name))

        plt.subplots(figsize=(h, w))
        plt.imshow(self.wc, interpolation='bilinear')
        plt.axis("off")


def main():
    m = map()
    for cat in m.dataframe_trim_bin.loc[:, 'Category'].unique():
        m.make_heatmap(category = cat)
        m.make_tagcloud(category = cat)
        break

if __name__ == "__main__":
    main()
