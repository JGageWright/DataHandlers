import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
from data_structures import experiment
import os

Tk = tk.Tk()
Tk.withdraw()


def ask_path():
    return filedialog.asksaveasfile(mode='w').name

def df_to_excel(df, sheet_name='Sheet1'):
    '''
    Uses pandas to always return a .xlsx file of the given df
    Giving the save name a file extension results in multiple files being saved
    '''
    where = filedialog.asksaveasfile(mode='wb', filetypes=[('Microsoft Excel Worksheet', '.xlsx')],
                                     defaultextension='.xlsx')
    save_name = where.name
    if save_name[-5:] != '.xlsx':
        save_name = str(save_name + '.xlsx')
    with pd.ExcelWriter(save_name) as writer:
        df.to_excel(writer, engine='openpyxl', sheet_name=sheet_name)

def cary630(filename):
    '''
    Given path, shapes .CSV data output by
    Aligent's Cary 630 Spectrometer (managed by MicroLab)
    to a usable dataframe with integer index
    '''
    df = pd.read_csv(filename,
                       header=4,
                       names=['Wavenumber', 'Absorbance'])
    return df

def load_experiment(filetype: str = '.csv') -> experiment:
    '''
    :param filetype: .xlsx or .csv
    :return: experiment object

    Creates and experiment object for a previously exported experiment.
    If filetype = .xlsx, the excel file must have sheets named 'data' and 'params'

    If filetype = .csv, two CSVs in the selected folder must be named 'data' and 'params', respecitively
    '''
    if filetype == '.xlsx':
        file = filedialog.askopenfilename(filetypes=[('Excel Worksheet', '.xlsx')])
        x = pd.ExcelFile(file, engine='openpyxl')
        sheets = {}
        for sheet in x.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet, index_col=0)
            sheets[str(sheet)] = df

        data = sheets['data']
        del sheets['data']
        params = sheets['params']
        del sheets['params']

        opt = []
        for sheet in sheets.keys():
            opt.append(sheets[sheet])

        exp = experiment(data, params, opt)
        return exp
    elif filetype == '.csv':
        dirname = filedialog.askdirectory(title='Select a folder of CSV files')
        filenames = os.listdir(dirname)

        data = pd.read_csv(dirname+'/data.csv', index_col=0)
        params = pd.read_csv(dirname + '/params.csv', index_col=0)
        filenames.remove('data.csv')
        filenames.remove('params.csv')

        opt = []
        for file in filenames:
            opt.append(
                pd.read_csv(dirname+'/'+file, index_col=0)
                )
        exp = experiment(data, params, opt)
        return exp

def biologic_mpt_voltammetry(filename: str) -> pd.DataFrame:
    """
    :param filename: Path to .mpt file
    :return: dataframe of all data, sorted with relevant voltammetry columns first

    No idea if this works on all .mpt files.
    In principle, one function could be written with options to resort columns in various ways.
    impedance.py includes an impedance importer, so could use that one
    """
    # .mpt has a variable number of header lines, but it tells you how many on line 2
    with open(filename, 'r', encoding="latin-1") as input_file:
        lines = input_file.readlines()

    header_line = lines[1]
    num_header_lines = int(header_line.split(":")[1])
    headers = lines[num_header_lines-1].split('\t')[0:-1]
    data_lines = lines[num_header_lines:]

    # Make a dataframe with the data
    df = pd.DataFrame(data={}, columns=headers)
    for i in range(len(data_lines)):
        df.loc[len(df)] = data_lines[i].split('\t')
    aux_cols = df.columns.drop('Ewe/V').drop('<I>/mA').drop('time/s')
    df = df.reindex(columns=['Ewe/V', '<I>/mA', 'time/s', *aux_cols])

    # Convert text to numbers
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

    # Be extra sure cycle number is an integer
    df['cycle number'] = df['cycle number'].astype(np.int64)

    return df

# Testing df
# df = pd.DataFrame({
#     1: ['one', 'four', 'seven'],
#     2: ['two', 'five', 'eight'],
#     3: ['three', 'six', 'nine']
# }, index=[0, 1, 2])
#
# df_to_excel(df)