import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cmath

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

def CHI_plot(df, technique, option=None, label=None):
    """Creates quick plots from CHI data

    Args:
        df (pd.DataFrame): Dataframe of Data. Much match formats from importer.
        technique (str): Electrochemical technique; used to determine what plot to draw.
        option (str, optional): Options for different plots within a technique. Defaults to None.

    Returns:
        tuple: fig, ax 
    """
    if technique.lower() in ['a.c. impedance', 'imp', 'eis', 'peis']:
        if option != None and option.lower() == 'bode':
            fig, ax = plt.subplots(1, 2, figsize=(24, 8))
            ax[0].scatter(np.log10(df['Freq/Hz']), np.log10(df['Zmag/ohm']), label=label)
            ax[0].set_xlabel('log$_{10}(f)$')
            ax[0].set_ylabel('log$_{10}|Z|$')
            
            ax[1].scatter(np.log10(df['Freq/Hz']), -df['Phase/deg'], label=label)
            ax[1].set_xlabel('log$_{10}(f) $')
            ax[1].set_ylabel('$-\phi$ / $\degree$')
        else:
            fig, ax = plt.subplots()
            ax.plot(df['Zre/ohm'], -df['Zim/ohm'], label=label)
            ax.set_xlabel('$Z_{real}$ / $\Omega$')
            ax.set_ylabel('$-Z_{imag}$ / $\Omega$')
            
    elif technique.lower() in ['cyclic voltammetry', 'linear sweep voltammetry', 'cv', 'lsv']:
        fig, ax = plt.subplots()
        ax.plot(df['Potential/V'], df['Current/A']*1000, label=label)
        ax.set_xlabel('$E$ vs. RE / V')
        ax.set_ylabel('$i$ / mA')
        
    elif technique.lower() in ['ocp', 'ocpt', 'open circuit potential - time', 'multi-current steps', 'istep', 'cg']:
        fig, ax = plt.subplots()
        ax.plot(df['Time/sec'], df['Potential/V'], label=label)
        ax.set_ylabel('$t$ / s')
        ax.set_ylabel('$E$ vs. RE / V')
    
    elif technique.lower() in ['ca', 'pstep', 'multi-potential steps']:
        fig, ax = plt.subplots()
        ax.plot(df['Time/sec'], df['Current/A']*1000, label=label)
        ax.set_xlabel('$t$ / s')
        ax.set_ylabel('$i$ / mA')
        
    return fig, ax

# def CHI_add_coplot(df, ax, technique, option=None, label=labels[i]=None):
#     if technique.lower() in ['a.c. impedance', 'imp', 'eis', 'peis']:
#         if option != None and option.lower() == 'bode':
#             ax[0].scatter(np.log10(df['Freq/Hz']), np.log10(df['Zmag/ohm']), label=labels[i]=label=labels[i])
#             ax[0].set_xlabel('log$_{10}(f)$')
#             ax[0].set_ylabel('log$_{10}|Z|$')
            
#             ax[1].scatter(np.log10(df['Freq/Hz']), -df['Phase/deg'], label=labels[i]=label=labels[i])
#             ax[1].set_xlabel('log$_{10}(f) $')
#             ax[1].set_ylabel('$-\phi$ / $\degree$')
#         else:
#             ax.plot(df['Zre/ohm'], -df['Zim/ohm'], label=labels[i]=label=labels[i])
#             ax.set_xlabel('$Z_{real}$ / $\Omega$')
#             ax.set_ylabel('$-Z_{imag}$ / $\Omega$')
            
#     elif technique.lower() in ['cyclic voltammetry', 'linear sweep voltammetry', 'cv', 'lsv']:
#         ax.plot(df['Potential/V'], df['Current/A']*1000, label=labels[i]=label=labels[i])
#         ax.set_xlabel('$E$ vs. RE / V')
#         ax.set_ylabel('$i$ / mA')
        
#     elif technique.lower() in ['ocp', 'ocpt', 'open circuit potential - time', 'multi-current steps', 'istep', 'cg']:
#         ax.plot(df['Time/sec'], df['Potential/V'], label=labels[i]=label=labels[i])
#         ax.set_ylabel('$t$ / s')
#         ax.set_ylabel('$E$ vs. RE / V')
    
#     return ax

def CHI_coplot(df_list, technique, ax=False, fig=False, option=None, labels=None, order=None):
    """Generates coplotted data from CHI data
    
    Note:
        if fig, ax are supplied as a set of subplots that does not match the technique (i.e. bode/imp), 
        pyplot throws error that ax is np.ndarray.
        
    Known Bug:
        list index error if option='bode' and order is not None.
        Currently, orders for option='bode' are ignored

    Args:
        df_list (list): list of dataframes from CHI_txt
        technique (str): Electrochemical technique; used to determine what plot to draw.
        ax (bool, optional): Existing ax to plot on. Defaults to False.
        fig (bool, optional): Existing fig to plot on. Defaults to False.
        option (str, optional): Options for different plots within a technique. Defaults to None.
        labels (list, optional): Labels for plots. Defaults to None.
        order (list, optional): Order to draw figure legend with. Defaults to None.

    Raises:
        ValueError: Both fig and ax or neither fig nor ax must be passed

    Returns:
        tuple: fig, ax
    """
    # Handle option defaults
    ax_isarray = False
    if order == None:
        order = range(len(df_list))
    if labels == None:
        labels = []
        for i in range(len(df_list)):
            labels.append('_')
        draw_legend = False
    else:
        draw_legend = True
   
   # Check if new fig, ax should be generated
    if ax is False or fig is False:
        if fig is not False or ax is not False:
            raise ValueError('supply CHI_coplot with fig and ax or neither')
        if option != None and option.lower() == 'bode':
            fig, ax = plt.subplots(1, 2, figsize=(24, 8))
        else:
            fig, ax = plt.subplots()
            
    # Do plotting
    for i, df, in enumerate(df_list):
        if technique.lower() in ['a.c. impedance', 'imp', 'eis', 'peis']:
            if option != None and option.lower() == 'bode':
                ax_isarray = True
                ax[0].scatter(np.log10(df['Freq/Hz']), np.log10(df['Zmag/ohm']), label=labels[i])
                ax[0].set_xlabel('log$_{10}(f)$')
                ax[0].set_ylabel('log$_{10}|Z|$')
                
                ax[1].scatter(np.log10(df['Freq/Hz']), -df['Phase/deg'])
                ax[1].set_xlabel('log$_{10}(f) $')
                ax[1].set_ylabel('$-\phi$ / $\degree$')
            else:
                ax.plot(df['Zre/ohm'], -df['Zim/ohm'], label=labels[i])
                ax.set_xlabel('$Z_{real}$ / $\Omega$')
                ax.set_ylabel('$-Z_{imag}$ / $\Omega$')
                
        elif technique.lower() in ['cyclic voltammetry', 'linear sweep voltammetry', 'cv', 'lsv']:
            ax.plot(df['Potential/V'], df['Current/A']*1000, label=labels[i])
            ax.set_xlabel('$E$ vs. RE / V')
            ax.set_ylabel('$i$ / mA')
            
        elif technique.lower() in ['ocp', 'ocpt', 'open circuit potential - time', 'multi-current steps', 'istep', 'cg']:
            ax.plot(df['Time/sec'], df['Potential/V'], label=labels[i])
            ax.set_xlabel('$t$ / s')
            ax.set_ylabel('$E$ vs. RE / V')
            
        elif technique.lower() in ['ca', 'pstep', 'multi-potential steps']:
            ax.plot(df['Time/sec'], df['Current/A']*1000, label=labels[i])
            ax.set_xlabel('$t$ / s')
            ax.set_ylabel('$i$ / mA')
    
    # Draw legend if possible
    if draw_legend is True:
        if order is not None and ax_isarray is False:
            handles, labels = plt.gca().get_legend_handles_labels()
            fig.legend([handles[idx] for idx in order],[labels[idx] for idx in order])
        elif order is not None and ax_isarray is True:
            raise TypeError('Arrays of axes cannot be reordered. Sorry :/')
        else:
            fig.legend()     
         
    return fig, ax

def CHI_coplot_from_dict(df_dict, technique, ax=False, fig=False, option=None, labels=None, order=None):
    # Handle option defaults
    ax_isarray = False
    if order == None:
        order = range(len(df_dict))
    if labels == None:
        labels = []
        for i in range(len(df_dict)):
            labels.append('_')
        draw_legend = False
    else:
        draw_legend = True
   
   # Check if new fig, ax should be generated
    if ax is False or fig is False:
        if fig is not False or ax is not False:
            raise ValueError('supply CHI_coplot with fig and ax or neither')
        if option != None and option.lower() == 'bode':
            fig, ax = plt.subplots(1, 2, figsize=(24, 8))
        else:
            fig, ax = plt.subplots()
            
    # Do plotting
    for i, key, in enumerate([*df_dict]):
        if technique.lower() in ['a.c. impedance', 'imp', 'eis', 'peis']:
            if option != None and option.lower() == 'bode':
                ax_isarray = True
                ax[0].scatter(np.log10(df_dict[key]['Freq/Hz']), np.log10(df_dict[key]['Zmag/ohm']), label=labels[i])
                ax[0].set_xlabel('log$_{10}(f)$')
                ax[0].set_ylabel('log$_{10}|Z|$')
                
                ax[1].scatter(np.log10(df_dict[key]['Freq/Hz']), -df_dict[key]['Phase/deg'])
                ax[1].set_xlabel('log$_{10}(f) $')
                ax[1].set_ylabel('$-\phi$ / $\degree$')
            else:
                ax.plot(df_dict[key]['Zre/ohm'], -df_dict[key]['Zim/ohm'], label=labels[i])
                ax.set_xlabel('$Z_{real}$ / $\Omega$')
                ax.set_ylabel('$-Z_{imag}$ / $\Omega$')
                
        elif technique.lower() in ['cyclic voltammetry', 'linear sweep voltammetry', 'cv', 'lsv']:
            ax.plot(df_dict[key]['Potential/V'], df_dict[key]['Current/A']*1000, label=labels[i])
            ax.set_xlabel('$E$ vs. RE / V')
            ax.set_ylabel('$i$ / mA')
            
        elif technique.lower() in ['ocp', 'ocpt', 'open circuit potential - time', 'multi-current steps', 'istep', 'cg']:
            ax.plot(df_dict[key]['Time/sec'], df_dict[key]['Potential/V'], label=labels[i])
            ax.set_xlabel('$t$ / s')
            ax.set_ylabel('$E$ vs. RE / V')
    
    # Draw legend if possible
    if draw_legend is True:
        if order is not None and ax_isarray is False:
            handles, labels = plt.gca().get_legend_handles_labels()
            fig.legend([handles[idx] for idx in order],[labels[idx] for idx in order])
        elif order is not None and ax_isarray is True:
            raise TypeError('Arrays of axes cannot be reordered. Sorry :/')
        else:
            fig.legend()     
         
    return fig, ax

def plot_imp_py(df: pd.DataFrame, freq: np.ndarray, fit: np.ndarray, no_bode: bool=False):
    """General quick plotting for circuits fit with impedance.py from data in standard format from CHI_txt() importing.

    Args:
        df (pd.DataFrame): EIS data imported like CHI_txt
        fit (ndarray): impedance.py circuit.predict() output
        freq (ndarray): frequencies used for fitting
    
    Returns:
        tuple: fig, ax, fig, ndarray
    """
    fig_nyq, ax = plt.subplots()
    ax.scatter(df['Zre/ohm'], -df['Zim/ohm'], c='C0', label='Data')
    ax.plot(np.array([ele.real for ele in fit]), -np.array([ele.imag for ele in fit]), c='C1', label='Fit')

    ax.set_xlabel('$Z_{real}$ / $\Omega$')
    ax.set_ylabel('$-Z_{imaginary}$ / $\Omega$')

    if no_bode is False:
        fig_bode, axs = plt.subplots(2)
        axs[0].scatter(df['Freq/Hz'], df['Zmag/ohm'], label='Data', c='C0')
        axs[0].plot(freq, [np.abs(ele) for  ele in fit], label='Fit', c='C1')

        axs[0].set_xscale('log')
        axs[0].set_xlabel('$f$ / Hz')
        axs[0].set_ylabel('$Z_{mag}$ / $\Omega$')

        axs[1].scatter(df['Freq/Hz'], -df['Phase/deg'], label='Data', c='C0')
        axs[1].plot(freq, [-cmath.phase(ele)*180/np.pi for  ele in fit], label='Fit', c='C1')

        axs[1].set_xscale('log')
        axs[1].set_xlabel('$f$ / Hz')
        axs[1].set_ylabel('$-\phi$ / $\circ$')
    
        return fig_nyq, ax, fig_bode, axs
    
    else: return fig_nyq, ax