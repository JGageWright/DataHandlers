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


def load_experiment(filetype: str = '.csv', csv_dirname: str = None) -> experiment:
    '''
    :param filetype: .xlsx or .csv
    :return: experiment object

    Creates an experiment object for a previously exported experiment.
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
        if csv_dirname is None:
            dirname = filedialog.askdirectory(title='Select a folder of CSV files')
        else:
            dirname = csv_dirname
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


def biologic_mpt(path: str, technique: str=None, area: float=None) -> pd.DataFrame:
    """
    Should work for all .mpt files, tested on CV, CVA, CA, PEIS, ZIR.
    
    In principle, one function could be written with options to resort columns in various ways.
    impedance.py includes an impedance importer, so could use that one

    Args:
        path (str): Path to .mpt file
        technique (str, optional): Technique type. Defaults to None.
        area (float, optional): Electrode area for normalization in cm2. Defaults to None.

    Returns:
        pd.DataFrame: dataframe of all data, sorted with relevant columns first when applicable
    """
    
    # .mpt has a variable number of header lines, but it tells you how many on line 2
    with open(path, 'r', encoding="latin-1") as input_file:
        lines = input_file.readlines()

    header_line = lines[1]
    num_header_lines = int(header_line.split(":")[1])
    headers = lines[num_header_lines-1].split('\t')[0:-1]
    data_lines = lines[num_header_lines:]

    # Make a dataframe with the data
    df = pd.DataFrame(data={}, columns=headers)
    for i in range(len(data_lines)):
        df.loc[len(df)] = data_lines[i].split('\t')
        
    # Convert text to numbers
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass
    
    # Convert current to Amps (default mA) and compute current densities.
    df['<I>/A'] = df['<I>/mA'] / 1000
    
    if area is not None:
        df['j/A.cm-2'] = df['<I>/A'] / area
        df['j/mA.cm-2'] = df['j/A.cm-2'] * 1000
    
    # Sort more relevant columns first
    if technique in ['CVA', 'CV', 'CA']:
        aux_cols = df.columns.drop('Ewe/V').drop('<I>/mA').drop('time/s').drop('j/mA.cm-2')
        df = df.reindex(columns=['Ewe/V', '<I>/mA', 'j/mA.cm-2', 'time/s', *aux_cols])
        
        df['cycle number'] = df['cycle number'].astype(np.int64) # Be extra sure cycle number is an integer
        
        
    return df

def CHI_txt(path):
    """Converts CH Instuments .txt data into pandas Datarame

    Args:
        path (str): path to .txt file

    Raises:
        ValueError: if data cannot be converted to a numerical datatype

    Returns:
        pd.DataFrame: Dataframe containing all data after header
    """
    header = []
    with open(path, 'r') as ff:
        lines = ff.readlines()
        # date = lines[0]
        technique = lines[1].replace('\n', '')
        i = 1
        for line in lines[1:]: # First line always date with ,
            if ',' not in line:
                header.append(line)
                if line != '\n': # readlines counts blank lines, but pandas does not.
                    i += 1
            else:
                break
    df = pd.read_csv(path, header=i)
    df.columns = df.columns.str.replace(' ', '')
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            raise ValueError('Column could not be converted to numeric')
    
    
    if technique == 'A.C. Impedance':
        df.rename({r"Z'/ohm": 'Zre/ohm', 
                   r'Z"/ohm': 'Zim/ohm',
                   r"Z/ohm": 'Zmag/ohm'}, axis=1, inplace=True)
        df['Zcx/ohm'] = df['Zre/ohm'] + 1j*df['Zim/ohm']
        df['Angular_Freq'] = df['Freq/Hz']*2*np.pi
    return df


def CHI_txt_todict(path, dict):
    """Converts CH Instuments .txt data into pandas Datarame and appends to passed dictionary

    Args:
        path (str): path to .txt file
        dict (dict): dictionary to append df

    Raises:
        ValueError: ValueError: if data cannot be converted to a numerical datatype

    Returns:
        dict: Dictionary of dataframe with filepath keys. Dataframes contain all data after header
    """
    header = []
    with open(path, 'r') as ff:
        lines = ff.readlines()
        # date = lines[0]
        technique = lines[1].replace('\n', '')
        i = 1
        for line in lines[1:]: # First line always date with ,
            if ',' not in line:
                header.append(line)
                if line != '\n': # readlines counts blank lines, but pandas does not.
                    i += 1
            else:
                break
    df = pd.read_csv(path, header=i)
    df.columns = df.columns.str.replace(' ', '')
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            raise ValueError('Column could not be converted to numeric')
    
    
    if technique == 'A.C. Impedance':
        df.rename({r"Z'/ohm": 'Zre/ohm', 
                   r'Z"/ohm': 'Zim/ohm',
                   r"Z/ohm": 'Zmag/ohm'}, axis=1, inplace=True)
        df['Zcx/ohm'] = df['Zre/ohm'] + 1j*df['Zim/ohm']
        df['Angular_Freq'] = df['Freq/Hz']*2*np.pi
    
    # remove common extension tags
    if path.lower().endswith('.txt') or path.lower().endswith('.dta'):
        dict[path[0:-4]] = df
    else:
        dict[path] = df
    return dict


def Gamry_dta(file: str, line_offset: int=0):
    """Converts Gamry's .DTA file to usable format.
    
    ------------Gamry's Notation-----------------
    
    Gamry's Vf (filtered voltage) is the measured potential. 
        If you select IR Compensation, the actual applied voltage between current interruptions is the sum of the Vf and Vu data.
        
        In Corrosion Potential measurements, or in the Open Circuit Voltage (OCV) measurement before an experiment, Vf is the filtered, measured, open-circuit voltage. 
        A digital filter has been applied to minimize pickup of the AC mains frequency (50 or 60 Hz).
        
    Gamry's Vu is the uncompensated voltage, i.e. the voltage-drop across the solution resistance between the Working Electrode and the tip of the Reference Electrode.
        If you select IR Compensation (current interrupt), Vu is the difference between the measured voltage with the current flowing, and the voltage during the period of the current interrupt. The actual applied voltage between current interruptions is the sum of the Vf and Vu data.

    Gamry's Vm, where it appears, is included only for compatibility with older versions of the Gamry Framework Software.
    
    ---------------------------------------------
    Args:
        file (str): Path to .DTA file
        line_offset (int): Number of extra lines to skip. Negative number read earlier lines.

    Returns:
        pd.DataFrame: data
    """
    
    # Get technique. It sits in the third line of a .DTA file.
    # The actual text that appears here may be mutable in the experimental setup, check that if you're getting errors.
    with open(file, 'r', errors='replace') as opened_file:
        lines = opened_file.readlines()
        technique = lines[2].split('\t')[2]
    
    
    # Import data
    for alias in ['chronopotentiometry scan', 'istep', 'isteps', 'chronop']:
        if alias in technique.lower():
            df = pd.read_csv(file, 
                    encoding='unicode escape',
                    delimiter='\t', 
                    skiprows=62 + line_offset, 
                    index_col=0, 
                    names=['empty', '', 'Time/sec', 'Potential/V', 'Current/A', 'Vu/V', 'Sig', 'Ach', 'IERange', 'Over', 'Temp/C'], 
                    usecols=lambda x: x != 'empty'
                    )
            
            del df['Over'] # get rid of this useless, unparsable shit
            return df
        
    for alias in ['open circuit potential', 'ocp', 'ocpt']:
        if alias in technique.lower():
            df = pd.read_csv(file, 
                    encoding='unicode escape',
                    delimiter='\t', 
                    skiprows=51 + line_offset, 
                    index_col=0, 
                    names=['empty', '', 'Time/sec', 'Potential/V', 'Vm/V', 'Ach', 'Over', 'Temp/C'], 
                    usecols=lambda x: x != 'empty'
                    )
            
            del df['Over'] # get rid of this useless, unparsable shit
            return df
    
    for alias in ['geis', 'eis']:
        if alias in technique.lower():
            df = pd.read_csv(file, 
                    encoding='unicode escape',
                    delimiter='\t', 
                    skiprows=57 + line_offset, 
                    index_col=0, 
                    names=['empty', '', 'Time/sec', 'Freq/Hz', 'Zre/ohm', 'Zim/ohm', 'Zsig/V',
                            'Zmag/ohm', 'Phase/deg', 'iDC/A', 'VDC/V', 'IERange'], 
                    usecols=lambda x: x != 'empty'
                    )
            df['Zcx/ohm'] = df['Zre/ohm'] + 1j*df['Zim/ohm']
            df['Angular_Freq'] = df['Freq/Hz']*2*np.pi
            return df
            
    raise NameError(technique+' is not a recognized technique')


def Ecell_csv(file: str, offset=0):
    """Imports High-precision multimeter full cell data

    Args:
        file (str): filepath to cell voltage CSV
        offset (int, optional): Number of seconds added to sync to proper time. Defaults to 0.

    Returns:
        pd.DataFrame: DataFrame with Ecell/V and Time/sec
    """
    df = pd.read_csv(file,
                        names=['Ecell/V', 'datetime'], skiprows=[1], parse_dates=[1])
    td = df['datetime'] - df['datetime'].iloc[0]
    df['Time/sec'] = td.dt.total_seconds()
    
    df['Time/sec'] += offset
    return df