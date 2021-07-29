import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('JGW')

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
    plt.grid()
    ax.set_ylabel('Absorbance (a.u.)')
    ax.set_xlabel('Wavenumber (cm$^{-1}$)')
    ax.set_title(str(title))
    return fig, ax