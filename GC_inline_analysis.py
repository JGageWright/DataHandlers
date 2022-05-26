import matplotlib.pyplot as plt
import glob
from scipy import interpolate
import numpy as np
import pandas as pd
from natsort import natsorted

def plot_GC_data(filepath, line1):
    '''
    Opens and plots GC data. This code throws out the header of the ACS file and reads until the last line of data
    Using the 9 minute GC program. Splits lines by comma.
    '''
    with open(filepath,'r') as f: #open file
        lines = f.readlines()[line1:] # make an array of lines that include data
    yvalues = []
    for line in lines:
        if line.strip() == '':
            continue
        else:
            Type = line.split(",")
            yval = int(Type[0]) # only considering first column of data (Type[0] = Type[1]), convert to int
            yvalues.append(yval)
    end_time = len(yvalues) / 5 #sampling rate is 5 / second
    xvalues = np.linspace(0, end_time, len(yvalues))
    
    plt.plot(xvalues, yvalues)
    plt.xlabel("Retention time (seconds)")
    plt.ylabel("Intensity")
    # plt.savefig(filename + '.png', dpi=600)
    

def integrate_peak(filepath, xleft, xright, data_start_line, thresh, smooth, gas, suppress_outputs: bool=False):
    
    with open(filepath, 'r') as f:
    # Define first and last lines to be read from ASC file. The data starts at data_start_line. 
        lines = f.readlines()[data_start_line:]
        
        newlines = []
        for line in lines:
            if line.strip() == '':
                continue
            else:
                newlines.append(line)
        # The step size is 0.2, so multiply the x position by 5 and add data_start_line to convert to line number
        line1 = xleft * 5 + data_start_line
        line2 = xright * 5 + data_start_line
        
        newlinesarray = newlines[line1:line2]

        # Fill arrays for x and y values with first column of data points from the ASC file
        xvalues = []
        yvalues = []
        for line in newlinesarray:
            Type = line.split(",")        
            yval = int(Type[0]) # only considering first column of data (Type[0] = Type[1]), convert to int
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
            if suppress_outputs is False:
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
        
        # If the peak has no width, return integral of NaN, warn user, but don't exit the script
        try:
            # Set up arrays that only include the peaks
            xpeak = xnew[left_edge_idx:right_edge_idx]
            ypeak = ynew[left_edge_idx:right_edge_idx]

            # Set up baseline function as a straight line between the two peak edges
            m = (ypeak[right_edge_idx - left_edge_idx - 1] - ypeak[0])/(xpeak[right_edge_idx - left_edge_idx - 1] - xpeak[0])
            b = ypeak[0] - m * xpeak[0]
            y_base = m * xpeak + b
        except IndexError:
            if left_edge_idx == right_edge_idx:
                if suppress_outputs is False:
                    print('Left and right peak edges have the same index (the peak has no width)')
            return np.NAN # Kill this function call if IndexError is raised, but continue script
        
        # Subtract the baseline from the peak
        y_base_corr = []
        for y, z in zip(ypeak, y_base):
            y_bc = y - z
            y_base_corr.append(y_bc)
           
        # Integrate the Baseline Corrected peak
        integral = np.trapz(y_base_corr, dx=0.2)
        
        # Return plot outputs
        if suppress_outputs is False:
            plt.figure()
            plt.plot(xpeak, ypeak, xpeak, y_base, 'r')
            plt.legend(['Spline', 'Baseline'])
            plt.title(gas +' Spline with Baseline')
            # plt.savefig(gas + 'splinewithbaseline.png', dpi=600)
            plt.show()

            plt.figure()
            plt.plot(xpeak, y_base_corr)
            plt.title(gas + ' Baseline Corrected')
            # plt.savefig(gas + 'baselinecorrected.png', dpi=600)
            plt.show()

            '''for idx, x, y in zip(range(0,len(xnew)), xnew, y2der):
                        print(idx,x, y) '''      
            print(integral)
            
        return integral


def integrate_TCD_peak(filepath, xleft, xright, data_start_line, thresh, smooth, suppress_outputs: bool=False):
    
    with open(filepath, 'r') as f:
    # Define first and last lines to be read from ASC file. The data starts at data_start_line
        lines = f.readlines()[data_start_line:]
        newlines=[]
        for line in lines:
            if line.strip() == '':
                continue
            else:
                newlines.append(line)

    # The step size is 0.2, so multiply the x position by 5 and add data_start_line to convert to line number
        line1 = xleft*5 + data_start_line
        line2 = xright*5 + data_start_line

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
            if suppress_outputs is False:
                print('no peak')
            return 0

        # Find the left edge of the peak, assuming edge of peak starts when 2nd der >= thresh
        for idx, x in zip(range(0, len(xnew)), xnew):
            if y2der[idx] >= thresh:
                left_edge_idx = idx
                break
        
        # Find the right edge of the peak, assuming edge of peak starts when 2nd der >= thresh
        for idx, x in zip(reversed(range(0, len(xnew))), xnew):
            if y2der[idx] >= thresh:
                right_edge_idx = idx
                break

        # Set up arrays that only include the peaks
        xpeak = xnew[left_edge_idx:right_edge_idx]
        ypeak = ynew[left_edge_idx:right_edge_idx]

        # If the peak has no width, return integral of NaN, warn user, but don't exit the script
        try:
            # Set up arrays that only include the peaks
            xpeak = xnew[left_edge_idx:right_edge_idx]
            ypeak = ynew[left_edge_idx:right_edge_idx]

            # Set up baseline function as a straight line between the two peak edges
            m = (ypeak[right_edge_idx - left_edge_idx - 1] - ypeak[0])/(xpeak[right_edge_idx - left_edge_idx - 1] - xpeak[0])
            b = ypeak[0] - m * xpeak[0]
            y_base = m * xpeak + b
        except IndexError:
            if left_edge_idx == right_edge_idx:
                if suppress_outputs is False:
                    print('Left and right peak edges have the same index (the peak has no width)')
            return np.NAN # Kill this function call if IndexError is raised, but continue script

        # Subtract the baseline from the peak
        y_base_corr = []
        for y, z in zip(ypeak, y_base):
            y_bc = y - z
            y_base_corr.append(y_bc)

        # Integrate the Baseline Corrected peak
        integral = np.trapz(y_base_corr, dx=0.2)


        if suppress_outputs is False:
            plt.figure()
            plt.plot(xpeak, ypeak, xpeak, y_base, 'r')
            plt.legend(['Spline','Baseline'])
            plt.title('H2 Spline with Baseline')
            # plt.savefig('h2splinewithbaseline.png', dpi=600)
            plt.show()

            plt.figure()
            plt.plot(xpeak, y_base_corr)
            plt.title('H2 Baseline Corrected')
            # plt.savefig('h2baselinecorrected.png', dpi=600)
            plt.show()

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

def handle_GC_data(folderpath,
                   COleft, COright, COthresh,
                   CH4left, CH4right, CH4thresh,
                   C2H4left, C2H4right, C2H4thresh, 
                   H2left, H2right, H2thresh, smooth,
                   data_start_line: int=25,
                   suppress_outputs: bool=False):
    
    # This glob.glob makes an array of all the file names with ASC. 
    filenames = glob.glob(folderpath + '/*.ASC')
    natsortedfilenames = natsorted(filenames)
    
    # Instantiate arrays that will contain the files from both detectors
    run = {}
    
    string_list = []
    for filename in natsortedfilenames:
        string_list.append(filename[-6:-4]) # Will throw error if file run number is > 99 (i.e. --D100)
    
    string_list = sorted(list(set(string_list))) # remove duplicates from finding TCD and FID run numbers
    fire_numbers = sorted([int(i) for i in string_list])
    # print(fire_numbers)
    for idx, number in enumerate(fire_numbers):
        run[number] = []
        for filename in natsortedfilenames:
            if 'D' + string_list[idx] + '.ASC' in filename:
                run[number].append(filename)
                
    peak_dict = {}
    for key in run:
        peak_dict[key] = {}
        for filename in run[key]:
            
            # Treat the FID Data First
            if 'FID' in filename:
                    if suppress_outputs is False:
                        print(filename)
                        plot_GC_data(filename, data_start_line)
                    
                    # integrate CO peak. Typical peak on CO2 GC shows up between 175 and 235 seconds, and has a 
                    # second derivative threshold of 2500
                    if suppress_outputs is False:
                        print('CO')
                    CO_int = integrate_peak(filename, COleft, COright, data_start_line, COthresh, smooth, 'CO', suppress_outputs=suppress_outputs)
                    peak_dict[key]['CO'] = CO_int

                    # integrate CH4 peak. Typical peak on CO2 GC shows up between 240 and 300 seconds, and has a 
                    # second derivative threshold of 2500
                    if suppress_outputs is False:
                        print('CH4')
                    CH4_int = integrate_peak(filename, CH4left, CH4right, data_start_line, CH4thresh, smooth, 'CH4', suppress_outputs=suppress_outputs)
                    peak_dict[key]['CH4'] = CH4_int

                    # integrate C2H4 peak. Typical peak on CO2 GC shows up between 525 and 600 seconds, and has a 
                    # second derivative threshold of 2500
                    if suppress_outputs is False:
                        print('C2H4')
                    C2H4_int = integrate_peak(filename, C2H4left, C2H4right, data_start_line, C2H4thresh, smooth, 'C2H4', suppress_outputs=suppress_outputs)
                    peak_dict[key]['C2H4'] = C2H4_int


            # Treat the TCD Data Second
            '''Integrate H2 peak. Typical peak shows up on CO2 GC between 150 and 230 seconds, and has a
            second derivative threshold of -2500. 
            ALSO CHANGED NEGATIVE SIGN IN FRONT OF H2_INT. 
            Peak pointed up is between 320 and 360. Pretty confident that the peak below between
            130 and 160 is the right one, it is the only one of the two that changes with increasing H2 
            conc for the calibration'''
            if 'TCD' in filename: 
                if suppress_outputs is False:
                    print(filename)
                    plot_GC_data(filename, data_start_line)
                    print('H2')
                H2_int = integrate_TCD_peak(filename, H2left, H2right, data_start_line, H2thresh, smooth, suppress_outputs=suppress_outputs)
                peak_dict[key]['H2'] = - H2_int

        # print("Peak dict:\n", peak_dict)
        df = pd.DataFrame(peak_dict).T  # transpose
        
        # print recently computed peak table to user
        if suppress_outputs is False:
            print(df.tail())
        
    df.reset_index(drop=True, inplace=True) # index from 0
    return df

def plot_FE(df, current_mA=200):
    """Plot H2 and C2H4 FE
    Set for dark backdrop plot style

    Args:
        df (DataFrame): df returned by handle_GC_data
        current_mA (int, optional): Current passed during step. Defaults to 200.
        
    Returns:
        fig, ax (tuple): fig and ax used for plotting
    """
    
    # Calibrations March 2022
    # Calibrations = mA per mL GC fire / peak area per mL GC fire
    calibrations = {'C2H4': 57.7531642857143 / 2019566.04657302,
                    'CH4': 4.16953035714286 / 141990.386115765,
                    'H2': -14.1597480654762 / 34959.0238571043,
                    'CO': 0 / 715060.1018}
    
    # Fix notebook cell rerunning key error
    if 'H2 FE/%' not in list(df.columns):
        for col in df:
            df[str(col) + ' FE/%'] = df[col] * calibrations[str(col)] / current_mA * 100

    fig, ax = plt.subplots()
    if plt.rcParams['axes.facecolor'] == 'black':
        h2_color = 'w'
    else:
        h2_color = 'k'
    ax.plot((df.index - 1) * .15, df['H2 FE/%'], label='Hydrogen', c=h2_color)
    ax.plot((df.index - 1 )* .15, df['C2H4 FE/%'], label='Ethylene', c='#1e81b0')
    ax.set_xlabel('$t$ / h')
    ax.set_ylabel('Faradaic Efficiency / %')
    ax.set_ylim(0, 100)
    ax.legend()
    
    return fig, ax

def GC_CO_SPC(df: pd.DataFrame, CO_flow_rate: float=1, total_flow_rate: float=20):
    """Calculates CO Single Pass Conversion based on the CO peak in GC.

    Args:
        df (pd.DataFrame): df with column ['CO'] containing GC peak integrals for CO.
        CO_flow_rate (float, optional): CO flow rate in sccm or mL/min. Defaults to 1.
        total_flow_rate (float, optional): Total flow rate to GC in sccm or min. Defaults to 20.

    Returns:
        np.Series: Series of SPC values.
    """
    
    calibration = (5000 / 10e9 / 22.4) / 715060.1018 # mol CO / min per unit integral
    CO_per_fire = df['CO'] * calibration # mol CO / min
    CO_to_GC = total_flow_rate / (1000 * 22.4) * (CO_flow_rate / total_flow_rate) # mol CO min at 0% conversion
    
    spc = 1 - (CO_per_fire/(CO_to_GC))
    return spc