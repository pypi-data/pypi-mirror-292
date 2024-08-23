##########################################################################
# Track Analyzer - Quantification and visualization of tracking data     #
# Authors: Arthur Michaut                                                #
# Copyright 2016-2019 Harvard Medical School and Brigham and             #
#                          Women's Hospital                              #
# Copyright 2019-2024 Institut Pasteur and CNRS–UMR3738                  #
# See the COPYRIGHT file for details                                     #
#                                                                        #
# This file is part of Track Analyzer package.                           #
#                                                                        #
# Track Analyzer is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# Track Analyzer is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the           #
# GNU General Public License for more details .                          #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with Track Analyzer (COPYING).                                   #
# If not, see <https://www.gnu.org/licenses/>.                           #
##########################################################################

import os
import os.path as osp
import csv

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import napari
from skimage import io
from skimage.color import rgb2gray
from skimage.util import img_as_ubyte
import tifffile as tifff

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from track_analyzer import plotting as tpl
from track_analyzer import calculate as tca

pd.options.mode.chained_assignment = None  # remove SettingWithCopyWarning

# Plotting parameters
color_list = [c['color'] for c in list(plt.rcParams['axes.prop_cycle'])] + sns.color_palette("Set1", n_colors=9,
                                                                                             desat=.5)
plot_param = {'figsize': (5, 5), 'dpi': 300, 'color_list': color_list, 'format': '.png', 'despine': True, 'logx': False,
              'logy': False, 'invert_yaxis': True, 'export_data_pts': False}


def paper_style():
    """
    Set some Seaborn plotting parameters
    :return:
    """
    mpl.rcParams.update(mpl.rcParamsDefault)  # ensure the default params are active
    sns.set_style("ticks")
    sns.set_context("paper", font_scale=2., rc={"lines.linewidth": 2, "lines.markersize": 9})


def get_cmap_color(value, colormap='plasma', vmin=None, vmax=None):
    """
    Get color corresponding to a value from a colormap. Optionally, give boundaries to colormap with vmin, vmax.
    :param value: value to be converted to color
    :type value: float or list or numpy.array
    :param colormap: Matplotlib colormap name
    :type colormap: str
    :param vmin: if not None, minimum value of colormap
    :type vmin: float or None
    :param vmax: if not None, maximum value of colormap
    :type vmax: float or None
    :return: color
    :rtype: tuple
    """

    colormap = plt.get_cmap(colormap)
    norm = plt.Normalize(vmin, vmax)
    return colormap(norm(value))


def get_cmap_lim(df,color_code,cmap_lim,dim):
    """
    Get cmap limits depending on color_code special cases and make sanity checks
    """

    # special cases
    if color_code in ['group','random','none']: 
        return None, color_code
    else:
        if color_code == 'z': 
            if dim != 3: 
                print("WARNING: z color-code cannot be used with 2D data, changing to random")
                return None, 'random'
        cmap_lim_default = [df[color_code].min(), df[color_code].max()]

    # use cmap_default value
    cmap_lim = cmap_lim_default
    # if cmap_lim is given in appropriate format (list or tuple of 2 elements, use is if not None)
    if type(cmap_lim) is list or type(cmap_lim) is tuple:
        if len(cmap_lim) == 2:
            for i,lim in enumerate(cmap_lim):
                if lim is None: 
                    cmap_lim[i] = cmap_lim_default[i]

    return cmap_lim, color_code


def listdir_nohidden(path):
    """
    List a directory without hidden files starting with a dot
    :param path: path to directory to list
    :type path: str
    :return: list of instances within a directory
    :rtype: list
    """
    if not osp.isdir(path):
        raise Exception('ERROR: {} is not a directory'.format(path))

    dir_list = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            dir_list.append(f)
    return dir_list


def safe_mkdir(path):
    """
    Make directory from only if it doesn't already exist
    :param path: path of directory to make
    :type path: str
    :return: path of directory
    :rtype: str
    """
    if not osp.isdir(path):
        os.mkdir(path)
    return path


def get_param_time_der(param):
    """
    Guess from a parameter name if it is a time derivative.
    If ends with _dot: first time derivative, if ends with _ddot: second time derivative
    :param param: parameters name
    :type param: str
    :return: raw parameter name (without derivative suffix) and type of derivative
    :rtype: str
    """
    if param.endswith('_dot'):
        return [param[:param.find('_dot')], 'first']
    elif param.endswith('_ddot'):
        return [param[:param.find('_ddot')], 'sec']
    else:
        return [param, None]


def make_unit_label(dimension='L', l_unit='um', t_unit='min'):
    """
    Make the Latex label of unit type depending on the dimension formula.
    Supported dimensions: L, LL, L/T, LL/T, L/TT, 1/L, 1/LL, T, 1/T
    Supported length units: um (for micrometers), s (for seconds), px (for pixels), au (for arbitrary unit)
    Supported time units: min (for minutes), mm (for millimeters), frame, au (for arbitrary unit)
    :param dimension: dimension using L and T for length and time dimensions
    :type dimension: str
    :param l_unit: length unit
    :type l_unit: str
    :param t_unit: time unit
    :type t_unit: str
    :return: label as a Latex formatted string
    :rtype: str
    """
    l_unit_dict = {'um': r'\mu m', 'mm': r'mm', 'm': r'm', 'px': 'px', 'none': '', 'au': ''}
    t_unit_dict = {'min': r'min', 's': r's', 'frame': 'frame', 'none': '', 'au': ''}

    if dimension == 'L':
        label = l_unit_dict[l_unit]
    elif dimension == 'LL':
        label = l_unit_dict[l_unit] + r'^2'
    elif dimension == 'LL/T':
        label = l_unit_dict[l_unit] + r'^2.' + t_unit_dict[t_unit] + r'^{-1}'
    elif dimension == 'L/TT':
        label = l_unit_dict[l_unit] + r'.' + t_unit_dict[t_unit] + r'^{-2}'
    elif dimension == 'L/T':
        label = l_unit_dict[l_unit] + r'.' + t_unit_dict[t_unit] + r'^{-1}'
    elif dimension == '1/L':
        label = l_unit_dict[l_unit] + r'^{-1}'
    elif dimension == '1/LL':
        label = l_unit_dict[l_unit] + r'^{-2}'
    elif dimension == 'T':
        label = t_unit_dict[t_unit]
    elif dimension == '1/T':
        label = t_unit_dict[t_unit] + r'^{-1}'
    elif dimension == 'none':
        label = ''
    else:
        print('Warning: this unit is not supported')
        label = r''

    return label


def make_param_label(param, l_unit='um', t_unit='min', time_der=None, mean=False, only_symbol=False, only_unit=False, manual_symbol=None, manual_unit=None):
    """
    Make a Latex formatted label of a parameter.
    The first and second time derivative and the mean symbol can be used.
    Supported parameters: x,y,z,x_scaled,y_scaled,z_scaled,z_rel,vx,vy,vz,v,ax,ay,az,a,area
    t,frame,D,curl,div,track_length,track
    Supported length units: um (for micrometers), s (for seconds), px (for pixels), au (for arbitrary unit)
    Supported time units: min (for minutes), mm (for millimeters), frame, au (for arbitrary unit)
    :param param: parameter
    :type param: str
    :param l_unit: length unit
    :type l_unit: str
    :param t_unit: time unit
    :type t_unit: str
    :param time_der: time derivative: 'first' or 'sec' or None
    :type time_der: str
    :param mean: mean parameter: add angle brackets as a sign for a mean parameter
    :type mean: str
    :param only_symbol: return only the parameter symbol
    :type only_symbol: bool
    :param only_unit: return only the parameter unit
    :type only_unit: bool
    :param manual_symbol: custom symbol to be used with param=None
    :type manual_symbol: str or None
    :param manual_unit: custom unit to be used with param=None
    :type manual_unit: str or None
    :return: parameter label: symbol and/or unit
    :rtype: str
    """

    # latex symbol
    symbol_dict = {'v': 'v', 'a': 'a', 'vx': 'v_x', 'vy': 'v_y', 'vz': 'v_z', 'ax': 'a_x', 'ay': 'a_y', 'az': 'a_z'}

    # a dict containing the features for each parameters (sym: symbol, dim: dimension, units, latex usage)
    param_dict = {}
    for p in list('xyz'):
        param_dict[p] = {'sym': p, 'dim': 'L', 'l_unit': 'px', 't_unit': 'none', 'latex': True}
    for p in ['x_scaled', 'y_scaled', 'z_scaled', 'z_rel']:
        param_dict[p] = {'sym': p[0], 'dim': 'L', 'l_unit': l_unit, 't_unit': 'none', 'latex': True}
    for p in ['vx', 'vy', 'vz', 'v']:
        param_dict[p] = {'sym': symbol_dict[p], 'dim': 'L/T', 'l_unit': l_unit, 't_unit': t_unit, 'latex': True}
    for p in ['ax', 'ay', 'az', 'a']:
        param_dict[p] = {'sym': symbol_dict[p], 'dim': 'L/TT', 'l_unit': l_unit, 't_unit': t_unit, 'latex': True}
    param_dict['t'] = {'sym': 't', 'dim': 'T', 'l_unit': 'none', 't_unit': t_unit, 'latex': True}
    param_dict['frame'] = {'sym': 'frame', 'dim': 'T', 'l_unit': 'none', 't_unit': 'none', 'latex': True}
    param_dict['D'] = {'sym': 'D', 'dim': 'LL/T', 'l_unit': l_unit, 't_unit': t_unit, 'latex': True}
    param_dict['div'] = {'sym': 'div', 'dim': '1/T', 'l_unit': l_unit, 't_unit': t_unit, 'latex': True}
    param_dict['curl'] = {'sym': 'curl', 'dim': '1/T', 'l_unit': l_unit, 't_unit': t_unit, 'latex': True}
    param_dict['track_length'] = {'sym': 'track duration', 'dim': 'T', 'l_unit': l_unit, 't_unit': t_unit,
                                  'latex': False}
    param_dict['track'] = {'sym': 'track id', 'dim': 'none', 'l_unit': l_unit, 't_unit': t_unit, 'latex': False}
    param_dict['area'] = {'sym': 'area', 'dim': 'LL', 'l_unit': l_unit, 't_unit': t_unit, 'latex': True}

    # output format
    if only_symbol and only_unit:
        print("Warning: only_symbol and only_unit can't be both True. Making them both False.")
        only_symbol = False
        only_unit = False

    # output label
    label = ''  
    if param is not None: 
        # check if mean
        if param.endswith('_mean'):
            param = param[:param.find('_mean')]
            mean = True

        # convert param if it ends by _dot or _ddot
        raw_param, time_der_ = get_param_time_der(param)
        if time_der_ is not None:
            time_der = time_der_
            param = raw_param

        # make symbol adding derivative or mean symbols
        symbol = param_dict[param]['sym']
        dim_der = ''
        if time_der == 'first':
            symbol = r'\dot{' + symbol + r'}'
            dim_der = '/T'  # change dimension
        elif time_der == 'sec':
            symbol = r'\ddot{' + symbol + r'}'
            dim_der = '/TT'  # change dimension
        if mean:
            symbol = r'\langle ' + symbol + r' \rangle'

        # make unit
        unit_ = make_unit_label(param_dict[param]['dim'] + dim_der, l_unit=param_dict[param]['l_unit'],
                                t_unit=param_dict[param]['t_unit'])

        # add latex dollar symbols if needed
        if param_dict[param]['latex']:
            if only_symbol:
                label = r'$' + symbol + r'$'
            elif only_unit:
                label = r'$' + unit_ + r'$'
            else:
                if len(unit_) > 0:  # if unit exists
                    label = r'$' + symbol + r'$ ($' + unit_ + r'$)'
                else:
                    label = r'$' + symbol + r'$'
        else:
            if only_symbol:
                label = symbol
            elif only_unit:
                label = unit_
            else:
                if len(unit_) > 0:  # if unit exists
                    label = symbol + ' (' + unit_ + ')'
                else:
                    label = symbol
    else: 
        no_symbol = False
        no_unit = False
        if manual_unit is None:
            no_unit = True 
        else:
            if len(manual_unit) == 0:
                no_unit = True
        if manual_symbol is None:
            no_symbol = True 
        else:
            if len(manual_symbol) == 0:
                no_symbol = True

        if only_symbol and not no_symbol:
            label = r'' + manual_symbol
        elif only_unit and not no_unit:
            label = r'' + manual_unit
        elif not only_symbol and not only_unit:
            if no_symbol and not no_unit:
                label = r'' + manual_unit
            elif not no_symbol and no_unit:
                label = r'' + manual_symbol
            elif not no_symbol and not no_unit: 
                label = r'' + manual_symbol + r' (' + manual_unit + r')'
            else:
                label = ''

    return label


def write_dict(dicts, filename, dict_names=None):
    """
    Write a dict or a list of dict into a csv file with keys in first column and values in the second column.
    Optional: if dicts is a list, a list of names for each dict can be given. There will be written in a separated
    row at the beginning of each dict
    :param dicts: a dict or a list of dict
    :type dicts: dict or list
    :param filename: filename of the csv file
    :type filename: str
    :param dict_names:
    :type dict_names: list
    """
    if type(dicts) is dict:
        dicts = [dicts]

    if type(dict_names) is list:
        if len(dicts) != len(dict_names):
            print("Warning: the name list doesn't match the dict list. Not printing names")
            dict_names = None

    with open(filename, "w+") as f:
        w = csv.writer(f)
        for i, d in enumerate(dicts):
            if type(d) is dict:
                if dict_names is not None:
                    f.write(dict_names[i] + '\n')
                for key, val in d.items():
                    w.writerow([key, val])
                f.write('\n')


def load_dict(filename):
    """
    Read a csv file and returns a dict, with csv first column as key and csv second column as values
    Try to convert to python objects if possible using the eval function
    :param filename: filename of the csv file
    :type filename: str
    :return: converted dict
    :rtype: dict
    """
    if not filename.endswith('.csv'):
        raise Exception("ERROR: No csv file passed. Aborting...")

    if not osp.exists(filename):
        raise Exception("ERROR: File does not exist. Aborting...")

    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        mydict = {}
        for rows in reader:
            if len(rows) > 0:
                if len(rows) == 2:
                    if rows[1] == '':
                        mydict[rows[0]] = None
                    else:
                        try:
                            mydict[rows[0]] = eval(rows[1])  # if needs conversion
                            try:
                                mydict[rows[0]] = eval(eval(rows[1]))  # if double string
                            except:
                                pass
                        except:
                            mydict[rows[0]] = rows[1]  # if string
                elif len(rows) > 2:  # if line splitted because of comma, try to concatenate line
                    val = ''
                    for i in range(1,len(rows)-1):
                        val += rows[i]+','
                    val += rows[len(rows)-1]

                    if val == '':
                        mydict[rows[0]] = None
                    else:
                        try:
                            mydict[rows[0]] = eval(val)  # if needs conversion
                            try:
                                mydict[rows[0]] = eval(eval(val))  # if double string
                            except:
                                pass
                        except:
                            mydict[rows[0]] = val  # if string
    return mydict


def make_grid(image_size, x_num=None, y_num=None, cell_size=None, scaled=False, lengthscale=1., origin=None,
              plot_grid=False, save_plot_fn=None):
    """
    Make a regular grid using numpy.meshgrid() over an image.
    Two grids are returned: a node_grid with the vertices of cells, and center_grid with the centers of the cells
    The meshsize can be defined by either the number of cells along one dimension (x or y), or the size of a cell
    (in px or scaled unit if scaled=True).
    If several definitions of meshsize are passed, by default the number of cells is used to ensure there is no
    conflict between definitions.
    If the grid does not cover the all image size it is cropped and centered (if origin is None) or tethered to one
    of 8 positions (left-bottom,center-bottom,etc.).
    :param image_size: image size (width,height) in px
    :type image_size: list or tuple
    :param x_num: number of cells along the x dimension
    :type x_num: int
    :param y_num: number of cells along the y dimension
    :type y_num: int
    :param cell_size: size of cell (in pixel or unit if scaled is True)
    :type cell_size: int or float
    :param scaled: cell size is scaled if True
    :type scaled: bool
    :param lengthscale: pixel size
    :type lengthscale: float
    :param origin: anchorage of the grid
    :type origin: str
    :param plot_grid: to plot an representation of the generated grid
    :type plot_grid: bool
    :param save_plot_fn: filename for plot
    :type save_plot_fn: str
    :return: node_grid of shape (n,m) depending on definition and center_grid of shape (n-1,m-1)
    :rtype: tuple
    """

    width, height = image_size

    # ensure there is no conflict by keeping only one definition (priority: x_num,y_num,cell_size)
    if [x_num, y_num, cell_size] == [None, None, None]:  # if no definition passed
        raise Exception("ERROR: cannot generate grids with no information. Aborting...")
    elif x_num is not None and y_num is not None and cell_size is not None:  # if three definitions, use x_num
        y_num = None
        cell_size = None
    elif x_num is not None and y_num is not None and cell_size is None:  # if x_num and y_num, use x_num
        y_num = None
    # if x_num or y_num and cell_size, use x_num or y_num
    elif [x_num, y_num] != [None, None] and cell_size is not None:
        cell_size = None

    # find definition available
    definition = None
    if x_num is not None and y_num is None and cell_size is None:
        definition = 'x_num'
    elif x_num is None and y_num is not None and cell_size is None:
        definition = 'y_num'
    elif x_num is None and y_num is None and cell_size is not None:
        definition = 'cell_size'
    else:
        raise Exception("ERROR: definition not found. Aborting...")

    # compute cell_size depending on the definition
    cell_size_ = 0
    if definition == 'x_num':
        x_num = int(x_num)
        if x_num < 1:
            raise Exception("ERROR: x_num needs to be at least 1. Aborting...")
        cell_size_ = float(width) / (x_num + 1)  # so x_num is the number of cells along the dimension
    elif definition == 'y_num':
        y_num = int(y_num)
        if y_num < 1:
            raise Exception("ERROR: y_num needs to be at least 1. Aborting...")
        cell_size_ = float(height) / (y_num + 1)  # so y_num is the number of cells along the dimension
    elif definition == 'cell_size':
        cell_size_ = cell_size if not scaled else cell_size / lengthscale
        if cell_size_ > width or cell_size_ > height:
            raise Exception("ERROR: cell size larger than image size. Aborting...")

    x_array = np.arange(0, width + cell_size_, cell_size_)
    x_array = x_array[x_array < width]
    y_array = np.arange(0, height + cell_size_, cell_size_)
    y_array = y_array[y_array < height]
    x_edge = width - x_array.max()
    y_edge = height - y_array.max()

    if origin is None or origin == 'center':  # center
        x_array = x_array + x_edge / 2
        y_array = y_array + y_edge / 2
    elif origin == "left-bottom":
        pass  # nothing to change
    elif origin == "center-bottom":
        x_array = x_array + x_edge / 2
    elif origin == "right-bottom":
        x_array = x_array + x_edge
    elif origin == "right-center":
        x_array = x_array + x_edge
        y_array = y_array + y_edge / 2
    elif origin == "right-top":
        x_array = x_array + x_edge
        y_array = y_array + y_edge
    elif origin == "center-top":
        x_array = x_array + x_edge / 2
        y_array = y_array + y_edge
    elif origin == "left-top":
        y_array = y_array + y_edge
    elif origin == "left-center":
        y_array = y_array + y_edge / 2

    x_center = x_array + cell_size_ / 2
    y_center = y_array + cell_size_ / 2

    node_grid = np.meshgrid(x_array, y_array)
    center_grid = np.meshgrid(x_center[:-1], y_center[:-1])

    if plot_grid:
        X, Y = node_grid
        x, y = center_grid
        fig, ax = plt.subplots(1, 1, figsize=plot_param['figsize'])
        ax.set_aspect('equal')
        for i in range(len(x_array)):
            plt.plot([X[0, i], X[-1, i]], [Y[0, i], Y[-1, i]], color_list[0])  # plot vertical lines
        for i in range(len(y_array)):
            plt.plot([X[i, 0], X[i, -1]], [Y[i, 0], Y[i, -1]], color_list[0])  # plot horizontal lines
        # plt.scatter(x, y, color=color_list[1])  # plot center of cells as dot
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        if save_plot_fn is not None:
            fig.tight_layout()
            fig.savefig(save_plot_fn, dpi=plot_param['dpi'])
            plt.close(fig)

    return node_grid, center_grid


def pool_datasets(df_list, name_list):
    """
    Concatenate together several dataframes with a column identifying the datasets' names
    :param df_list: list of DataFrames
    :type df_list: list
    :param name_list: names identifying each DataFrame
    :type name_list: list
    :return: DataFrame concatenating list of DataFrames
    :rtype: pandas.DataFrame
    """
    df_out = pd.DataFrame()

    for i, df in enumerate(df_list):
        if df is None:
            continue
        df['dataset'] = name_list[i]
        df_out = pd.concat([df_out, df], ignore_index=True)

    return df_out


def group_consecutives(vals, step=1):
    """
    Group together list of consecutive integer from a list of integer.
    :param vals: input list to be grouped
    :type vals: list
    :param step: expected gap between consecutive integer
    :type step: int
    :return: list of list (each being the consecutive integers)
    :rtype: list
    """
    run = []
    result = [run]
    expect = None
    for v in vals:
        if (v == expect) or (expect is None):
            run.append(v)
        else:
            run = [v]
            result.append(run)
        expect = v + step
    return result


def get_info(data_dir):
    """
    Get info about data given by a info.txt in the data directory.
    info.txt contains two mandatory info and several other optional ones.
    Each info is written on a line following the template: keyword : value
    Mandatory info: lengthscale in um/px and delta_t (frame intervalle) in min by default.
    Alternative units can be given by length_unit, time_unit.
    Other optional info:
    - table_unit: unit used in data table
    - separator: separator used in data table
    - image_width (in px)
    - image_height (in px)
    :param data_dir: path of the data directory
    :type data_dir: str
    :return: info in a dict
    :rtype: dict
    """
    filename = osp.join(data_dir, "info.txt")
    info = {}

    # list of parameters to grab
    string_list = ['length_unit', 'time_unit', 'table_unit', 'separator']
    int_list = ['image_width', 'image_height']
    float_list = ['lengthscale', 'timescale', 'z_step']

    if osp.exists(filename):
        # get parameters
        with open(filename) as f:
            for line in f:
                for param in string_list + int_list + float_list:
                    if param in line:
                        tokens = line.split(':')
                        if len(tokens) == 2:
                            if len(tokens[1].strip('\n')) > 0:
                                info[param] = tokens[1].strip('\n')
        # convert parameters
        for k in info.keys():
            if k in int_list:
                info[k] = int(info[k])
            elif k in float_list:
                info[k] = float(info[k])

    else:
        print("WARNING: info.txt doesn't exist or is not at the main data folder")
        return None

    mandatory_info = ['timescale', 'lengthscale']
    for mand_info in mandatory_info:
        if mand_info not in info.keys():
            print("ERROR: {} is not in info.txt".format(mand_info))
    return info


def get_data(data_dir, df=None, refresh=False, split_traj=False, set_origin_=False, image=None, reset_dim=['x', 'y'],
             invert_axes=[], custom_var={}, trackmate_input=False):
    """
    Main function to import data and perform the initial processing (scaling and computing of time derivatives).
    It saves the database as a pickle object.
    If the database already exists it just loads it from the pickle object if refresh is False.
    The data are either loaded from a file (positions.txt or positions.csv) or passed as pandas.DataFrame.
    Column names of df or the positions file must be: 'x','y',('z'),'frame','track'
    The coordinates origin and orientation can be reset with set_origin_ and invert_axes
    :param data_dir: path of the data directory
    :type data_dir: str
    :param df: raw positions Dataframe
    :type df: pandas.DataFrame or None
    :param refresh: refresh database
    :type refresh: bool
    :param split_traj: solve gaps in trajectories: interpolate missing data if False (default), or split in new tracks
    :type split_traj: bool
    :param set_origin_: to reset origin of coordinates with dict with dimensions as key and coordinates as values
    :param set_origin_: dict or None
    :param image: image dict returned by get_image()
    :type image: dict
    :param reset_dim: list of dimensions to reset, as set_origin_ contains coordinates along all dimensions
    :type reset_dim: list
    :param invert_axes: list of dimensions to invert (change sign)
    :type invert_axes: list
    :param custom_var: dict of custom variables: {'var_i':{'name':'var_name','unit':'var_unit'}}
    :type custom_var: dict
    :param trackmate_input: True if input file is a trackmate (v7) csv file
    :type trackmate_input: bool
    :return: dict with dataframe and key info
    :rtype: dict
    """
    # load existing database 
    pickle_fn = osp.join(data_dir, "data_base.p")

    if not osp.exists(pickle_fn) or refresh:  # compute database

        # get info
        info = get_info(data_dir)
        lengthscale = info["lengthscale"]
        timescale = info["timescale"]
        table_unit = 'px' if 'table_unit' not in info.keys() else info['table_unit']  # by default positions are in px
        z_step = None if 'z_step' not in info.keys() else info['z_step']
        if z_step == 0:
            z_step = None

        # if no dataframe is passed try to get it from a csv of txt file
        if df is None:
            data_file = osp.join(data_dir, 'positions.csv')
            sep = info["separator"] if "separator" in info.keys() else ','  # by default comma separated
            sep = '\t' if sep == 'tab' else sep
            if osp.exists(data_file):
                df = pd.read_csv(data_file, sep=sep)  # columns must be ['x','y','z','frame','track']
            else: 
                raise Exception("""data file does not exist, it must be named 'positions.csv' or 'positions.txt'""")

        # trackmate specific case
        if trackmate_input: 
            df = df[['POSITION_X','POSITION_Y','POSITION_Z','FRAME','TRACK_ID']]
            df.columns = ['x', 'y', 'z', 'frame', 'track']
            df = df.loc[3:]

        # check data type
        df = df.apply(pd.to_numeric, errors='ignore')
        dimensions = ['x', 'y', 'z'] if 'z' in df.columns else ['x', 'y']
        dim = len(dimensions)
        df['frame'] = df['frame'].astype(np.int64)
        for d in dimensions:
            df[d] = df[d].astype(np.float64)

        # rename track id and deal with gaps
        print("renaming tracks...")
        df = df[df['track'].notna()]  # remove Nan and None tracks
        df = tca.regularize_traj(df, dimensions, split_traj)

        # scale data
        print("applying length and time scales...")
        tca.scale_dim(df, dimensions=dimensions, timescale=timescale, lengthscale=lengthscale, z_step=z_step,
                      unit=table_unit, invert_axes=invert_axes)

        # compute velocities and accelerations
        print("computing velocities and accelerations...")
        tca.compute_vel_acc(df, dimensions=dimensions, timescale=timescale)

        # reset coordinates origin
        if set_origin_ is not False:
            if type(set_origin_) is dict:
                orig_coord_ = set_origin_
            else:
                orig_coord_ = None
            df, orig_coord = set_origin(df, image, reset_dim, lengthscale, orig_coord_)
            print("Successfully resetting origin of coordinates to: {}".format(orig_coord))

        if 'z' in dimensions:  # relative z: centered around mean
            df['z_rel'] = df['z_scaled'] - df['z_scaled'].mean()

        # update pickle
        data = {'df': df, 'lengthscale': lengthscale, 'timescale': timescale, 'dim': dim, 'dimensions': dimensions, 'custom_var':custom_var}
        pickle.dump(data, open(pickle_fn, "wb"))
    else:
        data = pickle.load(open(pickle_fn, "rb"))

    # extra check that df is numerci (in case of old pickle)
    df = data['df']
    df = df.apply(pd.to_numeric, errors='ignore')
    data['df'] = df

    return data


def get_traj(track_groups, track, min_frame=None, max_frame=None):
    """
    Get a single trajectory from its track id.
    A subset of the trajectory can be extracted by using min_frame and max_frame
    :param track_groups: output of a pandas.groupby()
    :type track_groups: pandas.DataFrameGroupBy
    :param track: track id
    :type track: int
    :param min_frame: minimal frame
    :type min_frame: int or None
    :param max_frame: maximal frame
    :type max_frame: int or None
    :return: dataframe of trajectory
    :rtype: pandas.DataFrame
    """
    group = track_groups.get_group(track)
    if min_frame is not None:
        group = group[group['frame'] >= min_frame]
    if max_frame is not None:
        group = group[group['frame'] <= max_frame]

    group.sort_values(by='t', inplace=True)  # ensure sorted by t
    return group.reset_index(drop=True)


def filter_by_traj_len(df, min_traj_len=1, max_traj_len=None):
    """
    Filter trajectories by their minimal and/or maximal length (in frames)
    :param df: dataframe of trajectories
    :type df: pandas.DataFrame
    :param min_traj_len: minimal trajectory length
    :type min_traj_len: int or None
    :param max_traj_len: maximal trajectory length
    :type max_traj_len: int or None
    :return: filtered dataframe of trajectories
    :rtype: pandas.DataFrame
    """

    # don't do anything if empty df
    if df.shape[0] == 0:
        return df

    if max_traj_len is None:  # assign the longest possible track
        max_traj_len = df['frame'].max() - df['frame'].min() + 1
    min_traj_len = 1 if min_traj_len is None else min_traj_len  # assign 1, if not given

    groups, group_values = get_unique_track_groups(df)
    df_list = []
    for group_value in group_values:
        track = groups.get_group(group_value)
        if (track.shape[0] >= min_traj_len) & (track.shape[0] <= max_traj_len):
            df_list.append(track)
    
    if len(df_list) > 0:
        out_df = pd.concat(df_list, ignore_index=True)
    else: 
        out_df = pd.DataFrame()  #return empty dataframe

    return out_df


def filter_by_frame_subset(df, frame_subset=None):
    """
    Filter trajectories by extracting a subset of frames
    :param df: dataframe of trajectories
    :type df: pandas.DataFrame
    :param frame_subset: frame boundaries of subset [minimal_frame,maximal_frame]
    :type frame_subset: list
    :return: filtered dataframe of trajectories
    :rtype: pandas.DataFrame
    """

    # don't do anything if empty df
    if df.shape[0] == 0:
        return df

    if frame_subset is None:
        return df
    elif frame_subset[0] is None and frame_subset[1] is None:
        return df
    elif frame_subset[0] is None or frame_subset[1] is None:
        if frame_subset[0] is not None:
            df_ = df[df['frame'] >= frame_subset[0]]
        elif frame_subset[1] is not None:
            df_ = df[df['frame'] <= frame_subset[1]]
    else:
        df_ = df[((df['frame'] >= frame_subset[0]) & (df['frame'] <= frame_subset[1]))]

    if df_.shape[0] == 0:
        print("WARNING: no data for this frame subset")
        #print("WARNING: no data for this frame subset. Returning unfiltered database")
        #return df
    return df_


def filter_by_region(df, xlim=None, ylim=None, zlim=None, polygon=None):
    """
    Filter data based on coordinates given in px. xy coordinates can be given by a rectangle (xlim,ylim) or a polygon.
    Rectangle selection is default
    :param df: dataframe of trajectories
    :type df: pandas.DataFrame
    :param xlim: [xmin,xmax]
    :type xlim: list or None
    :param ylim: [ymin,ymax]
    :type ylim: list or None
    :param zlim: [zmin,zmax]
    :type zlim: list or None
    :param polygon: polygon coordinates array(x_array,y_array)
    :type polygon: numpy.array or None
    :return: filtered dataframe of trajectories
    :rtype: pandas.DataFrame
    """

    # make rectangle selection default
    if (xlim is not None or ylim is not None) and polygon is not None: 
        polygon = None 

    # don't do anything if empty df
    if df.shape[0] == 0:
        return df

    df_ = df.copy()

    # filter by rectangle
    if xlim is not None or ylim is not None:
        df_ = filter_by_xyz(df_, xlim=xlim, ylim=ylim, zlim=zlim)

    # filter by polygon
    elif polygon is not None: 
        # first filter by xy extrema to speed up the process
        df_ = filter_by_xyz(df_, xlim=[polygon[:,0].min(),polygon[:,0].max()], ylim=[polygon[:,1].min(),polygon[:,1].max()], zlim=zlim)

        # then refine filtering
        poly_ = Polygon(polygon)
        data = []

        for ind in df_.index: 
            pt = Point(df_.loc[ind,['x','y']].values)
            if poly_.contains(pt):
                data.append(dict(zip(df_.columns,df_.loc[ind,:].values)))
        
        df_ = pd.DataFrame(data)
    
    # if all filters are None
    else: 
        pass

    return df_


def filter_by_xyz(df, xlim=None, ylim=None, zlim=None):
    """
    Extract data within a box given by xlim, ylim and zlim in px
    :param df: dataframe of trajectories
    :type df: pandas.DataFrame
    :param xlim: [xmin,xmax]
    :type xlim: list or None
    :param ylim: [ymin,ymax]
    :type ylim: list or None
    :param zlim: [zmin,zmax]
    :type zlim: list or None
    :return: filtered dataframe of trajectories
    :rtype: pandas.DataFrame
    """

    # don't do anything if empty df
    if df.shape[0] == 0:
        return df

    df_ = df.copy()

    dims = list('xyz')
    for i, lim_ in enumerate([xlim, ylim, zlim]):
        if lim_ is not None:
            if lim_[0] is None and lim_[1] is None:
                pass
            elif lim_[0] is None or lim_[1] is None:
                if lim_[0] is not None:
                    df_ = df_[df_[dims[i]] >= lim_[0]]
                elif lim_[1] is not None:
                    df_ = df_[df_[dims[i]] <= lim_[1]]
            else:
                df_ = df_[((df_[dims[i]] >= lim_[0]) & (df_[dims[i]] <= lim_[1]))]

    if df_.shape[0] == 0:
        print("WARNING: no data for this subset")
        #print("WARNING: no data for this subset. Returning unfiltered database")
        #return df
    return df_


def get_coordinates(image, df=None, verbose=True):
    """
    Interactive selection of coordinates on an image by hand-drawing using a Napari viewer.
    :param image: dict returned by get_image()
    :type image: dict
    :param df: pd.dataframe of tracks
    :type df: pandas.DataFrame
    :param verbose: verbosity
    :type verbose: bool
    :return: dict of list of selected shapes: {'points':[coordinates1,...],'rectangle':[coordinates1,...]}
    :rtype: dict
    """

    no_image = False
    
    if df is None and image is None: 
        raise Exception("No data nor image")
    
    # if no image plot tracks in viewer
    elif image is None: 
        no_image = True
    else: 
        if image["image_fn"] is None:
            no_image = True
        else: 
            if not osp.exists(image['image_fn']):
                print("Warning: {} does not exist".format(image['image_fn']))

    if no_image: 
        df = df.sort_values(by=['track', 'frame'])  # napari track layer requires data to be sorted by ID then frame
        if 'z' in df.columns:
            cols = ['frame', 'z', 'y', 'x'] 
            t_dim = 0
            z_dim = 1
        else:
            cols = ['frame', 'y', 'x']
            t_dim = 0
            z_dim = None
        tracks = df[['track'] + cols].values

    else: 
        image_fn = image['image_fn']
        t_dim = image['t_dim']
        z_dim = image['z_dim']
        im = io.imread(image_fn)

    # create list to store layers' data from an open Napari viewer
    shape_list = []
    points_list = []

    if no_image:
        viewer = napari.Viewer()
        viewer.add_tracks(tracks, name='trajectories')
    else: 
        viewer = napari.view_image(im)

    # print help message
    napari_message(viewer, "Draw points or rectangles, then press ENTER")

    # retrieve coodinates on clicking Enter
    @viewer.bind_key('Enter')
    def get_coord(viewer):
        for layer in viewer.layers:
            if type(layer) is napari.layers.shapes.shapes.Shapes:
                shape_list.append(layer)
            if type(layer) is napari.layers.points.points.Points:
                points_list.append(layer.data)
        viewer.close()

    if verbose:
        print("Draw points or rectangles, then press ENTER")

    napari.run()

    # inspect selected layers
    rectangle_list = []
    polygon_list = []
    if len(shape_list) > 0:
        for i, shape_type_ in enumerate(shape_list[0].shape_type):  # grab the first element to ignore if Enter is pressed several times
            if shape_type_ == 'rectangle':
                rectangle_list.append(shape_list[0].data[i])
            elif shape_type_ == 'polygon':
                polygon_list.append(shape_list[0].data[i])
    points = np.array([])
    if len(points_list) > 0:
        points = points_list[0]  # grab the first element to ignore if Enter is pressed several times
    
    if verbose:
        print('You have selected {} point(s), {} rectangle(s) and {} polygon(s)'.format(points.shape[0], len(rectangle_list), len(polygon_list)))

    # retreive coordinates
    coord_dict = {'points': [], 'rectangle': [], 'polygon': []}
    
    # get rectangle coordinates
    for rect in rectangle_list:
        # if 4D stack
        if t_dim is not None and z_dim is not None:
            frame = int(rect[0, t_dim])
            z = int(rect[0, z_dim])
            xmin, xmax = [rect[:, 3].min(), rect[:, 3].max()]
            ymin, ymax = [rect[:, 2].min(), rect[:, 2].max()]
        # if 3D (3rd dim being time or z)
        elif t_dim is not None or z_dim is not None:
            frame = int(rect[0, t_dim]) if t_dim is not None else None
            z = int(rect[0, z_dim]) if z_dim is not None else None
            xmin, xmax = [rect[:, 2].min(), rect[:, 2].max()]
            ymin, ymax = [rect[:, 1].min(), rect[:, 1].max()]
        # if 2D
        else:
            frame = None
            z = None
            xmin, xmax = [rect[:, 1].min(), rect[:, 1].max()]
            ymin, ymax = [rect[:, 0].min(), rect[:, 0].max()]

        coord_dict['rectangle'].append({'frame': frame, 'z': z, 'xlim': [xmin, xmax], 'ylim': [ymin, ymax]})

    # get polygon coordinates
    for poly in polygon_list:
        # if 4D stack
        if t_dim is not None and z_dim is not None:
            frame = int(poly[0, t_dim])
            z = int(poly[0, z_dim])
            x_array = poly[:, 3]
            y_array = poly[:, 2]
        # if 3D (3rd dim being time or z)
        elif t_dim is not None or z_dim is not None:
            frame = int(poly[0, t_dim]) if t_dim is not None else None
            z = int(poly[0, z_dim]) if z_dim is not None else None
            x_array = poly[:, 2]
            y_array = poly[:, 1]
        # if 2D
        else:
            frame = None
            z = None
            x_array = poly[:, 1]
            y_array = poly[:, 0]

        coord = np.array((x_array,y_array)).T  # column vectors of coordinates

        coord_dict['polygon'].append({'frame': frame, 'z': z, 'coord': coord})

    # get points coordinates
    for i in range(points.shape[0]):
        # if 4D stack
        if t_dim is not None and z_dim is not None:
            frame = int(points[i, t_dim])
            z = int(points[i, z_dim])
            x, y = [points[i, 3], points[i, 2]]
        # if 3D (3rd dim being time or z)
        elif t_dim is not None or z_dim is not None:
            frame = int(points[i, t_dim]) if t_dim is not None else None
            z = int(points[i, z_dim]) if z_dim is not None else None
            x, y = [points[i, 2], points[i, 1]]
        # if 2D
        else:
            frame = None
            z = None
            x, y = [points[i, 1], points[i, 0]]

        coord_dict['points'].append({'frame': frame, 'x': x, 'y': y, 'z': z})

    return coord_dict


def filter_by_traj_id(df, track_list=None):
    """
    Filter by trajectory id. Only one id can be given
    :param df: dataframe of trajectories
    :type df: pandas.DataFrame
    :param track_list: list of trajectory ids
    :type track_list: list or int or float or None
    :return: filtered dataframe of trajectories
    :rtype: pandas.DataFrame
    """

    # don't do anything if empty df
    if df.shape[0] == 0:
        return df

    if track_list is None:
        return df
    elif type(track_list) is float or type(track_list) is int:
        track_list = [track_list]

    tracks = df.groupby('track')
    df_list = []
    for track in track_list:
        df_list.append(get_traj(tracks, track))

    out_df = pd.concat(df_list, ignore_index=True)
    return out_df


def select_traj_by_xyzt(df, xlim=None, ylim=None, zlim=None, polygon=None, frame_lim=None):
    """
    Get ids of trajectories going through an xyzt box. The spatiotemporal box is defined its boundaries. 
    Alternativaly xy coordinates can be given by a polygon coordinates. 
    :param df: dataframe of trajectories
    :type df: pandas.DataFrame
    :param xlim: x boundaries
    :param xlim: list or None
    :param ylim: y boundaries
    :param ylim: list or None
    :param zlim: z boundaries
    :param zlim: list or None
    :param polygon: polygon coordinates
    :param polygon: numpy.array or None
    :param frame_lim: frame boundaries or unique frame
    :param frame_lim: int or list or None
    :return: list of trajectories id
    :rtype: list
    """

    # work on a copy
    df_ = df.copy()

    # filter by frame subset
    if type(frame_lim) is list or type(frame_lim) is tuple:
        df_ = filter_by_frame_subset(df_, frame_subset=frame_lim)
    elif type(frame_lim) is int or type(frame_lim) is float:
        df_ = df_[df_['frame'] == frame_lim]

    # filter by region
    df_ = filter_by_region(df_, xlim=xlim, ylim=ylim, zlim=zlim, polygon=polygon)

    # get ids
    track_list = df_['track'].unique()
    return track_list


def set_origin(df, image=None, reset_dim=['x', 'y'], lengthscale=1., orig_coord=None):
    """Set the origin of coordinates by selecting a point through a viewer. 
    Only some dimensions can be reset by reset_dim, the other are left unchanged.
    If no image is provided, the origin coordinates can be manually passed by orig_coord"""

    if orig_coord is None:
        # draw origin on image
        if image is not None:
            selection = get_coordinates(image,df)
            if len(selection['points']) != 1:
                raise Exception("ERROR: you need to select exactly one point to set the origin. Aborting...")

            origin = dict.fromkeys(reset_dim)

            for d in reset_dim:
                coord = selection['points'][0][d]
                if coord is not None:
                    coord *= lengthscale  # scale coordinate
                origin[d] = coord
        else:
            raise Exception("ERROR: no image nor origin coordinates provided. Aborting...")
    else:
        reset_dim = list(orig_coord.keys())
        origin = {d: orig_coord[d] * lengthscale for d in reset_dim}

    for d in reset_dim:
        if origin[d] is not None:
            df[d + '_scaled'] = df[d + '_scaled'] - origin[d]

    return df, origin


def select_sub_data(df, filters=[]):
    """
    Select subsets of data according a list of filters. Each element of the list will lead to a subset.
    Each subset is filtered by a dict:
    {'xlim','ylim','zlim','frame_subset','min_traj_len','max_traj_len','track_list','name'}
    :param df: dataframe of trajectories
    :type df: pandas.DataFrame
    :param filters: list of filters or single set of filters
    :type filters: list or dict or None
    :return: filtered dataframe of trajectories
    :rtype: pandas.DataFrame
    """

    # if no filter return input
    if filters is None:
        return df
    elif len(filters) == 0:
        return df

    # if only one set of filters
    if type(filters) is dict:  
        filters = [filters]

    # perform filtering
    df_list = []  # temp list of df 
    subset_names = []
    for i, filt in enumerate(filters):
        # filter
        df_ = filter_by_region(df, xlim=filt['xlim'], ylim=filt['ylim'], zlim=filt['zlim'], polygon=filt['ROI'])
        df_ = filter_by_frame_subset(df_, frame_subset=filt['frame_subset'])
        df_ = filter_by_traj_len(df_, min_traj_len=filt['min_traj_len'], max_traj_len=filt['max_traj_len'])
        df_ = filter_by_traj_id(df_, filt['track_list'])
        if filt['track_ROI'] is not None:
            track_list = select_traj_by_xyzt(df_,xlim=filt['track_ROI']['xlim'], ylim=filt['track_ROI']['ylim'], 
                                            zlim=filt['track_ROI']['zlim'], polygon=filt['track_ROI']['ROI'],
                                            frame_lim=filt['track_ROI']['frame_lim'])
            df_ = filter_by_traj_id(df_, track_list)

            # filter again by traj length because selected trajectories can be smaller
            df_ = filter_by_traj_len(df_, min_traj_len=filt['min_traj_len'], max_traj_len=filt['max_traj_len'])

        if len(filters) > 1:  # populate subset_names only if there are several subset
            subset_name = filt['name'] if filt['name'] != '' else 'subset_{}'.format(i)  # subset name

            # remove empty df_
            if df_.shape[0] > 0:  
                df_['subset'] = subset_name
                subset_names.append(subset_name)
            else: 
                print("WARNING: subset {} has no data: Removing this subset... ".format(subset_name))
        
        if df_.shape[0] > 0:
            df_list.append(df_)

    #check that subset name is not repeated
    if len(subset_names) != len(set(subset_names)):
        print("WARNING: some subset names are used several times")

    if len(df_list) > 0:
        out_df = pd.concat(df_list, ignore_index=True)
        return out_df
    else: 
        raise Exception("WARNING: all datasets are empty. Aborting...")


def get_background(image=None, frame=None, df=None, no_bkg=False, image_size=None, orig=None, axis_on=False,
                   dpi=plot_param['dpi'], figsize=(5, 5), figsize_factor=1):
    """Get image background or create white background if no_bkg. The image can be a time nd stack or a single image."""
    if orig is None:
        # orig = 'lower' if image_dir is None else 'upper' #trick to plot for the first time only inverting Yaxis: not very elegant...
        orig = 'lower'

    if image is None:
        no_bkg = True
    else:
        if image['image_fn'] is None:
            no_bkg = True

    if no_bkg:
        if image_size is not None:
            xmin, xmax, ymin, ymax = [0, image_size[0], 0, image_size[1]]
            figsize = ((xmax - xmin) / dpi, (ymax - ymin) / dpi)
        else:
            if df is None:
                print("WARNING: no image nor data provided")
                figsize = figsize
            else:
                # define image size as slightly larger than the data range
                xmin = df['x'].min() - 0.05 * (df['x'].max() - df['x'].min())
                xmax = df['x'].max() + 0.05 * (df['x'].max() - df['x'].min())
                ymin = df['y'].min() - 0.05 * (df['y'].max() - df['y'].min())
                ymax = df['y'].max() + 0.05 * (df['y'].max() - df['y'].min())
                figsize = ((xmax - xmin) / dpi, (ymax - ymin) / dpi)

        fig = plt.figure(frameon=False, figsize=figsize, dpi=dpi*figsize_factor)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_aspect('equal')

    else:
        # extract frame if image is nd stack
        z_dim = image['z_dim']
        t_dim = image['t_dim']
        image_fn = image['image_fn']
        if z_dim is not None:  # if z stack, make a max_proj
            fn, file_ext = osp.splitext(image_fn)
            image_fn_ = fn + '_maxproj.tif'
            if not osp.exists(image_fn_):
                tpl.stack_max_proj(image_fn, z_dim, t_dim)
            image_fn = image_fn_
        im = io.imread(image_fn)
        if t_dim is not None:
            im = im[frame]

        im = img_as_ubyte(im)  # 8bit conversion
        n = im.shape[0]
        m = im.shape[1]
        fig = plt.figure(frameon=False, figsize=(m / dpi, n / dpi), dpi=dpi*figsize_factor)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(im, aspect='equal', origin=orig, cmap='gray', vmin=0, vmax=255)
        xmin, xmax, ymin, ymax = ax.axis()

    if axis_on:
        ax.axis('on')
    else:
        ax.axis('off')

    return {'fig': fig, 'ax': ax, 'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax, 'no_bkg': no_bkg}


def get_image(data_dir, filename=None, verbose=False):
    """
    Get a multidimensional image in data directory and analyzes its dimensions.
    Convert it to 8bit grayscale if RGB after saving the original image.
    :param data_dir: path to data directory
    :type data_dir: str
    :param filename: custom filaneme if None replace by stack.tif
    :type filename: str or None
    :param verbose: print the dimension analysis
    :type verbose: bool
    :return: dict with image path, dimensions (t_dim, z_dim: indices of the t and z dimensions),
    image size [height, width] in px
    :rtype: dict
    """

    filename = osp.join(data_dir, 'stack.tif') if filename is None else filename

    if osp.exists(filename):
        im = io.imread(filename)

        # convert RGB image to grayscale
        if im.shape[-1] == 3:
            print("WARNING! RGB image, converting to grayscale")
            # change name RGB file
            dir_, fn = osp.split(filename)
            new_fn = osp.splitext(fn)[0] + '_RGB.tif'
            tifff.imsave(osp.join(dir_, new_fn), im)

            # convert to grayscale
            im = rgb2gray(im)
            im = img_as_ubyte(im)  # 8bit conversion
            tifff.imsave(filename, im)

        # analyze image dimensions
        image_dim = len(im.shape)
        z_dim, t_dim = [None, None]  # pos
        if image_dim == 2:
            y_size, x_size = im.shape
            z_dim, t_dim = [None, None]  # axes of z and t data
            if verbose:
                print("You have loaded a {}D image: ({}x{}) pixels".format(image_dim, x_size, y_size))
        elif image_dim == 3:
            t_size, y_size, x_size = im.shape
            z_dim, t_dim = [None, 0]  # axes of z and t data
            if verbose:
                print("You have loaded a {}D image: "
                      "({}x{}) pixels with {} time steps".format(image_dim, x_size, y_size, t_size))
        elif image_dim == 4:
            t_size, z_size, y_size, x_size = im.shape
            z_dim, t_dim = [1, 0]  # axes of z and t data
            if verbose:
                print("You have loaded a {}D image: ({}x{}) pixels with {} time steps "
                      "and {} z slices".format(image_dim, x_size, y_size, t_size, z_size))

        image_dict = {'image_fn': filename, 't_dim': t_dim, 'z_dim': z_dim, 'image_size': im.shape[-2:]}
    else:
        # get image size
        info = get_info(data_dir)

        if info is None:
            print("WARNING: no info.txt file so image size will be inferred")
            image_size = None
        else: 
            if 'image_width' in info.keys() and 'image_height' in info.keys():
                if info['image_width'] is not None and info['image_height'] is not None:
                    image_size = (info['image_height'],info['image_width'])
            else: 
                image_size = None
                print("WARNING: no image in directory, and image size is not defined in info.txt")

        image_dict = {'image_fn': None, 't_dim': None, 'z_dim': None, 'image_size': image_size}

    return image_dict


def load_config(data_dir, verbose=False):
    """ Import all existing config from the config directory. Each csv file is loaded in a dict """

    config_dir = osp.join(data_dir, 'config')

    out_dict = {}

    if osp.exists(config_dir):
        if osp.isdir(config_dir):
            for f in listdir_nohidden(config_dir):
                if f.endswith('.csv'):
                    out_dict[f[:-4]] = load_dict(osp.join(config_dir, f))
        else:
            print("WARNING: config is not a directory. Config not loaded.")
    else:
        print("WARNING: no config directory. Config not loaded.")

    return out_dict


def make_map_config(data_dir=None, export_config=True, empty_run=True):
    """
    Generate a list of dictionaries containing the parameters used to run map_analysis.
    empty_run allows not to use the default parameters to analyze and to skip the analysis
    """

    # config to create grid using prepare.make_grid()
    grid_param = {'x_num': 10,  # number of cells along x axis
                  'y_num': None,  # number of cells along y axis
                  'cell_size': None,  # size of a cell (=a square) in px or in unit if scaled is True
                  'scaled': False,  # boolean to use scaled length of cell_size
                  'origin': None,  # position of the grid (that is smaller or equal to image size)
                  'plot_grid': False,  # boolean to plot a representation of the grid
                  }

    # general config for plotting maps 
    map_param = {'no_bkg': False,  # boolean to remove background picture
                 'size_factor': 1.,  # size factor to tune relative size of arrows on vector plots
                 'show_axis': False,  # boolean to show plot axes
                 'export_field': False,  # export field points to txt files
                 'temporal_average': 0,  # number of frame to average map values over
                 'cmap': "plasma",  # color map for scalar fields
                 'increment': 1,  # increment to plot frames 
                 }

    # config of scalar field to plot. Each key is a parameter to plot and it stores a dict containing the plotting config for this specific parameter
    scalar_fields = {'vx': {'vlim': None,  # value limits to display on the color map
                            'cmap': "plasma"  # color map
                            },
                    'vy': {'vlim': None,  # value limits to display on the color map
                            'cmap': "plasma"  # color map
                            },
                    'v': {'vlim': None,  # value limits to display on the color map
                            'cmap': "plasma"  # color map
                            }
                     }

    # config of vector field to plot. Each key is a parameter to plot and it stores a dict containing the plotting config for this specific parameter
    vector_fields = {'v': {'vlim': None,  # value limits to display on the color map
                           'plot_on': 'v',  # parameter of the scalar map to plot on. If None, don't plot on scalar map
                           'cmap': "plasma"  # color map
                           }
                     }

    # config of vector average. Each key is a parameter to plot and it stores a dict containing the plotting config for this specific parameter
    vector_mean = {'v_mean': {'vlim': None,  # value limits to display on the color map
                              'dimensions': ['x', 'y', 'z'],  # dimension to compute the average on
                              'cmap': "plasma"  # color map
                              }
                   }

    if empty_run: 
        # erase analysis config
        scalar_fields = {}
        vector_fields = {}
        vector_mean = {}

    # package all in a dict
    config = {'grid_param': grid_param,
              'map_param': map_param,
              'scalar_fields': scalar_fields,
              'vector_fields': vector_fields,
              'vector_mean': vector_mean,
              }

    if export_config:
        if data_dir is None:
            raise Exception("ERROR: no data_dir given")
        else:
            config_dir = osp.join(data_dir, 'config')
            safe_mkdir(config_dir)

            for key in config.keys():
                fn = osp.join(config_dir, key + '.csv')
                write_dict(config[key], fn)

    return config


def make_traj_config(data_dir=None, export_config=True):
    """
    Generate a list of dictionaries containing the parameters used to run traj_analysis.
    """

    traj_config_ = {'run': True,  # run plot_traj
                    'color_code': 'z',  # color code: 'z', 'group', 'random', 'none'
                    'cmap': 'plasma',  # colormap to be used if color_code is 'z'
                    'cmap_lim': None,
                    # pass custom colormap limits (useful for getting coherent boundaries for all frames)
                    'show_tail': True,  # show trajectory tail
                    'hide_labels': True,  # hide trajectory ID
                    'lab_size': 6,  # label size in points if hide_labels is False
                    'no_bkg': False,  # don't show background image if an image is passed
                    'size_factor': 1.,  # to multiply the default size of markers and lines
                    'show_axis': False,  # to show the plot axes (by default just image)
                    'plot3D': False,  # plot in 3D  !! Not supportes anymore !!
                    'elevation': None,  # 3D paramater !! Not supportes anymore !!
                    'angle': None,  # 3D paramater !! Not supportes anymore !!
                    'subset_order': None,  # if color_code is group, order of group in color cycle
                    'increment': 1,  # increment to plot frames 
                    }

    MSD_config = {'run': True,  # run plot_all_MSD
                  'MSD_model': "biased_diff",  # fitting model: 'PRW', 'biased_diff', "pure_diff", None (if not fitting)
                  'dim': 2,  # dimension to compute MSD (doesn't have to match the data dimensions)
                  'fitrange': None,  # fitrange list boundaries of the fit: [low_bound,high_bound]. If a bound is
                  # None, the extremum is taken
                  'plot_all_MSD': True,  # plot MSD altogether
                  'plot_single_MSD': False,  # plot MSD individually
                  'logplot_x': True,  # plot in log along x axis
                  'logplot_y': True,  # plot in log along y axis
                  'alpha': 0.2  # transparency of individual plots when all plotted together
                  }

    scatter_config = {'run': True,  # run param_vs_param
                      'couple_list': [['x', 'v'], ['y', 'v']],  # list of [x,y] couples of variables to be plotted in scatter
                      'hue_var_list': [None,None],  # list of variables used for hue
                      'hue_cmap_list': [None,None], # list of colormaps used for hue
                      'mean_couple_list': [['x', 'v'], ['y', 'v']],  # list of [x,y] couples of variables averaged along the whole track to be plotted in scatter
                      'mean_hue_var_list': [None,None],  # list of variables used for hue
                      'mean_hue_cmap_list': [None,None], # list of colormaps used for hue
                      'x_bin_num': None,  #  number of evenly spaced bins along x axis
                      'ci': None,  # show confidence interval [0,100]
                      'fit_reg': False,  # show regression fit
                      'scatter': True,  # show scatter 
                      }

    hist_config = {'run': True,  # run plot_param_hist
                   'var_list': ['v'],  # list of variables to be plotted in histogram
                   'mean_var_list': ['v']  # list of variables averaged along the whole track to be plotted in histogram
                   }

    boxplot_config = {'run': True,  # run plot_param_hist
                       'var_list': ['v'],  # list of variables to be plotted 
                       'hue_var_list': [None],  # list of variables used for hue in swarmplots
                       'hue_cmap_list': [None], # list of colormaps used for hue in swarmplots
                       'save_stat': True ,  # run statistical test (scipy.stats.ttest_ind(equal_var=False))
                       'boxplot': True,  # show boxplot for variables in var_list
                       'swarmplot': False,  # show swarmplot for variables in var_list
                       'mean_var_list': ['v'],  # list of variables averaged along the whole track to be plotted
                       'mean_hue_var_list': [None],  # list of mean variables used for hue in swarmplots
                       'mean_hue_cmap_list': [None], # list of colormaps used for hue in swarmplots
                       'mean_boxplot': True,  # show boxplot for variables in mean_var_list
                       'mean_swarmplot': True,  # show swarmplot for variables in mean_var_list
                       'mean_save_stat': True ,  # run statistical test (scipy.stats.ttest_ind(equal_var=False)) for wholetrack parameters
                       }

    total_traj_config = {'run': True,  # run plot_centered_traj
                         'hide_labels': True,  # hide trajectory ID
                         'label_size': 5,  # label size in points if hide_labels is False
                         'center_origin': True,  # to center origin of all trajectories
                         'set_axis_lim': None,  # custom axis limites: [xmin,xmax,ymin,ymax]
                         'equal_axis': True,  # set x and y axes' scaling equal
                         'color_code': 'random',  # color code: 'z', 'group', 'random', 'none'
                         'cmap': 'plasma',  # colormap to be used if color_code is 'z'
                         'cmap_lim': None,  # pass custom colormap limits
                         'subset_order': None,  # if color_code is group, order of group in color cycle
                         'transparency': 1,  #plot transparency
                         'show_legend': True  # show legend
                         }

    # config of voronoi plot
    voronoi = {'run': True,  # run analysis
                'plot': True,  # plot diagram
                'vlim': None,  # value limits to display on the color map
                'cmap': "plasma",  # color map
                'compute_local_area': True,  # compute voronoi cell area
                'show_local_area': True,  # show voronoi cell area
                'area_threshold': 3,  # exclude areas above this multiple of area median
                'no_bkg': False,  # don't show background image if an image is passed
                'size_factor': 1.,  # to multiply the default size of lines !! Not implemented yet !!
                'show_axis': False,  # to show the plot axes (by default just image)
                'line_width': 1.,  # diagram line width
                'increment': 1,  # increment to plot frames 
               }

    # package all in a dict
    config = {'traj_config_': traj_config_,
              'MSD_config': MSD_config,
              'scatter_config': scatter_config,
              'hist_config': hist_config,
              'total_traj_config': total_traj_config,
              'voronoi_config': voronoi,
              'boxplot_config': boxplot_config,
              }

    if export_config:
        if data_dir is None:
            raise Exception("ERROR: no data_dir given")
        else:
            config_dir = osp.join(data_dir, 'config')
            safe_mkdir(config_dir)

            for key in config.keys():
                fn = osp.join(config_dir, key + '.csv')
                write_dict(config[key], fn)

    return config


def make_data_config(data_dir=None, export_config=True):
    """
    Initialize parameters used by get_data
    :param data_dir: path to data directory
    :type data_dir: str or None
    :param export_config: to export to config file
    :type export_config: bool
    :return: filters used by select_sub_data()
    :rtype: dict
    """

    config = {'split_traj': False,  # solve gaps in trajectories: interpolate missing data if False or split in new tracks
              'set_origin_': False,  # to reset origin of coordinates with dict with dimensions as key and coordinates as values
              'reset_dim': ['x', 'y'],  # list of dimensions to reset, as set_origin_ contains coordinates along all dimensions
              'invert_axes': [],  # list of dimensions to invert (change sign)
              'trackmate_input': False,  # if the input file is a trackmate (v7) csv file
             }

    if export_config: 
        if data_dir is None:
            raise Exception("ERROR: no data_dir given")
        else:
            config_dir = osp.join(data_dir, 'config')
            safe_mkdir(config_dir)
        fn = osp.join(config_dir, 'data_config.csv')
        write_dict(config, fn)

    return config


def init_filters(data_dir=None, export_config=False):
    """
    Initialize database filters
    :param data_dir: path to data directory
    :type data_dir: str or None
    :param export_config: to export to config file
    :type export_config: bool
    :return: filters used by select_sub_data()
    :rtype: dict
    """
    # filters for a single subset
    subset_dict = {'xlim': None,  # x boundaries
                   'ylim': None,  # y boundaries
                   'zlim': None,  # z boundaries
                   'ROI': None,  # polygon coordinates of selected region
                   'min_traj_len': None,  # minimum trajectory length
                   'max_traj_len': None,  # maximum trajectory length
                   'frame_subset': None,  # frame boundaries
                   'track_list': None,  # a list of trajectories ids
                   'track_ROI': None,  # a dict: {'xlim','ylim','zlim','frame_lim'}
                   'name': ''  # custom name to identify the subset
                   }

    filters = {'subset': 'separately',  # analyzed subsets separately or together, options: 'separately','together' 
                'filters_list': [subset_dict],  # list of subsets filters
                'subset_order': None,  # to give a custom order from plotting subset together
                }

    if export_config: 
        if data_dir is None:
            raise Exception("ERROR: no data_dir given")
        else:
            config_dir = osp.join(data_dir, 'config')
            safe_mkdir(config_dir)
        fn = osp.join(config_dir, 'filters.csv')
        write_dict(filters, fn)

    return filters


def make_all_config(data_dir=None, export_config=True):
    """
    Generate all default config dict and export them to csv. 
    """

    data_config = make_data_config(data_dir=data_dir, export_config=export_config)
    filters = init_filters(data_dir=data_dir, export_config=export_config)
    traj_config = make_traj_config(data_dir=data_dir, export_config=export_config)
    map_config = make_map_config(data_dir=data_dir, export_config=export_config)
    plot_config = tpl.make_plot_config(data_dir=data_dir, export_config=export_config)

    all_config = {"data_config": data_config,
                    "filters": filters,
                    "traj_config": traj_config,
                    "map_config": map_config,
                    "plot_config": plot_config,
                    }
    return all_config


def get_unique_track_groups(df):
    """
    Split a df in track groups making sure they are unique tracks (splitting by subsets too if exist)
    Return pandas groups and the values to get them
    """
    if 'subset' in df.columns: 
        groups = df.groupby(by=['subset','track'])
        df_ = df.drop_duplicates(subset=['subset','track']) # get only unique tracks
        group_values_arr = df_[['subset','track']].values
        
        # transform group_values_arr to a list of tuple
        group_values = []
        for i in range(group_values_arr.shape[0]):
            group_values.append((group_values_arr[i,0],group_values_arr[i,1]))

    else: 
        groups = df.groupby(by='track')
        group_values = df['track'].unique()

    return groups, group_values


def napari_message(viewer,text): 
    """
    Print a message in napari viewer
    """
    viewer.text_overlay.text = text
    viewer.text_overlay.visible = True
    viewer.text_overlay.font_size = 12
    viewer.text_overlay.color = "white"
    viewer.text_overlay.opacity = 1