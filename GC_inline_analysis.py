import matplotlib.pyplot as plt
import glob
from scipy import interpolate
import numpy as np
import pandas as pd
from natsort import natsorted

def plot_GC_data(filepath, line1, line2):
    '''
    Opens and plots GC data. This code throws out the first 25 lines of data, and goes until the last line of data
    Using the 9 minute GC program. Splits lines by comma.
    '''
    with open(filepath,'r') as f: #open file
        lines = f.readlines()[line1:line2] # make an array of lines that include data
    yvalues = []
    for line in lines:
        if line.strip() == '':
            continue
        else:
            Type = line.split(",")
            yval = int(Type[0]) # only considering first column of data, convert to int
            yvalues.append(yval)
    xvalues = np.linspace(0,540,540*5-1)
    
    plt.plot(xvalues, yvalues)
    plt.xlabel("Retention time (seconds)")
    plt.ylabel("Intensity")
    # plt.savefig(filename + '.png', dpi=600)
    

def integrate_peak(filepath, xleft, xright, thresh, smooth, gas):
    
    with open(filepath, 'r') as f:
    # Define first and last lines to be read from ASC file. The data starts at line 25. 
        lines = f.readlines()[25:5424]
        
        newlines=[]
        for line in lines:
            if line.strip() == '':
                continue
            else:
                newlines.append(line)
        # The step size is 0.2, so multiply the x position by 5 and add 25 to convert to line number
        line1 = xleft*5 + 25
        line2 = xright*5 + 25
        
        newlinesarray = newlines[line1:line2]

        # Fill arrays for x and y values with first column of data points from the ASC file
        xvalues = []
        yvalues = []
        for line in newlinesarray:
            Type = line.split(",")        
            yval = int(Type[0])
            xvalues = np.linspace(xleft, xright, (line2 - line1))
            yvalues.append(yval)
        
        
        # Fit the data with a cubic spine with smooth factor of 1000.
        # Smoothing the second derivative of the spline fit as much as possible is important for determining peak edges.
        tck = interpolate.splrep(xvalues, yvalues, k=3, s=smooth)
        xnew = np.arange(xleft, xright, 0.2)
        ynew = interpolate.splev(xnew, tck, der=0)

        # take second derivative of the spline fit
        y2der = interpolate.splev(xnew, tck, der=2)
        
        if np.amax(y2der) < thresh:
            print('no peak')
            return 0

        # Find the left edge of the peak, assuming edge of peak starts when 2nd der >= thresh
        for idx, x in zip(range(0,len(xnew)), xnew):
            if y2der[idx] >= thresh:
                left_edge_idx = idx
                break 
        
        # Find the right edge of the peak, assuming edge of peak starts when 2nd der >= thresh
        for idx, x in zip(reversed(range(0,len(xnew))), xnew):
            if y2der[idx] >= thresh:
                right_edge_idx = idx
                break
        

        # Set up arrays that only include the peaks
        xpeak = xnew[left_edge_idx:right_edge_idx]
        ypeak = ynew[left_edge_idx:right_edge_idx]

        # Set up baseline function as a straight line between the two peak edges
        m = (ypeak[right_edge_idx - left_edge_idx - 1] - ypeak[0])/(xpeak[right_edge_idx - left_edge_idx - 1] - xpeak[0])
        b = ypeak[0] - m * xpeak[0]
        y_base = m * xpeak + b
        plt.figure()
        plt.plot(xpeak, ypeak, xpeak, y_base, 'r')
        plt.legend(['Spline', 'Baseline'])
        plt.title(gas +' Spline with Baseline')
        # plt.savefig(gas + 'splinewithbaseline.png', dpi=600)
        plt.show()

        # Subtract the baseline from the peak
        y_base_corr = []
        for y, z in zip(ypeak, y_base):
            y_bc = y - z
            y_base_corr.append(y_bc)
        plt.figure()
        plt.plot(xpeak, y_base_corr)
        plt.title(gas + ' Baseline Corrected')
        # plt.savefig(gas + 'baselinecorrected.png', dpi=600)
        plt.show()

        '''for idx, x, y in zip(range(0,len(xnew)), xnew, y2der):
                    print(idx,x, y) '''      

        # Integrate the Baseline Corrected peak
        integral = np.trapz(y_base_corr, dx=0.2)
        print(integral)
        return integral


def integrate_TCD_peak(filepath, xleft, xright, thresh, smooth):
    
    with open(filepath, 'r') as f:
    # Define first and last lines to be read from ASC file. The data starts at line 25
        lines = f.readlines()[25:5424]
        newlines=[]
        for line in lines:
            if line.strip() == '':
                continue
            else:
                newlines.append(line)

    # The step size is 0.2, so multiply the x position by 5 and add 25 to convert to line number
        line1 = xleft*5 + 25
        line2 = xright*5 + 25

        newlinesarray = newlines[line1:line2]
        
        xvalues = []
        yvalues = []
        for line in newlinesarray:
            Type = line.split(",")
            yval = -int(Type[0]) # This minus sign is the only fundamental difference between FID and TCD integration.
            xvalues = np.linspace(xleft, xright, (line2 - line1))
            yvalues.append(yval)

        tck = interpolate.splrep(xvalues, yvalues, k=3, s=smooth)
        xnew = np.arange(xleft, xright, 0.2)
        ynew = interpolate.splev(xnew, tck, der=0)

        # take second derivative of the spline fit
        y2der = interpolate.splev(xnew, tck, der=2)
        
        if np.amax(y2der) < thresh:
            print('no peak')
            return 0

        # Find the left edge of the peak, assuming edge of peak starts when 2nd der >= thresh
        for idx,x in zip(range(0,len(xnew)), xnew):
            if y2der[idx] >= thresh:
                left_edge_idx = idx
                break
        
        # Find the right edge of the peak, assuming edge of peak starts when 2nd der >= thresh
        for idx,x in zip(reversed(range(0,len(xnew))), xnew):
            if y2der[idx] >= thresh:
                right_edge_idx = idx
                break

        # Set up arrays that only include the peaks
        xpeak = xnew[left_edge_idx:right_edge_idx]
        ypeak = ynew[left_edge_idx:right_edge_idx]

        # Set up baseline function as a straight line between the two peak edges
        m = (ypeak[right_edge_idx - left_edge_idx-1] - ypeak[0]) / (xpeak[right_edge_idx - left_edge_idx-1] - xpeak[0])
        b = ypeak[0] - m * xpeak[0]
        y_base = m * xpeak + b
        plt.figure()
        plt.plot(xpeak, ypeak, xpeak, y_base, 'r')
        plt.legend(['Spline','Baseline'])
        plt.title('H2 Spline with Baseline')
        # plt.savefig('h2splinewithbaseline.png', dpi=600)
        plt.show()

        # Subtract the baseline from the peak
        y_base_corr = []
        for y, z in zip(ypeak, y_base):
            y_bc = y - z
            y_base_corr.append(y_bc)
        plt.figure()
        plt.plot(xpeak, y_base_corr)
        plt.title('H2 Baseline Corrected')
        # plt.savefig('h2baselinecorrected.png', dpi=600)
        plt.show()

        '''for idx,x,y in zip(range(0,len(xnew)), xnew, y2der):
                    print(idx, x, y) '''      

        # Integrate the Baseline Corrected peak
        integral = np.trapz(y_base_corr, dx=0.2)
        print(integral)
        return integral
    
    
# For 9 minute CO program, the plot values are: 26,5424
# TYPICAL CO 9 MIN RAMP PEAK VALUES:
# COleft=180
# COright=220
# COthresh=280
# CH4left=200
# CH4right=250
# CH4thresh=1000
# C2H4left=460
# C2H4right=520
# C2H4thresh=1000
# H2left=90
# H2right=105
# H2thresh=-2500
# smooth=10

def handle_GC_data(folderpath, overallleft, overallright, 
                   COleft, COright, COthresh, 
                   CH4left, CH4right, CH4thresh,
                   C2H4left, C2H4right, C2H4thresh, 
                   H2left, H2right, H2thresh, smooth):
    
    # This glob.glob makes an array of all the file names with ASC. 
    filenames = glob.glob(folderpath + '/*.ASC')
    natsortedfilenames = natsorted(filenames)
    
    # Instantiate arrays that will contain the files from both detectors
    run = {}
    # This only works for runs that have no more than 10 files. It doesn't work when D10 starts happening.
    string_list = ['{0:02}'.format(i) for i in range(0,int(len(natsortedfilenames))+1)]
    # print(string_list)
    for number in range(1,int(len(natsortedfilenames)/2)+1):
        run[number] = []
        for filename in natsortedfilenames:
            if 'D' + string_list[number] + '.ASC' in filename:
                run[number].append(filename)
    # print(run)
    peak_dict = {}
    for key in run:
        peak_dict[key] = {}
        for filename in run[key]:
            
            # Treat the FID Data First
            if 'FID' in filename:
                    print(filename)
                    plot_GC_data(filename, overallleft, overallright)
                    
                    # integrate CO peak. Typical peak on CO2 GC shows up between 175 and 235 seconds, and has a 
                    # second derivative threshold of 2500
                    print('CO')
                    CO_int = integrate_peak(filename, COleft, COright, COthresh, smooth, 'CO')
                    peak_dict[key]['CO'] = CO_int

                    # integrate CH4 peak. Typical peak on CO2 GC shows up between 240 and 300 seconds, and has a 
                    # second derivative threshold of 2500
                    print('CH4')
                    CH4_int = integrate_peak(filename, CH4left, CH4right, CH4thresh, smooth, 'CH4')
                    peak_dict[key]['CH4'] = CH4_int

                    # integrate C2H4 peak. Typical peak on CO2 GC shows up between 525 and 600 seconds, and has a 
                    # second derivative threshold of 2500
                    print('C2H4')
                    C2H4_int = integrate_peak(filename, C2H4left, C2H4right, C2H4thresh, smooth, 'C2H4')
                    peak_dict[key]['C2H4'] = C2H4_int


            # Treat the TCD Data Second
            if 'TCD' in filename: 
                print(filename)
                plot_GC_data(filename, overallleft, overallright)
                '''Integrate H2 peak. Typical peak shows up on CO2 GC between 150 and 230 seconds, and has a
                second derivative threshold of -2500. 
                ALSO CHANGED NEGATIVE SIGN IN FRONT OF H2_INT. 
                Peak pointed up is between 320 and 360. Pretty confident that the peak below between
                130 and 160 is the right one, it is the only one of the two that changes with increasing H2 
                conc for the calibration'''
                print('H2')
                H2_int = integrate_TCD_peak(filename, H2left, H2right, H2thresh, smooth)
                peak_dict[key]['H2'] = - H2_int

        # print("Peak dict:\n", peak_dict)
        df = pd.DataFrame(peak_dict).T  # transpose
        print(df.tail())
        
    return df
        
