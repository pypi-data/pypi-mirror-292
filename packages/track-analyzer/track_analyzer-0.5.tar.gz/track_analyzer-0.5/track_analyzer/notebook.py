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
from skimage import io
from skimage.color import rgb2gray
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import warnings

from ipyfilechooser import FileChooser
import ipywidgets as widgets
from ipywidgets import HBox, VBox, GridspecLayout, Label, AppLayout, Layout
from IPython.display import Markdown, display
from traitlets import traitlets

from track_analyzer import prepare as tpr
from track_analyzer import plotting as tpl
from track_analyzer.scripts.analyze_tracks import traj_analysis
from track_analyzer.scripts.analyze_maps import map_analysis
from track_analyzer.scripts.compare_datasets import compare_datasets

from napari.settings import get_settings
get_settings().application.ipy_interactive = False  # disable interactive usage of Napari viewer (necessary for tpr.get_coordinates)

warnings.filterwarnings('ignore')

cwd = os.getcwd()  # working directory
plot_param = tpl.make_plot_config()  # some config parameters
color_list = plot_param['color_list']  # a list of colors often used

# Custom widgets
class LoadedButton(widgets.Button):
    """A button that can holds a value as a attribute."""

    def __init__(self, value=None, *args, **kwargs):
        super(LoadedButton, self).__init__(*args, **kwargs)
        # Create the value attribute.
        self.add_traits(value=traitlets.Any(value))

# Notebook functions
def printmd(string):
    display(Markdown(string))

def analyze_image(data_dir,filename=None,verbose=False):
    """Analyze an image dimensions and return its properties"""
    # analyze image
    y_size,x_size = [512,512] # default size of an image to inialize the make info widget 
    image = tpr.get_image(data_dir,filename=filename,verbose=True)
    if image['image_size'] is not None:
        y_size,x_size = image['image_size']

    # swap z and t dimensions if needed 
    check_swap_wid = False  # bool to retrieve swap_wid value if necessary
    if image['t_dim'] is not None and image['z_dim'] is not None:
        check_swap_wid = True
        printmd("If there is an error between t and z dimension, you can swap these dimensions")
        swap_wid = widgets.ToggleButton(value=False,description='Swap z and t') 
        display(swap_wid)
    else:
        swap_wid = None

    return image,y_size,x_size,check_swap_wid,swap_wid

def make_info_widget(data_dir,y_size,x_size,trackmate_data=True):
    """Make widgets to get information about the data"""
    length_unit_wid=widgets.Dropdown(options=['um', 'mm', 'au'],value='um',description='Length unit:',style={'description_width': 'initial'})
    time_unit_wid=widgets.Dropdown(options=['min', 's', 'hr', 'au'],value='min',description='Time unit:',style={'description_width': 'initial'})
    length_sc_wid=widgets.BoundedFloatText(value=1.0,min=0,max=1e4,description='Pixel size:',style={'description_width': 'initial'})
    z_sc_wid=widgets.BoundedFloatText(value=0,min=0,max=1e4,description='z step:',style={'description_width': 'initial'})
    time_sc_wid=widgets.BoundedFloatText(value=1.0,min=0,max=1e4,description='Frame interval:',style={'description_width': 'initial'})    
    width_wid=widgets.BoundedIntText(value=x_size,min=0,max=1e4,description='Image width (px):',style={'description_width': 'initial'})
    height_wid=widgets.BoundedIntText(value=y_size,min=0,max=1e4,description='Image height (px):',style={'description_width': 'initial'})
    
    left_box = VBox([length_unit_wid, time_unit_wid,width_wid])
    right_box = VBox([length_sc_wid, time_sc_wid,height_wid])
    box = HBox([left_box, right_box])
    printmd("**Information about the data**")
    display(box)
    printmd("In the data table, are the positions given in pixels or in the length unit (given above)?")
    default_unit = 'unit' if trackmate_data else 'px'
    table_unit_wid=widgets.Dropdown(options=['px', 'unit'],value=default_unit,description='Data unit:',style={'description_width': 'initial'})
    display(table_unit_wid)
    printmd("If the lengthscale in z is different from the xy lengthscale, enter the z step (in length unit). If not, leave it to zero.")
    display(z_sc_wid)
    
    wid_list = [length_unit_wid,time_unit_wid,length_sc_wid,time_sc_wid,width_wid,height_wid,table_unit_wid,z_sc_wid]
    param_names = ['length_unit','time_unit','lengthscale','timescale','image_width','image_height','table_unit','z_step']

    return wid_list,param_names

def make_database_widget(data_file,sep_wid, header_wid, trackmate_data=True):
    """Make widgets to organize the database"""
    col_wid_list = []
    left_list=[]
    right_list=[]
    param_list = ['discard','x','y','z','frame','track']
    var_list = []
    var_wid_dict = {}
    default_trackmate = {'POSITION_X':'x',
                        'POSITION_Y':'y',
                        'POSITION_Z':'z',
                        'FRAME':'frame',
                        'TRACK_ID':'track',
                        }
    # load data file
    sep = sep_wid.value if sep_wid.value !='tab' else '\t'
    header = 0 if header_wid.value else None
    df = pd.read_csv(data_file,sep=sep,header=header)
    if trackmate_data:
        df = df.loc[3:]  # the 3 first rows in trackmate files are metadata
    
    printmd("**Here are the first rows of the input data table**")
    display(df.head(10))
    
    # get all the potential variables in addition to x,y,z,frame,track
    custom_var_num = df.shape[1] - 5 # number of columns apart from 'x','y','z','frame','track'
    for i in range(custom_var_num): 
        param_list.append('var_{}'.format(i+1))
        var_list.append('var_{}'.format(i+1))
    
    # display the df columns as two columns of widgets
    for i,col in enumerate(df.columns):
        if trackmate_data:
            default_val = default_trackmate[col] if col in default_trackmate.keys() else 'discard'
        else: 
            default_val = 'discard'
        wid = widgets.Dropdown(options=param_list,value=default_val,
                               description='column {}:'.format(col),
                               style={'description_width': 'initial'})
        col_wid_list.append(wid)
        if i<len(df.columns)/2:
            left_list.append(wid)
        else: 
            right_list.append(wid)
    
    printmd("""**Select the columns to be used in the analysis: track,frame,x,y,(z). 
            Leave to "discard" the other ones. If you want to use custom variables, use var_i.**""")
    printmd("""**If your input file is a trackmate file, mandatory columns are selected by default.**""")
    
    left_box = VBox(left_list)
    right_box = VBox(right_list)
    display(HBox([left_box, right_box]))
    
    # get the custom variable name and unit
    HBox_list = []
    for var in var_list: 
        wid_name = widgets.Text(value='',placeholder='Variable name')
        wid_unit = widgets.Text(value='',placeholder='Variable unit')
        HBox_list.append(HBox([Label(var+':'),wid_name,wid_unit]))
        var_wid_dict[var] = {'name': wid_name, 'unit': wid_unit}
    
    printmd("""**If you selected some custom variables, give their name and unit to be displayed on plots. 
    You can use Latex, if necessary.**""")
    display(VBox(HBox_list))
    
    # deal with gaps in trajectories
    printmd("""**Some tracking softwares support to miss objects at some frames. This results in tracks with gaps.
            However, this analysis pipeline requires to have continuous tracks. How do you want to handle tracks with gaps:
            fill the gaps by linear interpolation or split the track in different tracks?**""")
    split_wid=widgets.Dropdown(options=['interpolate','split'],value='interpolate',description='gap resolution:'.format(col),style={'description_width': 'initial'})
    display(split_wid)

    return df,col_wid_list,var_wid_dict,split_wid,var_list

def reorganize_df(df,col_wid_list,var_wid_dict,split_wid,var_list):
    col_values = [wid.value for wid in col_wid_list]
    for param_ in ['x','y','frame','track']:  # mandatory columns
        if param_ not in col_values: 
            raise Exception("You MUST select a column for "+param_)
    df.columns = col_values  # rename columns

    # discard non-relevant columns
    col_values = np.array(col_values)
    new_cols = col_values[col_values!='discard']
    for c in new_cols: 
        if np.count_nonzero(new_cols==c) > 1: # if repeated element
            raise Exception("You have selected several times the column: "+c)
    df = df[new_cols]  
    
    # get names and units of custom variables
    custom_var = {}
    for var in var_list: 
        if var in new_cols:
            custom_var[var] = {'name': var_wid_dict[var]['name'].value, 'unit': var_wid_dict[var]['unit'].value}
    
    # retrieve split traj widget value
    split_traj = True if split_wid.value=='split' else False
    
    #get dimension
    dim_list = ['x','y','z'] if 'z' in df.columns else ['x','y']

    #remove None tracks
    df = df[df['track']!='None']  # remove None tracks
    
    # convert df data type
    for d in dim_list:
        df[d] = df[d].astype(np.float64)

    return df,custom_var,split_traj,dim_list

def make_coord_widget(df,dim_list): 
    """Make widgets to set the coordinates origin and signs"""

    # coordinates origin 
    printmd("""**Do you want to set a custom origin to the coordinates?**""")
    printmd("""Select a new origin by drawing on the image (an image viewer will be displayed at the next cell) and choose which dimension to reset)""")
    ori_onimage_wid=widgets.ToggleButton(value=False,description='Draw on image',style={'description_width': 'initial'})
    reset_dim_wid=widgets.SelectMultiple(options=dim_list,value=['x','y'],description='Dimensions to reset',style={'description_width': 'initial'})
    display(HBox([ori_onimage_wid,reset_dim_wid]))
    printmd("""Or directly type in the new origin (in px)""")
    origin_coord_wid_list=[]
    for dim in dim_list:
        print(dim)
        origin_coord_wid_list.append(widgets.FloatSlider(value=0,min=0,max=df[dim].max(),step=0.1,description=dim,style={'description_width': 'initial'}))
    display(HBox(origin_coord_wid_list))
    
    # axes signs
    printmd("""**Do you want to invert the axes?**
    Default orientation: x: left->right, y: top->bottom, z: slice number""")
    invert_axes_wid=widgets.SelectMultiple(options=dim_list,value=[],description='Axes to invert',style={'description_width': 'initial'})
    display(invert_axes_wid)

    return ori_onimage_wid,reset_dim_wid,origin_coord_wid_list,invert_axes_wid

def unpack_origin_coord(ori_onimage_wid,origin_coord_wid_list,dim_list):
    """Unpack the coordinates from the dataframe"""
    if not ori_onimage_wid.value:
        origin_coord={}
        all_zeros=True
        for d,wid in enumerate(origin_coord_wid_list):
            origin_coord[dim_list[d]]=wid.value
            if wid.value>0:
                all_zeros=False
        if all_zeros: # if no change of origin 
            origin_coord = False
        set_origin_ = origin_coord
    else:
        set_origin_ = True
    
    return set_origin_

def make_plotconfig_widget(plot_param):
    """Make widgets to set the plotting configuration"""

    printmd("## General plotting configuration")

    fig_w_wid = widgets.BoundedIntText(value=plot_param['figsize'][0],min=0,max=20,
                                    description='Figure width (inches):',style={'description_width': 'initial'})
    fig_h_wid = widgets.BoundedIntText(value=plot_param['figsize'][1],min=0,max=20,
                                    description='Figure height (inches):',style={'description_width': 'initial'})
    fig_dpi_wid = widgets.BoundedIntText(value=plot_param['dpi'],min=50,max=1e4,
                                        description='Figure resolution (dpi):',style={'description_width': 'initial'})
    fig_resfac_wid = widgets.FloatSlider(value=1,min=0.01,max=30,step=0.01,
                                        description='Figure size factor:',style={'description_width': 'initial'})
    fig_format_wid = widgets.Dropdown(options=['.png','.svg'],value='.png',
                                    description='Single plot format',style={'description_width': 'initial'})
    save_as_stack_wid = widgets.Checkbox(value=True, description='Save as tiff stack')
    despine_wid = widgets.ToggleButton(value=plot_param['despine'],
                                    description='despine figure')
    replace_color_wid = widgets.BoundedIntText(value=0,min=0,max=20,
                                        description='Number of colors:',style={'description_width': 'initial'})
    add_replace_wid = widgets.Dropdown(options=['add','replace'],value='add',
                                    description='add or replace?',style={'description_width': 'initial'})
    invert_yaxis_wid = widgets.ToggleButton(value=True,description='y axis origin: top')
    export_data_pts_wid = widgets.ToggleButton(value=True,description='export data points')

    display(HBox([fig_w_wid,fig_h_wid]),HBox([fig_dpi_wid,fig_format_wid]),despine_wid)
    printmd('Adjust figure resolution (if orginal image is too small or too large)')
    display(fig_resfac_wid)
    printmd('When plotting over timelapse, plot as a multidimensional tiff stack or as a series of individual image')
    display(save_as_stack_wid)
    printmd('Do you want to add/replace the first default colors used for plotting? Give the number of colors you want to select:')
    display(HBox([replace_color_wid,add_replace_wid]))
    printmd('How do you want to display the y-axis (standard orientation: origin at top)')
    display(invert_yaxis_wid)
    printmd('Do you want to export the data points of your plots as .csv files?')
    display(export_data_pts_wid)

    return fig_w_wid,fig_h_wid,fig_dpi_wid,fig_resfac_wid,fig_format_wid,save_as_stack_wid,despine_wid,replace_color_wid,add_replace_wid,invert_yaxis_wid,export_data_pts_wid


def make_filter_widget(df,subset_num,image):
    """Make widgets to filter the data"""

    # prepare default values for initializing widgets
    xlim = [df['x'].min(), df['x'].max()]  # maybe use image dimensions instead
    ylim = [df['y'].min(), df['y'].max()]
    zlim = [df['z'].min(), df['z'].max()] if 'z' in df.columns else []
    frame_min = df['frame'].min()
    frame_max = df['frame'].max()

    # cropping widget lists
    xlim_wid_list = []
    ylim_wid_list = []
    zlim_wid_list = []
    drawer_wid_list = []
    frame_subset_wid_list = []
    min_length_wid_list = []
    max_length_wid_list = []
    name_wid_list = []

    # retrieve drawer coordinates
    def get_image_coord(ex):
        """Call get_coordinates, display instruction and store coordinates in widget value """
        ex.value = tpr.get_coordinates(image,df=df,verbose=True)


    # create a set of filtering widget for each subset
    for i in range(subset_num):
        printmd("""### Subset #{}""".format(i + 1))

        # subset name
        printmd("""You can give it a custom name that will be used for saving data""")
        name_wid = widgets.Text(value='', placeholder='optional', description='Subset name:',
                                style={'description_width': 'initial'})
        name_wid_list.append(name_wid)
        display(name_wid)

        # spatial filtering
        xlim_wid = widgets.FloatRangeSlider(value=xlim, min=xlim[0], max=xlim[1], step=1,
                                            description='x range (px):', style={'description_width': 'initial'})
        ylim_wid = widgets.FloatRangeSlider(value=ylim, min=ylim[0], max=ylim[1], step=1,
                                            description='y range (px):', style={'description_width': 'initial'})
        if len(zlim) > 0:
            zlim_wid = widgets.FloatRangeSlider(value=zlim, min=zlim[0], max=zlim[1], step=1,
                                                description='z range (px):', style={'description_width': 'initial'})
        drawer_wid = LoadedButton(description="Draw ROI", value={})
        drawer_wid.on_click(get_image_coord)
        # store widgets
        xlim_wid_list.append(xlim_wid)
        ylim_wid_list.append(ylim_wid)
        drawer_wid_list.append(drawer_wid)
        if len(zlim) > 0:
            zlim_wid_list.append(zlim_wid)
        else:
            zlim_wid_list.append(None)
        #display
        printmd("**Select regions based on xy(z) coordinates**")
        printmd("""Select xy(z) coordinates using sliders (in pixels). Alternativaly, xy (not z) coordinates can be 
        selected by directly drawing on a Napari viewer. Click on 'Draw ROI' to display the viewer. If you use the 
        viewer selection, you can define several subsets, and xy coodinates from the sliders will be ignored.""")
        
        if len(zlim) > 0:
            display(VBox([HBox([xlim_wid, ylim_wid, zlim_wid]),drawer_wid]))
        else:
            display(VBox([HBox([xlim_wid, ylim_wid]),drawer_wid]))
            
        printmd("""Draw regions using either rectangles or polygons and hit ENTER when you're done. 
        If you want more details about the Napari viewer please visit https://napari.org/""")

        # time filtering 
        frame_subset_wid = widgets.IntRangeSlider(value=[frame_min, frame_max], min=frame_min, max=frame_max, step=1,
                                                description='Frame subset:', style={'description_width': 'initial'})
        min_length_wid = widgets.IntSlider(value=frame_min, min=frame_min, max=frame_max + 1, step=1,
                                        description='Minimum traj length:', style={'description_width': 'initial'})
        max_length_wid = widgets.IntSlider(value=frame_max + 1, min=frame_min, max=frame_max + 1, step=1,
                                        description='Maximum traj length:', style={'description_width': 'initial'})
        # store widgets
        frame_subset_wid_list.append(frame_subset_wid)
        min_length_wid_list.append(min_length_wid)
        max_length_wid_list.append(max_length_wid)
        # display
        printmd("**Select data based on trajectories duration or frame subset**")
        display(HBox([frame_subset_wid, min_length_wid, max_length_wid]))

    filter_wid_dict = {'xlim_wid_list':xlim_wid_list, 
                        'ylim_wid_list':ylim_wid_list, 
                        'zlim_wid_list':zlim_wid_list, 
                        'drawer_wid_list':drawer_wid_list, 
                        'frame_subset_wid_list':frame_subset_wid_list, 
                        'min_length_wid_list':min_length_wid_list, 
                        'max_length_wid_list':max_length_wid_list, 
                        'name_wid_list':name_wid_list,
                        }

    return filter_wid_dict
    

def retrieve_region_wid_values(drawer_wid,xlim_wid,ylim_wid,zlim_wid):
    """
    Get values of region selection giving priority to drawer widgets over sliders
    """
    # xy coordinates
    
    # default values if not selected through drawer
    xlim_list = []
    ylim_list = []
    polygon_list = []
    ROI_drawn = False  # ROI selected through drawer
    
    # update xylim and polygon if selected thtough drawer
    drawer_value = drawer_wid.value
    if drawer_value: #if not empty
        if len(drawer_value['rectangle']) > 0:  # there are rectangles
            #get list of xlim, ylim in case of several ROIs selected
            xlim_list = [r['xlim'] for r in drawer_value['rectangle']]
            ylim_list = [r['ylim'] for r in drawer_value['rectangle']]
            ROI_drawn = True
        if len(drawer_value['polygon']) > 0:  # there are polygons
            polygon_list = [r['coord'] for r in drawer_value['polygon']]
            ROI_drawn = True
        
    if not ROI_drawn:
        xlim_list = [xlim_wid.value]
        ylim_list = [ylim_wid.value]
    
    # z coordinates
    if zlim_wid is None:
        zlim = None
    else: 
        zlim = zlim_wid.value
        
    return xlim_list, ylim_list, zlim, polygon_list

def retrieve_filter_values(subset_num, filter_wid_dict):
    """
    Retrieve values of filters
    """

    # unpack widgets dict
    xlim_wid_list = filter_wid_dict['xlim_wid_list']
    ylim_wid_list = filter_wid_dict['ylim_wid_list']
    zlim_wid_list = filter_wid_dict['zlim_wid_list'] 
    drawer_wid_list = filter_wid_dict['drawer_wid_list'] 
    frame_subset_wid_list = filter_wid_dict['frame_subset_wid_list'] 
    min_length_wid_list = filter_wid_dict['min_length_wid_list'] 
    max_length_wid_list = filter_wid_dict['max_length_wid_list'] 
    name_wid_list = filter_wid_dict['name_wid_list']

    filters=[]
    for i in range(subset_num):
        xlim_list, ylim_list, zlim_, polygon_list = retrieve_region_wid_values(drawer_wid_list[i],
                                                                            xlim_wid_list[i],
                                                                            ylim_wid_list[i],
                                                                            zlim_wid_list[i])
        
        total_num_ROIs = len(xlim_list) + len(polygon_list) # total number of ROIs
        
        # if several rectangles get values of xlim, ylim, while keeping other filters constant
        for j in range(len(xlim_list)):  
            #name
            if total_num_ROIs > 1:  # if several subsets, modify name: name_number if name is empty: number
                name = name_wid_list[i].value + '_rectangle{}'.format(j+1) if name_wid_list[i].value != '' else 'rectangle{}'.format(j+1)
            else: 
                name = name_wid_list[i].value
            
            # initialize filter dict
            default_filter = tpr.init_filters(data_dir=None, export_config=False)
            filt_ = default_filter['filters_list'][0]  
            # fill info
            filt_['xlim'] = xlim_list[j]
            filt_['ylim'] = ylim_list[j]
            filt_['zlim'] = zlim_
            filt_['frame_subset'] = frame_subset_wid_list[i].value
            filt_['min_traj_len'] = min_length_wid_list[i].value
            filt_['max_traj_len'] = max_length_wid_list[i].value
            filt_['name'] = name
            # add to filter list
            filters.append(filt_)
        
        # if several polygons get values of xlim, ylim, while keeping other filters constant
        for j in range(len(polygon_list)):  
            #name
            if total_num_ROIs > 1:  # if several subsets, modify name: name_number if name is empty: number
                name = name_wid_list[i].value + '_polygon{}'.format(j+1) if name_wid_list[i].value != '' else 'polygon{}'.format(j+1)
            else: 
                name = name_wid_list[i].value
            
            # initialize filter dict
            default_filter = tpr.init_filters(data_dir=None, export_config=False)
            filt_ = default_filter['filters_list'][0]  
            # fill info
            filt_['ROI'] = polygon_list[j]
            filt_['zlim'] = zlim_
            filt_['frame_subset'] = frame_subset_wid_list[i].value
            filt_['min_traj_len'] = min_length_wid_list[i].value
            filt_['max_traj_len'] = max_length_wid_list[i].value
            filt_['name'] = name
            # add to filter list
            filters.append(filt_)
            
    printmd("**Select specific tracks**")
    printmd("You can select specific sets of tracks. "
            "This tool can be useful to perform fate mapping or retrospective mapping. "
            "If you selected several subsets before, this specific set will be applied to all of the subsets."
        )
    printmd("How many sets of tracks do you want to select?")
    set_num_wid = widgets.BoundedIntText(value=0,min=0,max=10,description='Number of sets:',style={'description_width': 'initial'})
    display(set_num_wid)

    return filters, set_num_wid

def make_track_widget(set_num,df,image):
    """
    Make widgets to select specific tracks
    """

    # prepare default values for initializing widgets
    xlim = [df['x'].min(), df['x'].max()]  # maybe use image dimensions instead
    ylim = [df['y'].min(), df['y'].max()]
    zlim = [df['z'].min(), df['z'].max()] if 'z' in df.columns else []
    frame_min = df['frame'].min()
    frame_max = df['frame'].max()

    # select specific trajectories
    # track selection widget lists
    track_name_wid_list = []
    track_xlim_wid_list = []
    track_ylim_wid_list = []
    track_zlim_wid_list = []
    track_drawer_wid_list = []
    track_frame_subset_wid_list = []
    track_list_wid_list = []

    # retrieve drawer coordinates
    def get_image_coord(ex):
        """Call get_coordinates, display instruction and store coordinates in widget value """
        ex.value = tpr.get_coordinates(image,df=df,verbose=True)

    for i in range(set_num):
        printmd("""### Set #{}""".format(i + 1))
        
        # subset name
        printmd("""You can give it a custom name that will be used for saving data""")
        track_name_wid = widgets.Text(value='', placeholder='optional', description='Set name:',
                                style={'description_width': 'initial'})
        track_name_wid_list.append(track_name_wid)
        display(track_name_wid)
        
        track_list_wid = widgets.Text(value='', placeholder='comma separated IDs', description='ID list:')
        track_xlim_wid = widgets.FloatRangeSlider(value=xlim, min=xlim[0], max=xlim[1], step=1,
                                            description='x range (px):', style={'description_width': 'initial'})
        track_ylim_wid = widgets.FloatRangeSlider(value=ylim, min=ylim[0], max=ylim[1], step=1,
                                            description='y range (px):', style={'description_width': 'initial'})
        if len(zlim) > 0:
            track_zlim_wid = widgets.FloatRangeSlider(value=zlim, min=zlim[0], max=zlim[1], step=1,
                                                description='z range (px):', style={'description_width': 'initial'})
        track_frame_subset_wid = widgets.IntRangeSlider(value=[frame_min, frame_max], min=frame_min, max=frame_max, step=1,
                                        description='Frame interval:', style={'description_width': 'initial'})
        track_drawer_wid = LoadedButton(description="Draw ROI", value={})
        track_drawer_wid.on_click(get_image_coord)
        # store widgets
        track_list_wid_list.append(track_list_wid)
        track_xlim_wid_list.append(track_xlim_wid)
        track_ylim_wid_list.append(track_ylim_wid)
        track_drawer_wid_list.append(track_drawer_wid)
        track_frame_subset_wid_list.append(track_frame_subset_wid)
        if len(zlim) > 0:
            track_zlim_wid_list.append(track_zlim_wid)
        else:
            track_zlim_wid_list.append(None)

        #display
        printmd("**Select tracks based on their xy(z)t coordinates**")
        printmd("""Select a xy(z) region containing the tracks at times given by the frame interval. 
        xy coordinates can be selected using sliders or by drawing on a Napari viewer. If you use the 
        viewer selection (by clicking on 'Draw ROI'), you can define several subsets, and xy coodinates from the sliders will be ignored.""")

        if len(zlim) > 0:
            display(VBox([track_drawer_wid, HBox([track_xlim_wid, track_ylim_wid, track_zlim_wid]),track_frame_subset_wid]))
        else:
            display(VBox([track_drawer_wid, HBox([track_xlim_wid, track_ylim_wid]),track_frame_subset_wid]))
        
        printmd("**Alternatively, select tracks based on their IDs**")
        
        printmd("""When running Track Analyzer at least once on your dataset, you can display 
        tracks IDs when plotting trajectories. Use these IDs to directly select tracks.""")
        display(track_list_wid)

    filter_wid_dict = {'track_list_wid_list':track_list_wid_list,
                       'track_xlim_wid_list':track_xlim_wid_list,
                       'track_ylim_wid_list':track_ylim_wid_list,
                       'track_zlim_wid_list':track_zlim_wid_list,
                       'track_drawer_wid_list':track_drawer_wid_list,
                       'track_frame_subset_wid_list':track_frame_subset_wid_list,
                       'track_name_wid_list':track_name_wid_list,
                       }

    return filter_wid_dict

def retrieve_set_filter_values(filters, set_num, filter_wid_dict):
    """
    Retrieve values of set of tracks filters
    """

    # unpack widgets dict
    track_list_wid_list = filter_wid_dict['track_list_wid_list']
    track_xlim_wid_list = filter_wid_dict['track_xlim_wid_list']
    track_ylim_wid_list = filter_wid_dict['track_ylim_wid_list'] 
    track_zlim_wid_list = filter_wid_dict['track_zlim_wid_list'] 
    track_drawer_wid_list = filter_wid_dict['track_drawer_wid_list'] 
    track_frame_subset_wid_list = filter_wid_dict['track_frame_subset_wid_list'] 
    track_name_wid_list = filter_wid_dict['track_name_wid_list'] 

    # get widgets values
    if set_num == 0: # if no set of tracks selected, just copy the filters
        new_filters = list(filters)
    else: 
        new_filters = []
        # for each set of filters, copy them to new sets of filters modified by the trajectory filters
        for filt in filters:   
            for i in range(set_num):
                # trajectory list selection
                track_list_val = track_list_wid_list[i].value
                if track_list_val == '':
                    track_list_val = None
                else:
                    try:
                        track_list_val = [int(e) for e in track_list_val.split(',')]
                    except:
                        print("ERROR: a value in the list is not a number")
                        track_list_val = None

                # ROI selection
                regions_wids = retrieve_region_wid_values(track_drawer_wid_list[i],
                                                        track_xlim_wid_list[i],
                                                        track_ylim_wid_list[i],
                                                        track_zlim_wid_list[i])
                
                track_xlim_list, track_ylim_list, track_zlim_, track_polygon_list = regions_wids
                
                t_total_num_ROIs = len(track_xlim_list) + len(track_polygon_list) # total number of ROIs

                # if several rectangles, get values of xlim, ylim, while keeping other filters constant
                for j in range(len(track_xlim_list)):
                    ROI = {'xlim': track_xlim_list[j],
                        'ylim': track_ylim_list[j],
                        'zlim': track_zlim_,
                        'ROI': None,
                        'frame_lim': track_frame_subset_wid_list[i].value,
                        }
                    #name
                    if t_total_num_ROIs > 1:  # if several subsets, modify name
                        name = track_name_wid_list[i].value + '_rectangle{}'.format(j+1) if track_name_wid_list[i].value !='' else 'rectangle{}'.format(j+1)
                    else: 
                        name = track_name_wid_list[i].value

                    # add new filters to existing filters
                    new_filt = dict(filt)  # make copy of old filters
                    new_filt['track_list'] = track_list_val
                    new_filt['track_ROI'] = ROI
                    if new_filt['name'] == '':
                        new_filt['name'] = name  # name = setname
                    else:
                        if name != '':
                            new_filt['name'] += '_' + name  # name = subsetname_setname

                    # store in a new list of filters
                    new_filters.append(new_filt)
                
                # if several polygons, get values of xlim, ylim, while keeping other filters constant
                for j in range(len(track_polygon_list)):
                    ROI = {'ROI': track_polygon_list[j],
                        'xlim': None,
                        'ylim': None,
                        'zlim': track_zlim_,
                        'frame_lim': track_frame_subset_wid_list[i].value,
                        }
                    #name
                    if t_total_num_ROIs > 1:  # if several subsets, modify name
                        name = track_name_wid_list[i].value + '_polygon{}'.format(j+1) if track_name_wid_list[i].value !='' else 'polygon{}'.format(j+1)
                    else: 
                        name = track_name_wid_list[i].value

                    # add new filters to existing filters
                    new_filt = dict(filt)  # make copy of old filters
                    new_filt['track_list'] = track_list_val
                    new_filt['track_ROI'] = ROI
                    if new_filt['name'] == '':
                        new_filt['name'] = name  # name = setname
                    else:
                        if name != '':
                            new_filt['name'] += '_' + name  # name = subsetname_setname

                    # store in a new list of filters
                    new_filters.append(new_filt)

    printmd('You set {} subsets. Edit their names and order to be plotted if needed.'.format(len(new_filters)))
    filt_names_wid_list = []
    order_wid_list = []
    for i,filt in enumerate(new_filters):
        print('subset {}'.format(i+1))
        print(filt)
        name_wid = widgets.Text(value=filt['name'], placeholder='optional', description='Subset name:',
                                style={'description_width': 'initial'})
        filt_names_wid_list.append(name_wid)
        # using numbering starting at 1 for users
        order_wid = widgets.BoundedIntText(value=i+1,min=1,max=len(new_filters)+1,description='order',style={'description_width': 'initial'})
        order_wid_list.append(order_wid)
        display(HBox([name_wid,order_wid]))
        printmd('---')

    return new_filters, filt_names_wid_list, order_wid_list


def make_traj_param_widgets(data,filters_dict,custom_var,info):
    """
    Make widgets for trajectory plotting
    """

    df = data['df']
    timescale = data['timescale']

    # prepare default values for widgets
    if data['dim'] == 2:
        dimensions = ['x', 'y']
        vel = ['v' + dim for dim in dimensions]
        acc = ['a' + dim for dim in dimensions]
        color_code_list = ['none','t', 'group', 'random','v','a'] + vel + acc + list(custom_var.keys())
        # if several subset plotted together, color code default: ROI
        if len(filters_dict['filters_list']) and filters_dict['subset'] == 'together':
            color_code_default = 'group'
        else:
            color_code_default = 'random'
    elif data['dim'] == 3:
        dimensions = ['x', 'y', 'z']
        vel = ['v' + dim for dim in dimensions]
        acc = ['a' + dim for dim in dimensions]
        color_code_list = ['none','z', 't', 'group', 'random','v','a'] + vel + acc + list(custom_var.keys())
        # if several subset plotted together, color code default: ROI
        if len(filters_dict['filters_list']) and filters_dict['subset'] == 'together':
            color_code_default = 'group'
        else:
            color_code_default = 'z'

            
    ### Section 1
    printmd('### Plotting options')

    printmd("**1. Trajectory plotting**")

    ## TAB 1
    # widgets
    traj_module_wid = widgets.ToggleButton(value=True, description='Run module')
    show_axis_wid = widgets.Checkbox(value=False, description='show axes')
    bkg_wid = widgets.Checkbox(value=False, description='hide background image')
    show_tail_wid = widgets.Checkbox(value=True, description='show trajectory tail')
    marker_size_wid = widgets.FloatSlider(value=1., min=0, max=20, steps=0.1,
                                        description='Relative size of dots and lines:',
                                        style={'description_width': 'initial'})
    hide_lab_wid = widgets.Checkbox(value=True, description='hide track label')
    lab_size_wid = widgets.IntSlider(value=6, min=0, max=100, description='Track label size (pt):',
                                    style={'description_width': 'initial'})
    color_code_wid = widgets.Dropdown(options=color_code_list, value=color_code_default, description='color code',
                                    style={'description_width': 'initial'})
    colormap_wid = widgets.Dropdown(options=['plasma', 'viridis', 'cividis', 'jet'], value='plasma', description='colormap',
                                    style={'description_width': 'initial'})
    inc_wid = widgets.BoundedIntText(value=1, min=1, max=df['frame'].max(), description='Plotting frame increment:',
                                        style={'description_width': 'initial'})
    lab_1 = Label('Plot trajectories frame by frame')

    # layout
    left_box_1 = VBox([show_axis_wid,bkg_wid, show_tail_wid, hide_lab_wid])
    right_box_1 = VBox([lab_size_wid, marker_size_wid, color_code_wid, colormap_wid,inc_wid])
    tab_1_ = HBox([left_box_1, right_box_1])
    tab_1 = VBox([lab_1, traj_module_wid, tab_1_])

    ## TAB 2
    # widgets
    xrange = np.abs(df['x_scaled'].max() - df['x_scaled'].min())
    yrange = np.abs(df['y_scaled'].max() - df['y_scaled'].min())
    xlim = [df['x_scaled'].min() - xrange, df['x_scaled'].max() + xrange]  # define custom xlim with wider boundaries
    ylim = [df['y_scaled'].min() - yrange, df['y_scaled'].max() + yrange]  # define custom ylim with wider boundaries
    all_traj_module_wid = widgets.ToggleButton(value=True, description='Run module')
    hide_lab_wid_2 = widgets.Checkbox(value=True, description='hide track label')
    center_wid = widgets.Checkbox(value=True, description='center origin')
    equal_axis_wid = widgets.Checkbox(value=False, description='equal scale on x/y axes')
    setlim_wid = widgets.Checkbox(value=False, description='set custom axis limits')
    lab_size_wid_2 = widgets.IntSlider(value=6, min=0, max=100, description='Track label size (pt):',
                                    style={'description_width': 'initial'})
    color_code_wid_2 = widgets.Dropdown(options=color_code_list, value=color_code_default, description='color code',
                                        style={'description_width': 'initial'})
    colormap_wid2 = widgets.Dropdown(options=['plasma', 'viridis', 'cividis', 'jet'], value='plasma',
                                    description='colormap',
                                    style={'description_width': 'initial'})
    xlim_wid = widgets.FloatRangeSlider(value=xlim, min=xlim[0], max=xlim[1], step=1,
                                        description='x range ({}):'.format(info['length_unit']),
                                        style={'description_width': 'initial'})
    ylim_wid = widgets.FloatRangeSlider(value=ylim, min=ylim[0], max=ylim[1], step=1,
                                        description='y range ({}):'.format(info['length_unit']),
                                        style={'description_width': 'initial'})
    traj_alpha_wid = widgets.FloatSlider(value=1, min=0, max=1, steps=0.01, description='transparency',
                                    style={'description_width': 'initial'})
    lab_2 = Label('Plot total trajectories')

    # layout
    left_box_2 = VBox([hide_lab_wid_2, center_wid, equal_axis_wid, setlim_wid,traj_alpha_wid])
    right_box_2 = VBox([lab_size_wid_2, color_code_wid_2, colormap_wid2, xlim_wid, ylim_wid])
    tab_2_ = HBox([left_box_2, right_box_2])
    tab_2 = VBox([lab_2, all_traj_module_wid, tab_2_])

    # display Section 1
    tab_titles = ['Plot frame by frame', 'Plot total trajectories']
    tab = widgets.Tab()
    tab.children = [tab_1, tab_2]
    for i in range(len(tab_titles)):
        tab.set_title(i, tab_titles[i])
    display(tab)


    ### Section 2
    printmd("**2. Parameter plotting**")

    param_module_wid = widgets.ToggleButton(value=True, description='Run module')
    display(param_module_wid)
    printmd("*Two kinds of parameters can be plotted: instantaneous parameters (measured at each time point), and parameters calculated over a whole track.*")
    printmd("*You can plot histograms or boxplots of single parameters or scatter plots of a couple of parameters (e.g. v vs y)*")
    printmd(
        "How many instantaneous parameters do you want to plot? (enter 0 if you don't want to plot parameters)")
    param_hist_num_wid = widgets.BoundedIntText(value=0, min=0, max=20, description='Number of histograms:',
                                                style={'description_width': 'initial'})
    param_box_num_wid = widgets.BoundedIntText(value=0, min=0, max=20, description='Number of boxplots:',
                                                style={'description_width': 'initial'})
    param_couple_num_wid = widgets.BoundedIntText(value=0, min=0, max=20, description='Number of scatter plots:',
                                                style={'description_width': 'initial'})
    display(HBox([param_hist_num_wid, param_box_num_wid, param_couple_num_wid]))
    printmd(
        "How many whole-trajectory parameters do you want to plot? (enter 0 if you don't want to plot parameters)")
    tparam_hist_num_wid = widgets.BoundedIntText(value=0, min=0, max=20, description='Number of histograms:',
                                                style={'description_width': 'initial'})
    tparam_box_num_wid = widgets.BoundedIntText(value=0, min=0, max=20, description='Number of boxplots:',
                                                style={'description_width': 'initial'})
    tparam_couple_num_wid = widgets.BoundedIntText(value=0, min=0, max=20, description='Number of scatter plots:',
                                                style={'description_width': 'initial'})
    display(HBox([tparam_hist_num_wid, tparam_box_num_wid, tparam_couple_num_wid]))


    ### Section 3
    printmd("**3. Mean Squared Displacement (MSD) analysis**")
    MSD_module_wid = widgets.ToggleButton(value=True, description='Run module')
    display(MSD_module_wid)

    printmd("You can either plot the MSD, or/and fit it with a random walk model")
    MSD_mode_wid = widgets.Dropdown(options=['only plot MSD', 'plot MSD and fit'], value='plot MSD and fit',
                                    description='Choose analysis: ',
                                    style={'description_width': 'initial'})
    display(MSD_mode_wid)

    printmd("***")
    printmd("*Plotting section*")
    printmd(
        "Plot MSD altogether or as single plots. For a large number of tracks, plotting single MSDs can be long... Consider not plotting them.")
    all_MSD_plot_wid = widgets.ToggleButton(value=True, description='plot MSD altogether')
    single_MSD_plot_wid = widgets.ToggleButton(value=False, description='single MSD plots')
    logplot_wid_x = widgets.Checkbox(value=True, description='x axis')
    logplot_wid_y = widgets.Checkbox(value=True, description='y axis')
    alpha_lab = Label('For all MSD plots, set the transparency (0=transparent, 1=opaque)')
    alpha_wid = widgets.FloatSlider(value=0.2, min=0, max=1, steps=0.01, description='transparency',
                                    style={'description_width': 'initial'})
    display(HBox([all_MSD_plot_wid, single_MSD_plot_wid]))
    display(HBox([Label('log plot: '), logplot_wid_x, logplot_wid_y]))
    display(HBox([alpha_lab, alpha_wid]))

    printmd("***")
    printmd("*Fitting section*")
    printmd("The MSD can be fitted with three different random walk models")
    MSD_wid = widgets.Dropdown(options=['random walk', 'biased random walk', 'persistent random walk'], value='biased random walk',
                            description='Choose model: ',
                            style={'description_width': 'initial'})
    display(MSD_wid)
    dim_wid = widgets.Dropdown(options=['2D', '3D'], value='2D', description='dimension: ',
                            style={'description_width': 'initial'})
    fitrange_wid = widgets.IntSlider(value=6 * timescale, min=0, max=df['t'].max(), step=1,
                                    description='Maximum lag time ({})'.format(info['time_unit']),
                                    style={'description_width': 'initial'})

    printmd("Perform MSD analysis in 2D (along the xy dimensions) or 3D")
    display(dim_wid)
    printmd(
        "Fitting MSDs can be difficult (at long lag times the calculation is very noisy because of the poor statistics). It is often necessary to restrict the fit to short lag times. ")
    display(fitrange_wid)

    ### Section 4
    printmd("**4. Voronoi analysis**")
    vor_module_wid = widgets.ToggleButton(value=True, description='Run module')
    display(vor_module_wid)

    # plotting parameters
    vor_show_axis_wid = widgets.Checkbox(value=False, description='show axes')
    vor_bkg_wid = widgets.Checkbox(value=False, description='hide background image')
    vor_plot_wid = widgets.Checkbox(value=True, description='plot diagram')
    vor_area_wid = widgets.Checkbox(value=True, description='show cell area')
    vor_area_thr_wid = widgets.BoundedFloatText(value=3, min=0, max=100, step=0.1,
                                            description='Max area threshold:',
                                            style={'description_width': 'initial'})
    vor_cmap_wid = widgets.Dropdown(options=['plasma', 'viridis', 'cividis', 'jet'], value='plasma', description='colormap',
                                    style={'description_width': 'initial'})
    vor_linewidth_wid = widgets.FloatSlider(value=1., min=0.01, max=20, steps=0.1,
                                        description='Diagram line width:',
                                        style={'description_width': 'initial'})
    vor_vmin_val_wid = widgets.BoundedFloatText(value=0, min=1e-6, max=1e6, step=1e-6,
                                            description='Minimal limit:',
                                            style={'description_width': 'initial'})
    vor_vmin_bool_wid = widgets.Checkbox(value=False, description='set custom limit')
    vor_vmax_val_wid = widgets.BoundedFloatText(value=0, min=1e-6, max=1e6, step=1e-6,
                                            description='Maximal limit:',
                                            style={'description_width': 'initial'})
    vor_vmax_bool_wid = widgets.Checkbox(value=False, description='set custom limit')
    inc_wid_vor = widgets.BoundedIntText(value=1, min=1, max=df['frame'].max(), description='Plotting frame increment:',
                                        style={'description_width': 'initial'})

    display(HBox([VBox([vor_show_axis_wid, vor_bkg_wid, vor_plot_wid,vor_linewidth_wid]),VBox([vor_area_wid, vor_area_thr_wid, vor_cmap_wid,inc_wid_vor])]))

    printmd('Optional: set custom plotting limits to area color code (in squared unit)')
    display(VBox([HBox([vor_vmin_bool_wid,vor_vmin_val_wid]),HBox([vor_vmax_bool_wid,vor_vmax_val_wid])]))

    traj_wid_dict = {
        'traj_wids': [traj_module_wid,show_axis_wid,bkg_wid,show_tail_wid,marker_size_wid,hide_lab_wid,lab_size_wid,color_code_wid,colormap_wid,inc_wid],
        'tot_traj_wids':[all_traj_module_wid,hide_lab_wid_2,center_wid,equal_axis_wid,setlim_wid,lab_size_wid_2,color_code_wid_2,colormap_wid2,xlim_wid,ylim_wid,traj_alpha_wid],
        'param_wids':[param_module_wid,param_hist_num_wid,param_box_num_wid,param_couple_num_wid,tparam_hist_num_wid,tparam_box_num_wid,tparam_couple_num_wid],
        'MSD_wids':[MSD_module_wid,MSD_mode_wid,all_MSD_plot_wid,single_MSD_plot_wid,logplot_wid_x,logplot_wid_y,alpha_wid,MSD_wid,dim_wid,fitrange_wid],
        'vor_wids':[vor_module_wid,vor_show_axis_wid,vor_bkg_wid,vor_plot_wid,vor_linewidth_wid,vor_area_wid,vor_area_thr_wid,vor_cmap_wid,vor_vmin_bool_wid,vor_vmin_val_wid,vor_vmax_bool_wid,vor_vmax_val_wid,inc_wid_vor]
    }

    return traj_wid_dict

def make_param_plot_widgets(data,traj_wid_dict,custom_var):
    """
    Make widgets for parameter plotting
    """

    # unpack necessary widgets values
    [param_module_wid,param_hist_num_wid,param_box_num_wid,param_couple_num_wid,tparam_hist_num_wid,tparam_box_num_wid,tparam_couple_num_wid] = traj_wid_dict['param_wids']
    [MSD_module_wid,MSD_mode_wid,all_MSD_plot_wid,single_MSD_plot_wid,logplot_wid_x,logplot_wid_y,alpha_wid,MSD_wid,dim_wid,fitrange_wid] = traj_wid_dict['MSD_wids']
    [vor_module_wid,vor_show_axis_wid,vor_bkg_wid,vor_plot_wid,vor_linewidth_wid,vor_area_wid,vor_area_thr_wid,vor_cmap_wid,vor_vmin_bool_wid,vor_vmin_val_wid,vor_vmax_bool_wid,vor_vmax_val_wid,inc_wid_vor] = traj_wid_dict['vor_wids']

    # get MSD parameters
    if not MSD_module_wid.value:
        MSD_fit = False
    else:
        if MSD_mode_wid.value == 'only plot MSD':
            MSD_fit = None
        else:
            MSD_model_dict = {'random walk': 'pure_diff', 'biased random walk': 'biased_diff',
                            'persistent random walk': 'PRW'}
            MSD_fit = MSD_model_dict[MSD_wid.value]

    # prepare parameters lists
    if param_module_wid.value:
        dimensions = ['x', 'y'] if data['dim'] == 2 else ['x', 'y', 'z']
        scaled_dimensions = [dim + '_scaled' for dim in dimensions]
        vel = ['v' + dim for dim in dimensions]
        acc = ['a' + dim for dim in dimensions]

        params = ['track', 't'] + dimensions + scaled_dimensions + vel + acc + ['v', 'a'] + list(custom_var.keys())
        params_track = ['track', 'track_length', 't'] + dimensions + scaled_dimensions + vel + acc + ['v', 'a'] + list(custom_var.keys())

        # add MSD output to track parameters
        if MSD_fit is not None and MSD_fit is not False:
            MSD_param = 'P' if MSD_fit == 'PRW' else 'D'
            params_track += [MSD_param]
        # add voronoi output to instantaneous parameters
        if vor_module_wid.value:
            params += ['area']
            params_track += ['area']

        # default
        default_param = 'v'
        default_xparam = ['x', 'y', 't']

        # histogram widgets
        param_hist_wid_list = []
        tparam_hist_wid_list = []
        for i in range(param_hist_num_wid.value):
            w = widgets.Dropdown(options=params, value=default_param, description='parameter',
                                style={'description_width': 'initial'})
            param_hist_wid_list.append(w)
        box_1 = VBox(param_hist_wid_list)
        for i in range(tparam_hist_num_wid.value):
            w = widgets.Dropdown(options=params_track, value=default_param, description='parameter',
                                style={'description_width': 'initial'})
            tparam_hist_wid_list.append(w)
        box_2 = VBox(tparam_hist_wid_list)
        
        # boxplots widgets
        boxplot_wid = widgets.Checkbox(value=True, description='Show boxplot')
        swarmplot_wid = widgets.Checkbox(value=False, description='Show swarmplot')
        ttest_wid = widgets.Checkbox(value=True, description='Run t-test')
        param_box_wid_list = []
        hue_box_wid_list = []
        huecmap_box_wid_list = []
        row_list = []
        
        for i in range(param_box_num_wid.value):
            w = widgets.Dropdown(options=params, value=default_param, description='parameter',
                                style={'description_width': 'initial'})
            param_box_wid_list.append(w)
            w1 = widgets.Dropdown(options=[None]+params, value=None, description='hue',
                                style={'description_width': 'initial'})
            hue_box_wid_list.append(w1)
            w2 = widgets.Dropdown(options=['plasma', 'viridis', 'cividis', 'jet'], value='plasma', description='colormap',
                                    style={'description_width': 'initial'})
            huecmap_box_wid_list.append(w2)
            row_list.append(HBox([w,w1,w2]))
        
        box_6 = VBox([HBox([boxplot_wid, swarmplot_wid, ttest_wid])]+row_list)
        
        tparam_box_wid_list = []
        t_hue_box_wid_list = []
        t_huecmap_box_wid_list = []
        t_row_list = []
        t_boxplot_wid = widgets.Checkbox(value=True, description='Show boxplot')
        t_swarmplot_wid = widgets.Checkbox(value=True, description='Show swarmplot')
        t_ttest_wid = widgets.Checkbox(value=True, description='Run t-test')
        for i in range(tparam_box_num_wid.value):
            w = widgets.Dropdown(options=params_track, value=default_param, description='parameter',
                                style={'description_width': 'initial'})
            tparam_box_wid_list.append(w)
            w1 = widgets.Dropdown(options=[None]+params_track, value=None, description='hue',
                                style={'description_width': 'initial'})
            t_hue_box_wid_list.append(w1)
            w2 = widgets.Dropdown(options=['plasma', 'viridis', 'cividis', 'jet'], value='plasma', description='colormap',
                                    style={'description_width': 'initial'})
            t_huecmap_box_wid_list.append(w2)
            t_row_list.append(HBox([w,w1,w2]))
        box_7 = VBox([HBox([t_boxplot_wid, t_swarmplot_wid, t_ttest_wid])]+t_row_list)

        # couples widgets
        xparam_wid_list = []
        yparam_wid_list = []
        hue_param_wid_list = []
        cmap_param_wid_list = []
        for i in range(param_couple_num_wid.value):
            x = widgets.Dropdown(options=params, value=default_xparam[i % len(default_xparam)], description='x parameter',
                                style={'description_width': 'initial'})
            y = widgets.Dropdown(options=params, value=default_param, description='y parameter',
                                style={'description_width': 'initial'})
            hue = widgets.Dropdown(options=params, value=None, description='hue',
                                style={'description_width': 'initial'})
            cmap = widgets.Dropdown(options=['plasma', 'viridis', 'cividis', 'jet'], value='plasma', description='colormap',
                                    style={'description_width': 'initial'})
            xparam_wid_list.append(x)
            yparam_wid_list.append(y)
            hue_param_wid_list.append(hue)
            cmap_param_wid_list.append(cmap)

        box_3 = HBox([VBox(xparam_wid_list),VBox(yparam_wid_list),VBox(hue_param_wid_list),VBox(cmap_param_wid_list)])

        t_xparam_wid_list = []
        t_yparam_wid_list = []
        t_hue_param_wid_list = []
        t_cmap_param_wid_list = []
        for i in range(tparam_couple_num_wid.value):
            x = widgets.Dropdown(options=params_track, value=default_xparam[i % len(default_xparam)],
                                description='x parameter',
                                style={'description_width': 'initial'})
            y = widgets.Dropdown(options=params_track, value=default_param, description='y parameter',
                                style={'description_width': 'initial'})
            hue = widgets.Dropdown(options=params_track, value=None, description='hue',
                                style={'description_width': 'initial'})
            cmap = widgets.Dropdown(options=['plasma', 'viridis', 'cividis', 'jet'], value='plasma', description='colormap',
                                    style={'description_width': 'initial'})
            t_xparam_wid_list.append(x)
            t_yparam_wid_list.append(y)
            t_hue_param_wid_list.append(hue)
            t_cmap_param_wid_list.append(cmap)

        box_4 = HBox([VBox(t_xparam_wid_list),VBox(t_yparam_wid_list),VBox(t_hue_param_wid_list),VBox(t_cmap_param_wid_list)])

        
        # scatter plots parameters
        scatter_wid = widgets.Checkbox(value=True, description='Show scatter plot')
        reg_wid = widgets.Checkbox(value=True, description='Show regression plot')
        ci_wid = widgets.FloatSlider(value=95, min=0, max=100, steps=0.1,
                                        description='Confidence interval:',
                                        style={'description_width': 'initial'})
        xbin_wid = widgets.Checkbox(value=False, description='Bin data along x axis')
        xbin_num_wid = widgets.IntSlider(value=10, min=1, max=100,
                                        description='Number of evenly spaced bins:',
                                        style={'description_width': 'initial'})
        box_5 = VBox([HBox([scatter_wid, reg_wid,xbin_wid]),HBox([ci_wid,xbin_num_wid])])

        acc1 = widgets.Accordion(children=[box_1, box_2])
        acc3 = widgets.Accordion(children=[box_6, box_7])
        acc2 = widgets.Accordion(children=[box_5,box_3, box_4])
        acc_titles = ['Instantaneous parameters', 'Whole_trajectory parameters']
        for i in range(len(acc_titles)):
            acc1.set_title(i, acc_titles[i])
            acc3.set_title(i, acc_titles[i])
        acc_titles_2 = ['Plotting parameters'] + acc_titles
        for i in range(len(acc_titles_2)):
            acc2.set_title(i, acc_titles_2[i])
        
        # layout
        tab_titles = ['Histograms', 'Boxplots', 'Scatter plots']
        tab = widgets.Tab()
        tab.children = [acc1, acc3, acc2]
        for i in range(len(tab_titles)):
            tab.set_title(i, tab_titles[i])
        display(tab)

    param_plot_widgets_dict = {
        'hist': [param_hist_wid_list,tparam_hist_wid_list],
        'box': [boxplot_wid,swarmplot_wid,ttest_wid,param_box_wid_list,hue_box_wid_list,huecmap_box_wid_list,tparam_box_wid_list,t_hue_box_wid_list,t_huecmap_box_wid_list,t_row_list,t_boxplot_wid,t_swarmplot_wid,t_ttest_wid],
        'scatter': [xparam_wid_list,yparam_wid_list,hue_param_wid_list,cmap_param_wid_list,t_xparam_wid_list,t_yparam_wid_list,t_hue_param_wid_list,t_cmap_param_wid_list,scatter_wid,reg_wid,ci_wid,xbin_wid,xbin_num_wid],
        }
    

    return param_plot_widgets_dict


def retrieve_traj_param_widgets(traj_wid_dict,param_plot_widgets_dict):
    """
    Retrieve trajectory widgets
    """

    # unpack widgets values
    [traj_module_wid,show_axis_wid,bkg_wid,show_tail_wid,marker_size_wid,hide_lab_wid,lab_size_wid,color_code_wid,colormap_wid,inc_wid] = traj_wid_dict['traj_wids']
    [all_traj_module_wid,hide_lab_wid_2,center_wid,equal_axis_wid,setlim_wid,lab_size_wid_2,color_code_wid_2,colormap_wid2,xlim_wid,ylim_wid,traj_alpha_wid] = traj_wid_dict['tot_traj_wids']
    [param_module_wid,param_hist_num_wid,param_box_num_wid,param_couple_num_wid,tparam_hist_num_wid,tparam_box_num_wid,tparam_couple_num_wid] = traj_wid_dict['param_wids']
    [MSD_module_wid,MSD_mode_wid,all_MSD_plot_wid,single_MSD_plot_wid,logplot_wid_x,logplot_wid_y,alpha_wid,MSD_wid,dim_wid,fitrange_wid] = traj_wid_dict['MSD_wids']
    [vor_module_wid,vor_show_axis_wid,vor_bkg_wid,vor_plot_wid,vor_linewidth_wid,vor_area_wid,vor_area_thr_wid,vor_cmap_wid,vor_vmin_bool_wid,vor_vmin_val_wid,vor_vmax_bool_wid,vor_vmax_val_wid,inc_wid_vor] = traj_wid_dict['vor_wids']
    [param_hist_wid_list,tparam_hist_wid_list] = param_plot_widgets_dict['hist']
    [boxplot_wid,swarmplot_wid,ttest_wid,param_box_wid_list,hue_box_wid_list,huecmap_box_wid_list,tparam_box_wid_list,t_hue_box_wid_list,t_huecmap_box_wid_list,t_row_list,t_boxplot_wid,t_swarmplot_wid,t_ttest_wid] = param_plot_widgets_dict['box']
    [xparam_wid_list,yparam_wid_list,hue_param_wid_list,cmap_param_wid_list,t_xparam_wid_list,t_yparam_wid_list,t_hue_param_wid_list,t_cmap_param_wid_list,scatter_wid,reg_wid,ci_wid,xbin_wid,xbin_num_wid] = param_plot_widgets_dict['scatter']
    
    # get MSD parameters
    if not MSD_module_wid.value:
        MSD_fit = False
    else:
        if MSD_mode_wid.value == 'only plot MSD':
            MSD_fit = None
        else:
            MSD_model_dict = {'random walk': 'pure_diff', 'biased random walk': 'biased_diff',
                            'persistent random walk': 'PRW'}
            MSD_fit = MSD_model_dict[MSD_wid.value]

    # Initialize config
    traj_config = tpr.make_traj_config(export_config=False)

    #traj_config_
    traj_config["traj_config_"]["run"] = traj_module_wid.value
    traj_config["traj_config_"]["color_code"] = color_code_wid.value
    traj_config["traj_config_"]["cmap"] = colormap_wid.value
    traj_config["traj_config_"]["lab_size"] = lab_size_wid.value
    traj_config["traj_config_"]["size_factor"] = marker_size_wid.value
    traj_config["traj_config_"]["show_tail"] = show_tail_wid.value
    traj_config["traj_config_"]["hide_labels"] = hide_lab_wid.value
    traj_config["traj_config_"]["no_bkg"] = bkg_wid.value
    traj_config["traj_config_"]["show_axis"] = show_axis_wid.value
    traj_config["traj_config_"]["increment"] = inc_wid.value

    #total_traj_config
    traj_config["total_traj_config"]["run"] = all_traj_module_wid.value
    traj_config["total_traj_config"]["color_code"] = 'none' if color_code_wid_2.value=='unique' else color_code_wid_2.value
    traj_config["total_traj_config"]["cmap"] = colormap_wid2.value
    traj_config["total_traj_config"]["lab_size"] = lab_size_wid_2.value
    traj_config["total_traj_config"]["center_origin"] = center_wid.value
    traj_config["total_traj_config"]["hide_labels"] = hide_lab_wid_2.value
    traj_config["total_traj_config"]["set_axis_lim"] = xlim_wid.value+ylim_wid.value if setlim_wid.value else None
    traj_config["total_traj_config"]["equal_axis"] = equal_axis_wid.value
    traj_config["total_traj_config"]["transparency"] = traj_alpha_wid.value

    # hist_config, boxplot, and scatter_config 
    plot_param_hist_ = []
    plot_t_param_hist_ = []
    plot_param_box_ = []
    plot_param_box_hue = []
    plot_param_box_cmap = []
    plot_t_param_box_ = []
    plot_t_param_box_hue = []
    plot_t_param_box_cmap = []
    plot_param_vs_param_ = []
    plot_param_vs_param_hue = []
    plot_param_vs_param_cmap = []
    plot_track_param_vs_param_ = []
    plot_track_param_vs_param_hue = []
    plot_track_param_vs_param_cmap = []

    if param_module_wid.value:
        for i in range(param_hist_num_wid.value):
            plot_param_hist_.append(param_hist_wid_list[i].value)
        for i in range(tparam_hist_num_wid.value):
            plot_t_param_hist_.append(tparam_hist_wid_list[i].value)
        for i in range(param_box_num_wid.value):
            plot_param_box_.append(param_box_wid_list[i].value)
            plot_param_box_hue.append(hue_box_wid_list[i].value)
            plot_param_box_cmap.append(huecmap_box_wid_list[i].value)
        for i in range(tparam_box_num_wid.value):
            plot_t_param_box_.append(tparam_box_wid_list[i].value)
            plot_t_param_box_hue.append(t_hue_box_wid_list[i].value)
            plot_t_param_box_cmap.append(t_huecmap_box_wid_list[i].value)
        for i in range(param_couple_num_wid.value):
            plot_param_vs_param_.append([xparam_wid_list[i].value,yparam_wid_list[i].value])
            plot_param_vs_param_hue.append(hue_param_wid_list[i].value)
            plot_param_vs_param_cmap.append(cmap_param_wid_list[i].value)
        for i in range(tparam_couple_num_wid.value):
            plot_track_param_vs_param_.append([t_xparam_wid_list[i].value,t_yparam_wid_list[i].value])   
            plot_track_param_vs_param_hue.append(t_hue_param_wid_list[i].value)
            plot_track_param_vs_param_cmap.append(t_cmap_param_wid_list[i].value)
            
    if len(plot_param_hist_)>0 or len(plot_t_param_hist_)>0:
        traj_config["hist_config"]["run"] = True
        traj_config["hist_config"]["var_list"] = plot_param_hist_
        traj_config["hist_config"]["mean_var_list"] = plot_t_param_hist_

    else: 
        traj_config["hist_config"]["run"] = False
        
    if len(plot_param_box_)>0 or len(plot_t_param_box_)>0:
        traj_config["boxplot_config"]["run"] = True
        traj_config["boxplot_config"]["var_list"] = plot_param_box_
        traj_config["boxplot_config"]["hue_var_list"] = plot_param_box_hue
        traj_config["boxplot_config"]["hue_cmap_list"] = plot_param_box_cmap
        traj_config["boxplot_config"]["save_stat"] = ttest_wid.value
        traj_config["boxplot_config"]["boxplot"] = boxplot_wid.value
        traj_config["boxplot_config"]["swarmplot"] = swarmplot_wid.value
        traj_config["boxplot_config"]["mean_var_list"] = plot_t_param_box_
        traj_config["boxplot_config"]["mean_hue_var_list"] = plot_t_param_box_hue
        traj_config["boxplot_config"]["mean_hue_cmap_list"] = plot_t_param_box_cmap
        traj_config["boxplot_config"]["mean_save_stat"] = t_ttest_wid.value
        traj_config["boxplot_config"]["mean_boxplot"] = t_boxplot_wid.value
        traj_config["boxplot_config"]["mean_swarmplot"] = t_swarmplot_wid.value
        
    else: 
        traj_config["boxplot_config"]["run"] = False
        
    if len(plot_param_vs_param_)>0 or len(plot_track_param_vs_param_)>0:
        traj_config["scatter_config"]["run"] = True
        traj_config["scatter_config"]["couple_list"] = plot_param_vs_param_
        traj_config["scatter_config"]["hue_var_list"] = plot_param_vs_param_hue
        traj_config["scatter_config"]["hue_cmap_list"] = plot_param_vs_param_cmap
        traj_config["scatter_config"]["mean_couple_list"] = plot_track_param_vs_param_
        traj_config["scatter_config"]["mean_hue_var_list"] = plot_track_param_vs_param_hue
        traj_config["scatter_config"]["mean_hue_cmap_list"] = plot_track_param_vs_param_cmap
        traj_config["scatter_config"]["ci"] = ci_wid.value
        traj_config["scatter_config"]["fit_reg"] = reg_wid.value
        traj_config["scatter_config"]["scatter"] = scatter_wid.value
        traj_config["scatter_config"]["x_bin_num"] = xbin_num_wid.value if xbin_wid.value else None
    else: 
        traj_config["scatter_config"]["run"] = False
            
    # MSD_config
    traj_config["MSD_config"]["run"] = MSD_module_wid.value
    traj_config["MSD_config"]["MSD_model"] = MSD_fit
    traj_config["MSD_config"]["dim"] = 2 if dim_wid.value == '2D' else 3
    traj_config["MSD_config"]["fitrange"] = [None,fitrange_wid.value]
    traj_config["MSD_config"]["plot_all_MSD"] = all_MSD_plot_wid.value
    traj_config["MSD_config"]["plot_single_MSD"] = single_MSD_plot_wid.value
    traj_config["MSD_config"]["logplot_x"] = logplot_wid_x.value
    traj_config["MSD_config"]["logplot_y"] = logplot_wid_y.value
    traj_config["MSD_config"]["alpha"] = alpha_wid.value

    # Voronoi_config
    vlim = [None, None]
    if vor_vmin_bool_wid.value: 
        vlim[0] = vor_vmin_val_wid.value
    if vor_vmax_bool_wid.value: 
        vlim[1] = vor_vmax_val_wid.value
    traj_config["voronoi_config"]["run"] = vor_module_wid.value
    traj_config["voronoi_config"]["plot"] = vor_plot_wid.value
    traj_config["voronoi_config"]["vlim"] = vlim 
    traj_config["voronoi_config"]["cmap"] = vor_cmap_wid.value
    traj_config["voronoi_config"]["compute_local_area"] = vor_module_wid.value # compute by default if module run
    traj_config["voronoi_config"]["show_local_area"] = vor_area_wid.value
    traj_config["voronoi_config"]["area_threshold"] = vor_area_thr_wid.value
    traj_config["voronoi_config"]["no_bkg"] = vor_bkg_wid.value
    traj_config["voronoi_config"]["show_axis"] = vor_show_axis_wid.value
    traj_config["voronoi_config"]["line_width"] = vor_linewidth_wid.value
    traj_config["voronoi_config"]["increment"] = inc_wid_vor.value

    return traj_config


def make_map_widgets(data_dir,data,custom_var):
    """
    Make widgets for map plotting
    """ 
    # default colormaps
    colormap_list = ['plasma', 'viridis', 'jet', 'bwr', 'bwr_r']  

    # unpack necessary data
    df = data['df']
    dim = data['dim']

    # 1. Make grid
    info = tpr.get_info(data_dir)
    w = info['image_width']
    h = info['image_height']
    image_aspect_ratio = h / w
    lengthscale = info['lengthscale']
    orig_list = ['center', "left-bottom", "center-bottom", "right-bottom", "right-center", "right-top", "center-top",
                "left-top", "left-center"]  # options to position the grid

    # number of cells along x axis
    x_num_wid = widgets.BoundedIntText(value=10, min=1, max=1000, description='Number of cells along x axis:',style={'description_width': 'initial'})

    # interactive output to display cell size
    def calc_cell_size(x_num_wid):
        """
        Calculate cell size based on number of cells
        """
        y_num = int(x_num_wid * image_aspect_ratio)
        cell_size = w / (x_num_wid + 1)
        cell_size_scaled = (w * lengthscale) / (x_num_wid + 1)
        printmd("""Number of cells along y axis: {}  
                Cell size: {:.2f} px ({:.2f} {})""".format(y_num,cell_size,cell_size_scaled,info['length_unit']))
        #printmd('Cell size: {:.2f} (px)'.format(cell_size))
        #printmd('Cell size: {:.2f} ({})'.format(cell_size_scaled,info['length_unit']))

    output_size = widgets.interactive_output(calc_cell_size, {'x_num_wid': x_num_wid})

    # position of the grid
    orig_wid = widgets.Dropdown(options=orig_list, value='center', description='Grid origin: ',
                                style={'description_width': 'initial'})

    # button to plot grid
    plot_grid_wid = widgets.Button(value=True, description='Show grid')
    output_plot = widgets.Output(value=True, description='Show grid')

    def btn_eventhandler(b):
        with output_plot:
            info = tpr.get_info(data_dir)
            image_size = [info['image_width'], info['image_height']]
            tpr.make_grid(image_size, x_num=x_num_wid.value, origin=orig_wid.value, plot_grid=True)
            plt.show()

    plot_grid_wid.on_click(btn_eventhandler)

    # layout
    grid_1 = GridspecLayout(2, 2)
    left = [x_num_wid, output_size]
    right = [orig_wid, plot_grid_wid]
    for i in range(2):
        grid_1[i,0] = left[i]
        grid_1[i,1] = right[i]
    tab_1 = VBox([grid_1,output_plot])

    # 2. Map params
    temp_avg_wid = widgets.BoundedIntText(value=0, min=0, max=100, description='Temporal average:',
                                        style={'description_width': 'initial'})
    arrow_size_wid = widgets.BoundedFloatText(value=1., min=0, max=100, description='Relative size of arrows:',
                                            style={'description_width': 'initial'})
    export_wid = widgets.Checkbox(value=True, description='export fields')
    bkg_wid = widgets.Checkbox(value=False, description='hide background image')
    show_axes_wid = widgets.Checkbox(value=False, description='show axes')
    inc_wid = widgets.BoundedIntText(value=1, min=1, max=df['frame'].max(), description='Plotting frame increment:',
                                        style={'description_width': 'initial'})

    # layout
    grid_2 = GridspecLayout(3, 2)
    left = [temp_avg_wid, arrow_size_wid,inc_wid]
    right = [bkg_wid, export_wid,show_axes_wid]
    for i in range(3):
        grid_2[i, 0] = left[i]
        grid_2[i, 1] = right[i]

    # 3. Scalar fields
    scalar_fields = ['vx', 'vy', 'vz', 'v', 'ax', 'ay', 'az', 'a', 'div', 'curl'] if dim == 3 else [
        'vx', 'vy', 'v', 'ax', 'ay', 'a', 'div', 'curl']
    scalar_fields = scalar_fields + list(custom_var.keys())
    left_3 = [Label('Field to plot',layout=Layout(width='200px'))]
    center_l_3 = [Label('Plotting limits',layout=Layout(width='300px'))]
    center_r_3 = [Label('Use custom limits',layout=Layout(width='200px'))]
    right_3 = [Label('Color map',layout=Layout(width='200px'))]

    scalar_wid_dict = {}  # to store widgets

    for i, f in enumerate(scalar_fields):
        if f in ['div', 'curl', 'v_mean', 'a_mean']:
            vlim = [-1e4, 1e4]
            vlim_min = vlim[0]
            vlim_max = vlim[1]
        else:
            vlim = [df[f].min(), df[f].max()]
            vlim_min = vlim[0] - np.abs(vlim[1] - vlim[0])
            vlim_max = vlim[1] + np.abs(vlim[1] - vlim[0])
        
        if f == 'div':
            cmap = 'bwr_r'
        elif f == 'curl':
            cmap = 'bwr'
        else: 
            cmap = 'plasma'

        run_wid = widgets.ToggleButton(value=True, description=f,layout=Layout(width='200px'))
        vlim_wid = widgets.FloatRangeSlider(value=vlim, min=vlim_min, max=vlim_max,layout=Layout(width='300px'))
        vlim_tick_wid = widgets.Checkbox(value=False,layout=Layout(width='200px'))
        cmap_wid = widgets.Dropdown(options=colormap_list, value=cmap,layout=Layout(width='200px'))

        # store widgets
        scalar_wid_dict[f] = [run_wid,vlim_wid,vlim_tick_wid,cmap_wid]

        # append to lists to display
        left_3.append(run_wid)
        center_l_3.append(vlim_wid)
        center_r_3.append(vlim_tick_wid)
        right_3.append(cmap_wid)

    box_3 = AppLayout(header=None,
                    left_sidebar=VBox(left_3),
                    center=HBox([VBox(center_l_3), VBox(center_r_3)]),
                    right_sidebar=VBox(right_3),
                    pane_widths=[1, 2.5, 1],
                    footer=None)

    # 4. Vector fields
    scalar_fields_ = ['none'] + scalar_fields
    vector_fields = ['v', 'a']
    vf_4 = [Label('Vector field to plot',layout=Layout(width='150px'))]
    sf_4 = [Label('plot on scalar field',layout=Layout(width='150px'))]
    vl_4 = [Label('Plotting limits',layout=Layout(width='200px'))]
    vl_tick_4 = [Label('Use custom limits',layout=Layout(width='150px'))]
    cm_4 = [Label('Color map',layout=Layout(width='150px'))]

    vector_wid_dict = {}  # to store widgets

    for i, f in enumerate(vector_fields):
        vlim = [df[f].min(), df[f].max()]
        vlim_min = vlim[0] - np.abs(vlim[1] - vlim[0])
        vlim_max = vlim[1] + np.abs(vlim[1] - vlim[0])

        run_wid = widgets.ToggleButton(value=True, description=f,layout=Layout(width='150px'))
        plot_on_wid = widgets.Dropdown(options=scalar_fields_, value=f,layout=Layout(width='150px'))
        vlim_wid = widgets.FloatRangeSlider(value=vlim, min=vlim_min, max=vlim_max,layout=Layout(width='200px'))
        vlim_tick_wid = widgets.Checkbox(value=False,layout=Layout(width='150px'))
        cmap_wid = widgets.Dropdown(options=colormap_list, value='plasma',layout=Layout(width='150px'))

        # store widgets
        vector_wid_dict[f] = [run_wid,plot_on_wid,vlim_wid,vlim_tick_wid,cmap_wid]

        # append to lists to display
        vf_4.append(run_wid)
        sf_4.append(plot_on_wid)
        vl_4.append(vlim_wid)
        vl_tick_4.append(vlim_tick_wid)
        cm_4.append(cmap_wid)


    def update_v_by_on_map_wid(*args):
        f = sf_4[1].value
        if f in ['div', 'curl', 'v_mean', 'a_mean']:
            vlim = [-1e4, 1e4]
            vlim_min = vlim[0]
            vlim_max = vlim[1]
            disabled = True
        else:
            vlim = [df[f].min(), df[f].max()]
            vlim_min = vlim[0] - np.abs(vlim[1] - vlim[0])
            vlim_max = vlim[1] + np.abs(vlim[1] - vlim[0])
            disabled = False
        if f == 'div':
            cmap = 'bwr_r'
        elif f == 'curl':
            cmap = 'bwr'
        else: 
            cmap = 'plasma'
        vl_4[1].value = vlim
        vl_4[1].min = vlim_min
        vl_4[1].max = vlim_max
        cm_4[1].value = cmap


    def update_a_by_on_map_wid(*args):
        f = sf_4[2].value
        if f in ['div', 'curl', 'v_mean', 'a_mean']:
            vlim = [-1e4, 1e4]
            vlim_min = vlim[0]
            vlim_max = vlim[1]
            disabled = True
        else:
            vlim = [df[f].min(), df[f].max()]
            vlim_min = vlim[0] - np.abs(vlim[1] - vlim[0])
            vlim_max = vlim[1] + np.abs(vlim[1] - vlim[0])
            disabled = False
        if f == 'div':
            cmap = 'bwr_r'
        elif f == 'curl':
            cmap = 'bwr'
        else: 
            cmap = 'plasma'
        vl_4[2].value = vlim
        vl_4[2].min = vlim_min
        vl_4[2].max = vlim_max
        cm_4[2].value = cmap


    sf_4[1].observe(update_v_by_on_map_wid, names='value')
    sf_4[2].observe(update_a_by_on_map_wid, names='value')

    box_4 = AppLayout(header=None,
                    left_sidebar=VBox(vf_4),
                    center=HBox([VBox(sf_4), VBox(vl_4)]),
                    right_sidebar=HBox([VBox(vl_tick_4), VBox(cm_4)]),
                    pane_widths=[1, 3, 2],
                    footer=None)

    # 5. Vector mean
    vector_fields = ['v', 'a']
    fields_5 = [Label('Field to average',layout=Layout(width='150px'))]
    dim_5 = [Label('Dimensions to average',layout=Layout(width='150px'))]
    vlim_5 = [Label('Plotting limits',layout=Layout(width='200px'))]
    vl_tick_5 = [Label('Use custom limits',layout=Layout(width='150px'))]
    cmap_5 = [Label('Color map',layout=Layout(width='150px'))]

    vmean_wid_dict = {}  # to store widgets

    for i, f in enumerate(vector_fields):
        cmap = 'plasma'
        vlim = [df[f].min(), df[f].max()]
        vlim_min = vlim[0] - np.abs(vlim[1] - vlim[0])
        vlim_max = vlim[1] + np.abs(vlim[1] - vlim[0])

        run_wid = widgets.ToggleButton(value=True, description=f,layout=Layout(width='150px'))
        dim_wid = widgets.Dropdown(options=[('x,y,z', ['x', 'y', 'z']),
                                                    ('x,y', ['x', 'y']),
                                                    ('x,z', ['x', 'z']),
                                                    ('y,z', ['y', 'z'])],
                                            value=['x', 'y', 'z'],layout=Layout(width='150px'))
        vlim_wid = widgets.FloatRangeSlider(value=vlim, min=vlim_min, max=vlim_max,layout=Layout(width='200px'))
        vlim_tick_wid = widgets.Checkbox(value=False,layout=Layout(width='150px'))
        cmap_wid = widgets.Dropdown(options=colormap_list, value=cmap,layout=Layout(width='150px'))

        # store widgets
        vmean_wid_dict[f] = [run_wid,dim_wid,vlim_wid,vlim_tick_wid,cmap_wid]

        # append to lists to display

        fields_5.append(run_wid)
        dim_5.append(dim_wid)
        vlim_5.append(vlim_wid)
        vl_tick_5.append(vlim_tick_wid)
        cmap_5.append(cmap_wid)

    box_5 = AppLayout(header=None,
                    left_sidebar=VBox(fields_5),
                    center=HBox([VBox(dim_5),VBox(vlim_5)]),
                    right_sidebar=HBox([VBox(vl_tick_5), VBox(cmap_5)]),
                    pane_widths=[1, 2, 2],
                    footer=None)

    # layout
    accordion = widgets.Accordion(children=[box_3, box_4, box_5])
    acc_titles = ['Scalar fields', 'Vector fields', 'Vector mean']
    for i in range(len(acc_titles)):
        accordion.set_title(i, acc_titles[i])

    tab_titles = ['Make grids', 'Map parameters', 'Fields to plot']
    tab = widgets.Tab()
    tab.children = [tab_1, grid_2, accordion]
    for i in range(len(tab_titles)):
        tab.set_title(i, tab_titles[i])

    display(tab)

    map_widgets_dict = {
        'grid': [x_num_wid, orig_wid],
        'map': [temp_avg_wid, arrow_size_wid, export_wid, bkg_wid, show_axes_wid, inc_wid],
        'scalar': scalar_wid_dict,
        'vector': vector_wid_dict,
        'vmean': vmean_wid_dict,
    }

    return map_widgets_dict


def retrieve_map_param_widgets(map_widgets_dict):
    """
    Retrieve map widgets values
    """

    # Unpack widgets dict
    [x_num_wid, orig_wid] = map_widgets_dict['grid']
    [temp_avg_wid, arrow_size_wid, export_wid, bkg_wid, show_axes_wid, inc_wid] = map_widgets_dict['map']
    scalar_wid_dict = map_widgets_dict['scalar']
    vector_wid_dict = map_widgets_dict['vector']
    vmean_wid_dict = map_widgets_dict['vmean']

    # Prepare config
    map_config = tpr.make_map_config(export_config=False)

    # grid_param
    map_config["grid_param"] = {'x_num':x_num_wid.value, #use only
                                'y_num':None,
                                'cell_size':None,
                                'scaled':False,
                                'origin':orig_wid.value,
                                'plot_grid':False}

    # map_param
    map_config["map_param"]["no_bkg"] = bkg_wid.value
    map_config["map_param"]["size_factor"] = arrow_size_wid.value
    map_config["map_param"]["export_field"] = export_wid.value
    map_config["map_param"]["temporal_average"] = temp_avg_wid.value
    map_config["map_param"]["show_axis"] = show_axes_wid.value
    map_config["map_param"]["increment"] = inc_wid.value

    # scalar_fields
    scalar_fields_dict={}
    for f in scalar_wid_dict.keys():
        if scalar_wid_dict[f][0].value:
            vlim = scalar_wid_dict[f][1].value if scalar_wid_dict[f][2].value else None
            scalar_fields_dict[f]={'vlim':vlim,'cmap':scalar_wid_dict[f][3].value}
    map_config["scalar_fields"] = scalar_fields_dict
            
    #4. vector_fields
    vector_fields_dict={}
    for f in vector_wid_dict.keys():
        if vector_wid_dict[f][0].value:
            plot_on = vector_wid_dict[f][1].value
            vlim = vector_wid_dict[f][2].value if vector_wid_dict[f][3].value else None
            vector_fields_dict[f]={'plot_on':plot_on,'vlim':vlim,'cmap':vector_wid_dict[f][4].value}
    map_config["vector_fields"] = vector_fields_dict
            
    #5. vector_mean
    vector_mean_dict={}
    for f in vmean_wid_dict.keys():
        if vmean_wid_dict[f][0].value:
            dimensions = vmean_wid_dict[f][1].value
            vlim = vmean_wid_dict[f][2].value if vmean_wid_dict[f][3].value else None
            vector_mean_dict[f]={'dimensions':dimensions,'vlim':vlim,'cmap':vmean_wid_dict[f][4].value}
    map_config["vector_mean"] = vector_mean_dict

    return map_config


def make_folder_widgets(init_dir, dataset_num):
    """
    Make widgets to get datasets paths and names
    """

    # help message
    printmd("**For each dataset, select the trajectory analysis folder (containing the files all_data.csv and mean_track_data.csv) and, optionally, give  a name to the dataset.**")

    # choose datasets folders
    fc_list=[]
    name_wid_list=[]
    rows=[]

    for i in range(dataset_num):
        lab = widgets.Label("Dataset #{}".format(i))
        fc_data = FileChooser(init_dir)
        fc_data.use_dir_icons = True
        fc_data.title = 'Choose the dataset folder'
        fc_list.append(fc_data)
        name=widgets.Text(value='',placeholder='optional',description='Dataset name:',style={'description_width': 'initial'})
        name_wid_list.append(name)
        rows.append(HBox([lab,fc_data,name]))
        
    display(VBox(rows))
    
    return fc_list,name_wid_list

def make_number_analysis_widgets(dataset_num,fc_list=None,data_dir_list=None,name_wid_list=None,name_list=None):
    """
    Make widgets to get the number of analyses to compare
    dataset paths and names can be passed by a list of widgets or directly as a list of paths and names
    data_dir_list and name_list must be passed together instead of fc_list and name_wid_list
    """

    # get datasets
    if data_dir_list is not None and name_list is not None:
        pass
    else:
        data_dir_list = []
        name_list = []
        for i in range(dataset_num):
            data_dir_ = fc_list[i].selected_path  # allow use to use a list of path instead of the file chooser
            if data_dir_ is None:
                continue
            else:
                name = name_wid_list[i].value
                if name == '':
                    name = osp.split(data_dir_)[1]
                data_dir_list.append(data_dir_)
                name_list.append(name)
            
    # datadir is the datadir of the first dataset
    data_dir = osp.sep.join(data_dir_list[0].split(osp.sep)[:-2]) #the main dir is two levels up
    if not osp.exists(osp.join(data_dir,'info.txt')): 
        raise Exception("""ERROR: your first dataset root directory doesn't contain an info file, which is required. Aborting...\n
        root director: {}""".format(data_dir))

    # number of plot kinds
    printmd("**Parameters plotting section**")
    printmd("You can plot histograms or boxplots of single parameters or scatter plots of a couple of parameters (e.g. v vs y)")
    param_module_wid = widgets.ToggleButton(value=True,description='Run module')
    display(param_module_wid)

    printmd("How many instantaneous parameters (histogram or couples) do you want to plot? (enter 0 if you don't want to plot parameters)")
    param_hist_num_wid = widgets.BoundedIntText(value=1,min=0,max=10,description='Number of histograms:',style={'description_width': 'initial'})
    param_box_num_wid = widgets.BoundedIntText(value=1,min=0,max=10,description='Number of boxplots:',style={'description_width': 'initial'})
    param_couple_num_wid = widgets.BoundedIntText(value=1,min=0,max=10,description='Number of couples:',style={'description_width': 'initial'})
    display(HBox([param_hist_num_wid,param_box_num_wid,param_couple_num_wid]))

    printmd("How many whole-trajectory parameters (histogram or couples) do you want to plot? (enter 0 if you don't want to plot parameters)")
    tparam_hist_num_wid = widgets.BoundedIntText(value=1,min=0,max=10,description='Number of histograms:',style={'description_width': 'initial'})
    tparam_box_num_wid = widgets.BoundedIntText(value=1,min=0,max=10,description='Number of boxplots:',style={'description_width': 'initial'})
    tparam_couple_num_wid = widgets.BoundedIntText(value=1,min=0,max=10,description='Number of scatter plots:',style={'description_width': 'initial'})
    display(HBox([tparam_hist_num_wid,tparam_box_num_wid,tparam_couple_num_wid]))

    printmd("***")
    printmd("**MSD section**")
    MSD_plot_wid = widgets.ToggleButton(value=True,description='plot MSD')
    logplot_wid_x = widgets.Checkbox(value=True,description='x axis')
    logplot_wid_y = widgets.Checkbox(value=True,description='y axis')
    alpha_lab = Label('For all MSD plots, set the transparency (0=transparent, 1=opaque)')
    alpha_wid = widgets.FloatSlider(value=0.2,min=0,max=1,steps=0.01,description='transparency',style={'description_width': 'initial'})
    display(MSD_plot_wid)
    display(HBox([Label('log plot: '),logplot_wid_x,logplot_wid_y]))
    display(HBox([alpha_lab,alpha_wid]))

    dataset_wid_dict = {
        'data_dir': data_dir,
        'data_dir_list': data_dir_list,
        'name_list': name_list,
        'param_wid_list': [param_module_wid,param_hist_num_wid,param_box_num_wid,param_couple_num_wid,tparam_hist_num_wid,tparam_box_num_wid,tparam_couple_num_wid],
        'MSD_wid_list': [MSD_plot_wid,logplot_wid_x,logplot_wid_y,alpha_wid],
        }
    
    return dataset_wid_dict

def make_comp_widgets(dataset_wid_dict):
    """
    Make widgets for datasets comparison
    """

    # unpack widgets values
    data_dir_list = dataset_wid_dict['data_dir_list']
    [param_module_wid,param_hist_num_wid,param_box_num_wid,param_couple_num_wid,tparam_hist_num_wid,tparam_box_num_wid,tparam_couple_num_wid] = dataset_wid_dict['param_wid_list']
    [MSD_plot_wid,logplot_wid_x,logplot_wid_y,alpha_wid] = dataset_wid_dict['MSD_wid_list']

    # get and pool datasets
    df_list = []
    track_df_list = []
    MSD_df_list = []
    for d in data_dir_list:
        # df
        df_fn = osp.join(d, 'all_data.csv')
        df = pd.read_csv(df_fn, index_col=0) if osp.exists(df_fn) else None
        df_list.append(df)

        # track_df
        df_fn = osp.join(d, 'mean_track_data.csv')
        df = pd.read_csv(df_fn, index_col=0) if osp.exists(df_fn) else None
        track_df_list.append(df)

        # MSD_df
        df_fn = osp.join(d, 'all_MSD.csv')
        df = pd.read_csv(df_fn, index_col=0) if osp.exists(df_fn) else None
        MSD_df_list.append(df)

    # retrieve MSD widgets values
    if not MSD_plot_wid.value:
        MSD_plot_param = None
    else:
        MSD_plot_param = {
            'logplot_x':logplot_wid_x.value,
            'logplot_y':logplot_wid_y.value,
            'alpha':alpha_wid.value,
            'xylim':[None,None,0.1,None]
            }

    # widgets for parameters plotting
    if param_module_wid.value:
        # prepare parameters lists
        if 'data' not in locals():
            data = tpr.get_data(dataset_wid_dict['data_dir'])

        dimensions = ['x', 'y'] if data['dim'] == 2 else ['x', 'y', 'z']
        scaled_dimensions = [dim+'_scaled' for dim in dimensions]
        vel = ['v'+dim for dim in dimensions]
        acc = ['a'+dim for dim in dimensions]

        params = ['track', 't'] + dimensions + scaled_dimensions + vel + acc + ['v', 'a', 'area']

        # get whole_track param
        params_track = []
        for data_dir_ in data_dir_list:
            fn = osp.join(data_dir_, 'mean_track_data.csv')
            if not osp.exists(fn):
                raise Exception("ERROR: No data to compare in {}. Aborting...".format(data_dir_))
            df_prop = pd.read_csv(fn, index_col=0)
            params_track = params_track + list(df_prop.columns)
        params_track = list(set(params_track))

        # hist
        kde_wid = widgets.Checkbox(value=True, description='kde')
        hist_wid = widgets.Checkbox(value=True, description='hist')
        kde_t_wid = widgets.Checkbox(value=True, description='kde')
        hist_t_wid = widgets.Checkbox(value=True, description='hist')

        param_hist_wid_list = []
        tparam_hist_wid_list = []
        for i in range(param_hist_num_wid.value):
            w = widgets.Dropdown(options=params, value='v', description='parameter', style={'description_width': 'initial'})
            param_hist_wid_list.append(w)
        box_1 = HBox([VBox(param_hist_wid_list), VBox([widgets.Label('Plotting parameters'), kde_wid, hist_wid])])
        for i in range(tparam_hist_num_wid.value):
            w = widgets.Dropdown(options=params_track, value='v', description='parameter', style={'description_width': 'initial'})
            tparam_hist_wid_list.append(w)
        box_2 = HBox([VBox(tparam_hist_wid_list), VBox([widgets.Label('Plotting parameters'), kde_t_wid, hist_t_wid])])

        # boxplots
        swarm_wid = widgets.Checkbox(value=False, description='swarmplot') # no swarmplot for instantaneous because often too many points
        boxplot_wid = widgets.Checkbox(value=True, description='boxplot')
        stat_wid = widgets.Checkbox(value=True, description='run ttest')
        swarm_t_wid = widgets.Checkbox(value=True, description='swarmplot')
        boxplot_t_wid = widgets.Checkbox(value=True, description='boxplot')
        stat_t_wid = widgets.Checkbox(value=True, description='run ttest')

        param_box_wid_list = []
        tparam_box_wid_list = []
        for i in range(param_box_num_wid.value):
            w = widgets.Dropdown(options=params, value='v', description='parameter', style={'description_width': 'initial'})
            param_box_wid_list.append(w)
        box_3 = HBox([VBox(param_box_wid_list), VBox([widgets.Label('Plotting parameters'), swarm_wid, boxplot_wid, stat_wid])])
        for i in range(tparam_box_num_wid.value):
            w = widgets.Dropdown(options=params_track, value='v', description='parameter', style={'description_width': 'initial'})
            tparam_box_wid_list.append(w)
        box_4 = HBox([VBox(tparam_box_wid_list), VBox([widgets.Label('Plotting parameters'), swarm_t_wid, boxplot_t_wid, stat_t_wid])])

        # couples
        xparam_wid_list = []
        yparam_wid_list = []
        for i in range(param_couple_num_wid.value):
            x = widgets.Dropdown(options=params, value='t', description='x parameter', style={'description_width': 'initial'})
            y = widgets.Dropdown(options=params, value='v', description='y parameter', style={'description_width': 'initial'})
            xparam_wid_list.append(x)
            yparam_wid_list.append(y)

        left5 = VBox(xparam_wid_list)
        right5 = VBox(yparam_wid_list)
        box_5 = HBox([left5, right5])

        t_xparam_wid_list = []
        t_yparam_wid_list = []
        for i in range(tparam_couple_num_wid.value):
            x = widgets.Dropdown(options=params_track, value='t', description='x parameter', style={'description_width': 'initial'})
            y = widgets.Dropdown(options=params_track, value='v', description='y parameter', style={'description_width': 'initial'})
            t_xparam_wid_list.append(x)
            t_yparam_wid_list.append(y)

        left6 = VBox(t_xparam_wid_list)
        right6 = VBox(t_yparam_wid_list)
        box_6 = HBox([left6, right6])

        acc1 = widgets.Accordion(children=[box_1, box_2],titles=('Instantaneous parameters','Whole_trajectory parameters'))
        acc2 = widgets.Accordion(children=[box_3, box_4],titles=('Instantaneous parameters','Whole_trajectory parameters'))
        acc3 = widgets.Accordion(children=[box_5, box_6],titles=('Instantaneous parameters','Whole_trajectory parameters'))

        tab_titles = ['Parameter histograms', 'Parameter boxplots', 'Parameter couples']
        tab = widgets.Tab()
        tab.children = [acc1, acc2, acc3]
        for i in range(len(tab_titles)):
            tab.set_title(i, tab_titles[i])
        display(tab)

    # store compare data
    compare_dict = {
        'df_list': df_list,
        'track_df_list': track_df_list,
        'MSD_df_list': MSD_df_list,
        'MSD_plot_param': MSD_plot_param,
        'hist_wids': [kde_wid,hist_wid,kde_t_wid,hist_t_wid,param_hist_wid_list,tparam_hist_wid_list],
        'boxplot_wids': [swarm_wid,boxplot_wid,stat_wid,swarm_t_wid,boxplot_t_wid,stat_t_wid,param_box_wid_list,tparam_box_wid_list],
        'couple_wids': [xparam_wid_list,yparam_wid_list,t_xparam_wid_list,t_yparam_wid_list]
    }

    return compare_dict

def retrieve_comp_widgets_values(compare_dict,dont_run=False):
    """
    Retrieve values from widgets
    """

    if not dont_run:
        # unpack widgets
        [kde_wid,hist_wid,kde_t_wid,hist_t_wid,param_hist_wid_list,tparam_hist_wid_list] = compare_dict['hist_wids']
        [swarm_wid,boxplot_wid,stat_wid,swarm_t_wid,boxplot_t_wid,stat_t_wid,param_box_wid_list,tparam_box_wid_list] = compare_dict['boxplot_wids']
        [xparam_wid_list,yparam_wid_list,t_xparam_wid_list,t_yparam_wid_list] = compare_dict['couple_wids']

        # retrieve values
        param_hist={'param':[],'hist':hist_wid.value,'kde':kde_wid.value}
        track_param_hist={'param':[],'hist':hist_t_wid.value,'kde':kde_t_wid.value}
        param_box={'param':[],'swarmplot':swarm_wid.value,'boxplot':boxplot_wid.value,'save_stat':stat_wid.value}
        track_param_box={'param':[],'swarmplot':swarm_t_wid.value,'boxplot':boxplot_t_wid.value,'save_stat':stat_t_wid.value}
        param_couples={'couples':[],'axis_lim':None}
        track_param_couples={'couples':[],'axis_lim':None}

        for i in range(len(param_hist_wid_list)):
            param_hist['param'].append(param_hist_wid_list[i].value)
        for i in range(len(tparam_hist_wid_list)):
            track_param_hist['param'].append(tparam_hist_wid_list[i].value)
        for i in range(len(param_box_wid_list)):
            param_box['param'].append(param_box_wid_list[i].value)
        for i in range(len(tparam_box_wid_list)):
            track_param_box['param'].append(tparam_box_wid_list[i].value)
        for i in range(len(xparam_wid_list)):
            param_couples['couples'].append((xparam_wid_list[i].value,yparam_wid_list[i].value))
        for i in range(len(t_xparam_wid_list)):
            track_param_couples['couples'].append((t_xparam_wid_list[i].value,t_yparam_wid_list[i].value))

    else: 
        param_couples,track_param_couples,param_hist,track_param_hist,param_box,track_param_box = [None,None,None,None,None,None]

    return param_couples,track_param_couples,param_hist,track_param_hist,param_box,track_param_box