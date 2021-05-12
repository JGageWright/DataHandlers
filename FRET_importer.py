import pandas as pd
import numpy as np
import glob
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from tkinter import filedialog, messagebox
import tkinter as tk
from importer_snippets import episodic_to_dataframe, get_times, convert_times, get_folders

# root = tk.Tk()
# root.withdraw()
# folder_list = get_folders()
# print(folder_list)
folder_1 = r'C:/Users/jgage/OneDrive/Documents/Biosensor Files/FRET/MMP9/04062021 MMP9 Bulk/5'
folder_2 = r'C:/Users/jgage/OneDrive/Documents/Biosensor Files/FRET/MMP9/04062021 MMP9 Bulk/7 plus a half'
folder_3 = r'C:/Users/jgage/OneDrive/Documents/Biosensor Files/FRET/MMP9/04062021 MMP9 Bulk/10'
folder_4 = r'C:/Users/jgage/OneDrive/Documents/Biosensor Files/FRET/MMP9/03152021 MMP9 Bulk/15'
folder_5 = r'C:/Users/jgage/OneDrive/Documents/Biosensor Files/FRET/MMP9/03152021 MMP9 Bulk/20'
folder_6 = r'C:/Users/jgage/OneDrive/Documents/Biosensor Files/FRET/MMP9/03152021 MMP9 Bulk/30'
folder_7 = r'C:/Users/jgage/OneDrive/Documents/Biosensor Files/FRET/MMP9/03152021 MMP9 Bulk/50'
folder_list = [folder_1, folder_2, folder_3, folder_4, folder_5, folder_6, folder_7]

'''
Import several folders of episodic data, with the assumption that the data are all the same shape (see episodic to dataframe fucntion)
essentially, all columns should be episode spectra
The data are imported into the dfl_list object (a list of DataFrame lists corresponding to each folder (concentration)
Each dfl in dfl_list has [params, raw, signal]
'''

# Get Params
params = pd.Series({'int_time': 3000,
                    'scans_avg': 10,
                    'min_delay': 0,
                    'ms_delay': 0
                    })

dfl5, dfl7_5, dfl10, dfl15, dfl20, dfl30, dfl50 = [], [], [], [], [], [], []
dfl_list = [dfl5, dfl7_5, dfl10, dfl15, dfl20, dfl30, dfl50]
for i in range(len(folder_list)):
    for filename in os.listdir(folder_list[i]):
        if filename.lower().endswith(".ep1x"):
            dfl_list[i].append([(params.append(pd.Series({'filename': filename}))),
                                episodic_to_dataframe(folder_list[i] + '/' + filename)])


def add_times(df):
    '''
    Puts times on top of dataframe
    '''
    num_episodes = len(df.columns)
    times_in_seconds = get_times(params, num_episodes)
    time_codes = convert_times(times_in_seconds)

    # Create a DataFrame that maps episodes to times. Just move this into import function for generality
    time_dict = {}
    name_dict = {}
    for i in range(num_episodes):
        time_dict[i] = [times_in_seconds[i], time_codes[i]]
        name_dict[i] = 'ep' + (str(i + 1))
    time_df = pd.DataFrame(data=time_dict,
                           index=['time (s)', 'H/M/S'], )
    time_df.rename(name_dict, inplace=True, axis=1)
    df = time_df.append(df, ignore_index=False)
    return df


# Put times at the top of each df in dfl_list
for i in range(len(dfl_list)):
    for j in range(len(dfl_list[i])):
        dfl_list[i][j][1] = add_times(dfl_list[i][j][1])

# Extract the signal
for i in range(len(dfl_list)):
    for j in range(len(dfl_list[i])):
        signal = dfl_list[i][j][1].iloc[569:578, :].mean(axis=0)
        if j == 0:
            dfl_list[i].append(signal.rename(('signal' + str(j + 1)), axis=1).to_frame())
        else:
            # dfl_list[i][-1]['signal' + str(j + 1)] = signal.rename(('signal' + str(j + 1)), axis = 1).to_frame()
            dfl_list[i][-1] = pd.concat([dfl_list[i][-1], signal.rename(('signal' + str(j + 1)), axis=1).to_frame()],
                                        axis=1, join='outer')

# Again assuming times are the same for each trial
# for i in range(len(dfl_list[:])):
#     dfl_list[i][-1]['time (s)'] = dfl_list[i][-2][1].loc['time (s)', :]


# ^^That assumption failed here...
for i in range(len(dfl_list[:])):
    dfl_list[i][-1]['time (s)'] = dfl_list[i][-2][1].loc['time (s)', :]
    # print('i:'+str(i), dfl_list[i][-1]['time (s)'])

# Make plots
def plot_reg_from_regl(regl, vol=False, name='Unnamed Figure', title=''):
    reg, reg_x, reg_y = regl[0], regl[1], regl[2]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(reg_x, reg_y, c='k', zorder=1)
    ax.plot(reg_x, reg.predict(reg_x), color='r', zorder=0.8)


def plot_run_spectra(data_df):
    data_df.drop(['time (s)', 'H/M/S'], axis=0, inplace=True)
    fig = plt.figure()
    ax = fig.add_subplot
    for spectrum in data_df.iteritems():
        ax.plot(data_df.index, data_df[spectrum])
    return fig


def plot_spectra(df, text='', save_name=''):
    # Plot conc, trial, 1=raw spectra. Omit first 10 wavelengths
    plt.style.use('seaborn-talk')
    fig, ax = plt.subplots()
    ax.set_ylabel('Intensity (Counts)', fontsize=20)
    ax.set_xlabel('Wavelength (nm)', fontsize=20)
    df.iloc[10:,:].plot(use_index=True, colormap='seismic', legend=False, ax=ax, linewidth=1)
    ax.text(.95, 0.85,
            text, font='arial',
            fontsize=16, horizontalalignment='right', transform=ax.transAxes)
    if save_name != '':
        fig.savefig('figs/'+str(save_name), dpi=600, pad_inches=0)
    return fig

def plot_run(df, text='', save_name=''):
    # Plot conc, trials (signal df) as signal vs. time
    plt.style.use('seaborn-talk')
    fig, ax = plt.subplots()
    for column in df.iloc[:,:-1].columns.to_list():
        ax.scatter(x=df['time (s)'], y=df[column], label=column)
        ax.legend()
        ax.text(.95, 0.05,
            text, font='arial',
            fontsize=14, verticalalignment='bottom', horizontalalignment='right', transform=ax.transAxes)
    ax.set_ylabel('Intensity (Counts)', fontsize=20)
    ax.set_xlabel('Time (s)', fontsize=20)
    if save_name != '':
        fig.savefig('figs/'+str(save_name), dpi=600, pad_inches=0)
    return fig

# plot_spectra(dfl15[0][1])