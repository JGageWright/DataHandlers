import pandas as pd
import glob, os, time, openpyxl
from tkinter import filedialog, messagebox
import tkinter as tk

def get_folders(folder_list=None):
    '''
    Gets path of any set of directories from the user manually
    '''
    if folder_list == None:
        folder_list = []
    folder_path = filedialog.askdirectory(title='Select Data Folder')
    folder_list.append(folder_path)
    prompt = tk.messagebox.askyesno('Data Folder Selection',
                                    'Are there any other folders?', icon='warning')
    if prompt == True:
        get_folders(folder_list)

    return folder_list


def get_filenames_from_folder(folder_path, extension=None):
    '''
    Takes folder_path
    Returns list of .SSM file paths in folder_path
    '''
    filenames = []
    for file in glob.glob(folder_path + '/*' + str(extension)):
        filenames.append(file)
    filenames.sort()  # Perhaps unnecessary, brings me peace
    return filenames

def get_filename_and_extension(path):
    '''
    Previously get_column_name
    Takes file path
    Returns filename and extension only for column naming
    '''
    return path.split("\\")[-1]


#Stellarnet/Spectrawiz SSM Importer
def series_stellarnet_ssm(file):
    """
    Takes path to .SSM file and imports using pandas from_csv() to a Series
    Returns intensity data only
    """
    df = pd.read_csv(file, skiprows=1, delim_whitespace=True, names=['wavelength', 'intensity'])
    list = []
    for element in df['intensity']:
        list.append(element)
    series = pd.Series(list)
    return series


def concat_me(DataFrame, Series, name=None):
    """
    Concatenates Series in to new DataFrame Column
    Added Bonus: Names series
    """
    Series.name = name
    return pd.concat([DataFrame, Series], axis=1)


def import_ssm_folder(folder_path):
    """
    Takes folder path, abstracts to get filenames list and
    Concatenates the series representing all data
    Returns DataFrame of folder's .SSM data

    Dependent on tkinter, glob, pandas
    """
    filenames = get_filenames_from_folder(folder_path, '.ssm')
    basis = pd.read_csv(filenames[0],
                        skiprows=1,
                        delim_whitespace=True,
                        names=['Wavelength', get_filename_and_extension(filenames[0])])
    for file in filenames[1::1]:
        series = series_stellarnet_ssm(file)
        name = get_filename_and_extension(file)
        basis = concat_me(basis, series, name)
    basis.set_index(basis.columns[0], inplace=True)
    return basis


def blank_subtract(raw):
    """
    Takes raw DataFrame with n columns
    Subtracts all values by value in nth column
    Returns DataFrame with n-1 columns
    """
    blank = raw.iloc[:, -1]
    no_blank = raw.iloc[:, 0:-1]
    subtracted = no_blank.sub(blank, axis=0)
    return subtracted


def get_params(folder_path):
    """
    Grabs the parameters reported by the stellarnet system
    """
    filenames = get_filenames_from_folder(folder_path, '.ssm')
    head = pd.read_csv(filenames[0], nrows=0, delim_whitespace=True)
    params = list(head.columns.values)
    return params


#ELISA Importer
def make_ELISA_dataframe(lines):
    '''
    Takes sorted sets lines from the raw text file
    Places OD data in units of (a.u.) in dataframes that maintain the 8x12 shape (but inlcude indexes).
    '''
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    df = pd.DataFrame(columns=range(1, 13))
    row_indexer = 0
    for line in lines:
        # print(line)
        row_as_list = line.split(sep=',')
        if len(row_as_list) == 13:
            row_as_list.pop(0)
        else:
            continue
            # Lines that do not contain data are directed here
        row_dict = {}
        column_indexer = 0
        for value in row_as_list:
            row_dict[column_indexer + 1] = int(value.strip('+')) / 1000
            column_indexer += 1
        s = pd.Series(row_dict)
        s.name = rows[row_indexer]
        df = df.append(s)
        row_indexer += 1
    return df

# with open(file_path) as file:
#     lines = file.readlines()
#     lines.pop(0)
#     n = int((len(lines)) / 11)
#     output_dataframes = []
#     for i in range(n):
#         df = make_ELISA_dataframe(lines[11*i:11*i + 8])
#         output_dataframes.append(df)


#Episodic Importers
def episodic_to_dataframe(file):
    '''
    Takes .EP1x file, returns dataframe indexed by wavelength and 'epx'
    where x is the episode number

    pd.read_csv needs to know how many columns there will be before importing
    or else it will assume the first row contains column names, not data
    '''
    row = pd.read_csv(file, delim_whitespace=True, nrows=1)
    num_episodes = len(row.columns) - 1
    column_names = ['wavelength']
    for column in range(num_episodes):
        column_names.append('ep' + str(column + 1))
    # Now it will actually be imported
    raw = pd.read_csv(file, delim_whitespace=True, index_col=0, names=column_names)
    # Columns are now indexed with their episode number.
    return raw


def export_dfl(df_list, params):
    '''
    Takes the list of [filename, df] pairs generated from legacy FRET script
    Saves each dataframe (and input params) to separate sheets in a single .xlsx file in the save location
    '''
    save_path = filedialog.asksaveasfile(title='Select Save Location',
                                         filetypes=[('Microsoft Excel Worksheet', '.xlsx')])
    save_name = save_path.name
    if save_name[-5:] != '.xlsx':
        save_name = str(save_name + '.xlsx')
    with pd.ExcelWriter(save_name) as writer:
        for name_df_pairs in df_list:
            name_df_pairs[1].to_excel(writer,
                                      sheet_name=name_df_pairs[0])
        params.to_excel(writer, sheet_name='params')
        writer.save()
        writer.close()


def export_dfl_list(dfl_list, params):
    '''
    Takes the dfl_list generated from the data folder
    Saves each signal df and params to separate sheets in a single .xlsx file in the save location

    Recall that dfl_list is a monster object of many nested lists, which during its invention indexed like:
    dfl_list[conc_1, ...][trial_1, ... , trial_n, signal][params, spectra_dataframe]

    OPEN ISSUE: the params that is passed in does not necessarily apply to each set of spectra.
    '''
    save_path = filedialog.asksaveasfile(title='Select Save Location',
                                         filetypes=[('Microsoft Excel Worksheet', '.xlsx')])
    save_name = save_path.name
    if save_name[-5:] != '.xlsx':
        save_name = str(save_name + '.xlsx')
    with pd.ExcelWriter(save_name) as writer:
        for i in range(len(dfl_list)):
            dfl_list[i][-1].to_excel(writer, sheet_name='Conc' + str(i))
        params.to_excel(writer, sheet_name='params')

#SET OFFSET HERE IN SECONDS
def get_times(params, episodes):
    '''
    Returns a list of times, marking the start of each collection period
    Times are strictly in seconds
    '''
    collection_period = params['scans_avg'] * (int(params['int_time']) / 1000)
    delay = ((int(params['min_delay']) * 60) + (int(params['ms_delay']) / 1000))
    times = []
    for ep in range(episodes):
        times.append(
            int(ep * (collection_period + delay) + 15) #SET OFFSET HERE IN SECONDS
        )
    return times


def convert_times(list):
    '''
    Takes list of times in seconds
    Returns list of times in more readable H:M:S format
    '''
    time_codes = []
    for i in list:
        time_codes.append(time.strftime("%H:%M:%S", time.gmtime(i)))
    return time_codes