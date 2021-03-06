import numpy as np
from numpy.linalg import lstsq
import pandas as pd
import matplotlib.pyplot as plt

class PolyReg:
    """
    Uses sklear linear regression machinery, but has relevant callable attributes.
    
    No parameters can be fixed
    Polynomial coefficients in order of decreasing degree are in coef[i].
    Note that ss_yy is commonly named ss_tot in other implementations. This is the total sum of squares.
    coef = ndarray of fitting parameters in order of decreasing degree
    ss_res = sum of squares of residuals.
    std_err = ndarray of standard errors of the fitting parameters in order of decreasing degree. These are calculated as the square root of diagonal elements in the covariance matrix.
    """
    def __init__(self, xdata, ydata, degree: int):
        """
        :param xdata: Array of xdata
        :param ydata: Array of ydata
        :param degree: Degree of polynomial fit
        """
        self.xdata = xdata
        self.ydata = ydata
        self.degree = degree
        self.coef, self.cov = np.polyfit(xdata, ydata, degree, cov=True)
        self.residuals = ydata - np.polyval(self.coef, xdata)
        self.ss_res = np.sum(self.residuals**2)
        self.ss_yy = np.sum((ydata - np.mean(ydata)) ** 2)
        self.ss_xx = np.sum((xdata - np.mean(xdata)) ** 2)
        self.ss_xy = np.sum((xdata - np.mean(xdata))*(ydata - np.mean(ydata)))
        self.r_squared = 1 - (self.ss_res / self.ss_yy)
        self.std_err = np.sqrt(np.diag(self.cov))
        self.s_y = np.sqrt(self.ss_res / (len(ydata) - 1 - self.degree))
        self.roots = np.roots(self.coef)
        
    def report(self):
        '''
        Returns some quantities of interest
        '''
        params = {}
        for i in range(len(self.coef)):
            params['coef_deg' + str(len(self.coef) - i -1)] = self.coef[i]
            params['std_err_deg' + str(len(self.coef) - i -1)] = self.std_err[i]
            
        params['r_squared'] = self.r_squared
        params['s_y'] = self.s_y
        series = pd.Series(params)
        return series
    
    def eval(self, x):
        return np.polyval(self.coef, x)
    
    
class LinFixB:
    """Linear regression class similar to PolyReg, but with degree = 0 and the y-intercept (b) fixed at 0
    """
    def __init__(self, xdata, ydata) -> None:
        self.xdata = xdata
        self.ydata = ydata
        
        x_col = xdata[:, np.newaxis] # x must be a column vector for np.lstsq
        y_col = ydata[:, np.newaxis] # y must have same shape as x
        
        self.coef, ss_res, rank, s = lstsq(x_col, y_col, rcond=False)
        b = np.zeros([1]) # insert intercept manually
        self.coef = np.append(self.coef, b)
        
        self.cov = np.cov(xdata, ydata)
        self.residuals = ydata - np.polyval(self.coef, xdata)
        self.ss_res = np.sum(self.residuals**2)
        self.ss_yy = np.sum((ydata) ** 2)
        self.r_squared = 1 - (self.ss_res / self.ss_yy)
        self.std_err = np.sqrt(np.diag(self.cov)) # Not sure if this is correct
        self.s_y = np.sqrt(self.ss_res / (len(ydata) - 2)) # len(ydata) - 1 - degree of fit
        self.roots = np.roots(self.coef)
        
    def report(self):
        '''
        Returns some quantities of interest
        '''
        params = {}
        for i in range(len(self.coef)):
            params['coef_deg' + str(len(self.coef) - i -1)] = self.coef[i]
            
        params['r_squared'] = self.r_squared
        series = pd.Series(params)
        return series
    
    def eval(self, x):
        return np.polyval(self.coef, x)
    
    
def linear_region(x, y, bounds: tuple=None, index=False, ax=None):
    """Fits specified region to a line and plots it over the data

    Args:
        x (array): x data
        y (array): y data
        bounds (tuple, optional): Bounds of region to fit in units of x or array indicies if index is True. Defaults to None.
        index (bool, optional): If bounds should be read as array indicies. Defaults to False.
        ax: existing axes to plot on. Defaults to None.

    Returns:
        tuple: LinReg.PolyReg object containing linear fit, figure, axes or a tuple of fit, ax
    """
    if bounds != None:
        if index is True:
            bound_idx = bounds
        elif index is False:
            bound_idx = np.argmin(np.abs(x - bounds[0])), np.argmin(np.abs(x - bounds[1]))
    elif bounds == None:
        bound_idx = (0, len(x) - 1)
    fit = PolyReg(x[bound_idx[0]:bound_idx[1]], y[bound_idx[0]:bound_idx[1]], 1)
    
    if ax == None:
        fig, ax = plt.subplots()
        newax = True
    else:
        newax = False
        
    ax.scatter(x, y, c='C0')
    x_space = np.linspace(x[bound_idx[0]], x[bound_idx[1]], 1000)
    ax.plot(x_space, fit.eval(x_space), c='C1')
    
    if newax is True:
        return fit, fig, ax
    elif newax is False:
        return fit, ax
    


def avg_region(x, y, bounds: tuple=None, index=False):
    """Averages specified region

    Args:
        x (array): x data
        y (array): y data
        bounds (tuple, optional): Bounds of region to fit in units of x or array indicies if index is True. Defaults to None.
        index (bool, optional): If bounds should be read as array indicies. Defaults to False.

    Returns:
        float: average of y data over region
    """
    if bounds != None:
        if index is True:
            bound_idx = bounds
        elif index is False:
            bound_idx = np.argmin(np.abs(x - bounds[0])), np.argmin(np.abs(x - bounds[1]))
    elif bounds == None:
        bound_idx = (0, len(x) - 1)
    
    fig, ax = plt.subplots()
    ax.plot(x, y, zorder=0)
    ax.scatter((x[bound_idx[0]],x[bound_idx[1]]), ((y[bound_idx[0]], y[bound_idx[1]])),
               marker='|', s=250, c='C1', zorder=1)
    return np.mean(y[bound_idx[0]:bound_idx[1]]), fig, ax
