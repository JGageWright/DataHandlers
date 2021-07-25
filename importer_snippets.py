import pandas as pd
import tkinter as tk
from tkinter import filedialog

Tk = tk.Tk()
Tk.withdraw()


def ask_path():
    return filedialog.asksaveasfile(mode='w').name

def df_to_excel(df, sheet_name='Sheet1'):
    '''
    Uses pandas to always return a .xlsx file of the given df
    KNOWN BUG: Giving the save name a file extension results in multiple files being saved
    '''
    where = filedialog.asksaveasfile(mode='w', filetypes=[('Microsoft Excel Worksheet', '.xlsx')],
                                     defaultextension='.xlsx')
    save_name = where.name
    if save_name[-5:] != '.xlsx':
        save_name = str(save_name + '.xlsx')
    with pd.ExcelWriter(save_name) as writer:
        df.to_excel(writer, engine='openpyxl', sheet_name=sheet_name)

# Testing df
# df = pd.DataFrame({
#     1: ['one', 'four', 'seven'],
#     2: ['two', 'five', 'eight'],
#     3: ['three', 'six', 'nine']
# }, index=[0, 1, 2])
#
# df_to_excel(df)