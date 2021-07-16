import pandas as pd
import numpy as np

def PeakTempCorrection(df, R0=0.49441, m=1):
    '''
    df must have Heat Rate, Peak Temp, Peak Height (W/g) as first three columns.

    ASTM E698-2011
    df is a dataframe of raw data, which has Heat Rate, Peak Temp (C), and Peak Height (W/g) columns
    R0 is the thermal resistance in K/mW
    m is the mass of the sample in mg
    '''

    df['log10(Heat Rate)'] = np.log10(df.iloc[:, 0])
    df['Height (mW)'] = df.iloc[:, 2] * m / 1000
    df['Lag Corr. Temp (C)'] = df.iloc[:, 1] - (df['Height (mW)'] * R0)
    df['Lag Corr. Temp (K)'] = df['Lag Corr. Temp (C)'] + 273.15
    df['Lag Corr. ΔT'] = df['Lag Corr. Temp (C)'] - df.loc[df.iloc[:, 0] == 10, 'Lag Corr. Temp (C)'].array
    return df