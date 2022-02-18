import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def IR_abs_plot(df, title=None):
    '''
    Makes routine plots of IR data in Absorbance vs. Wavenumber form
    There must be columns named 'Wavenumber' and 'Absorbance'
    Returns fig, ax tuple
    '''
    x, y = df['Wavenumber'], df['Absorbance']

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.invert_xaxis()
    ax.set_ylabel('Absorbance (a.u.)')
    ax.set_xlabel('Wavenumber (cm$^{-1}$)')
    ax.set_title(str(title))
    return fig, ax

def CHI_plot(df, technique, option=None):
    """Creates quick plots from CHI data

    Args:
        df (pd.DataFrame): Dataframe of Data. Much match formats from importer.
        technique (str): Electrochemical technique; used to determine what plot to draw.
        option (str, optional): Options for different plots within a technique. Defaults to None.

    Returns:
        tuple: fig, ax tuple
    """
    if technique.lower() in ['a.c. impedance', 'imp', 'eis', 'peis']:
        if option != None and option.lower() == 'bode':
            fig, ax = plt.subplots(1, 2, figsize=(24, 8))
            ax[0].scatter(np.log10(df['Freq/Hz']), np.log10(df['Zmag/ohm']))
            ax[0].set_xlabel('log$_{10}(f)$')
            ax[0].set_ylabel('log$_{10}|Z|$')
            
            ax[1].scatter(np.log10(df['Freq/Hz']), -df['Phase/deg'])
            ax[1].set_xlabel('log$_{10}(f) $')
            ax[1].set_ylabel('$-\phi$ / $\degree$')
        else:
            fig, ax = plt.subplots()
            ax.plot(df['Zre/ohm'], -df['Zim/ohm'])
            ax.set_xlabel('$Z_{real}$ / $\Omega$')
            ax.set_ylabel('$-Z_{imag}$ / $\Omega$')
            
    elif technique.lower() in ['cyclic voltammetry', 'linear sweep voltammetry', 'cv', 'lsv']:
        fig, ax = plt.subplots()
        ax.plot(df['Potential/V'], df['Current/A']*1000)
        ax.set_xlabel('$E$ vs. RE / V')
        ax.set_ylabel('$i$ / mA')
        
    elif technique.lower() in ['ocp', 'ocpt', 'open circuit potential - time']:
        fig, ax = plt.subplots()
        ax.plot(df['Time/sec'] ,df['Potential/V'])
        ax.set_ylabel('$t$ / s')
        ax.set_ylabel('$E$ vs. RE / V')
        
    return fig, ax