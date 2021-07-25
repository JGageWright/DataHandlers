import numpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import scipy.stats as stats
from importer_snippets_2020 import make_ELISA_dataframe
import LinReg
import statsmodels.api as sm

# Get some test data
data_path = r'notebooks/testdata_02192021_rhMMP9.txt'  # Used Scan 2
with open(data_path) as file:
    lines = file.readlines()
    lines.pop(0)
    n = int((len(lines)) / 11)
    output_dataframes = []
    for i in range(n):
        df = make_ELISA_dataframe(lines[11 * i:11 * i + 8])
        output_dataframes.append(df)

# Choose scan to use and do background subtraction
raw = output_dataframes[1].iloc[0:8, 0:8]
sub = raw.iloc[0:6, 0:8].sub(raw.iloc[6:8, 0:8].mean(axis=1).mean(axis=0))

# Reshape s.t. rows are replicants, the typical quadruplicant layout is below
reshape = sub.iloc[:, 4:8].rename(
    index={'A': 'I', 'B': 'J', 'C': 'K', 'D': 'L', 'E': 'M', 'F': 'N'},
    columns={5: 1, 6: 2, 7: 3, 8: 4})
data = sub.iloc[:, 0:4].append(reshape)

# Run stats
data['Mean'] = data.iloc[:,0:4].mean(axis=1)
data['SD'] = data.iloc[:, 0:4].std(ddof=1, axis=1)
data['Conc'] = {3500: 'A', 2500: 'B', 1500: 'C', 1000: 'D',
                750: 'E', 500: 'F', 400: 'I', 300: 'J',
                200: 'K', 100: 'L', 50: 'M', 25: 'N'}

# Replace outliers with NaN
def grubbs_filter(data):
    """
    This will be necessary, needs to replace any singular outlier with NaN
    """
    # the outlier I happen to have already found, write a real function!
    data.iloc[2, 3] = np.NaN
    return data


data = grubbs_filter(data)
xdata = np.array(data['Conc'].loc['F':'N'])
ydata = np.array(data['Mean'].loc['F':'N'])

# SciPy implementation
# def Linear(x, m, b):
#     return m*x + b
#
# popt, pcov = opt.curve_fit(Linear, xdata, ydata)


reg = LinReg.PolyReg(xdata, ydata, 1)
print(reg.coef)
print(reg.std_err[0])
print(reg.s_y)

# model, cov = np.polyfit(xdata, ydata, 1, full=False, cov=True)
# print(model, cov, end='\n')
#
# print(np.trace(cov)**2)

