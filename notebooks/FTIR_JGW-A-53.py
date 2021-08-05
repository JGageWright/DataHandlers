import pandas as pd
import matplotlib.pyplot as plt
from DataHandlers import importer_snippets, importer_snippets_2020, plotting


# Filename library:
path_list = importer_snippets_2020.get_filenames_from_folder(r'..\data\JGW-A-53', extension='csv')
# for path in path_list:
#     print(path)

KBr_df = importer_snippets.cary630(r'..\data\JGW-A-53\kbr_jgw-a-53-03.csv')
Hen_df = importer_snippets.cary630(r'..\data\JGW-A-53\henicosane.urea_jgw-a-53-35.csv')
DAB_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,4-dab_jgw-a-53-34.csv')
DAH_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,6-dah_jgw-a-53-15.csv')
DAO_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,8-dao_jgw-a-53-32.csv')
DAN_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,9-dan_jgw-a-53-30.csv')
DAD_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,10-dad_jgw-a-53-19.csv')
DADD_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,12-dadd_jgw-a-53-24.csv')

# Subtract the heneicosane/urea spectrum
subtract = True

if subtract == True:
    DAB_df['Absorbance'] = DAB_df['Absorbance'] - Hen_df['Absorbance']
    DAH_df['Absorbance'] = DAH_df['Absorbance'] - Hen_df['Absorbance']
    DAO_df['Absorbance'] = DAO_df['Absorbance'] - Hen_df['Absorbance']
    DAN_df['Absorbance'] = DAN_df['Absorbance'] - Hen_df['Absorbance']
    DAD_df['Absorbance'] = DAD_df['Absorbance'] - Hen_df['Absorbance']
    DADD_df['Absorbance'] = DADD_df['Absorbance'] - Hen_df['Absorbance']

KBr_fig, KBr_ax = plotting.IR_abs_plot(KBr_df, 'Pure KBr')
Hen_fig, Hen_ax = plotting.IR_abs_plot(Hen_df, 'Heneicosane/urea')
DAB_fig, DAB_ax = plotting.IR_abs_plot(DAB_df, '1,4-diacetoxybutane/urea')
DAH_fig, DAH_ax = plotting.IR_abs_plot(DAH_df, '1,6-diacetoxyhexane/urea')
DAO_fig, DAO_ax = plotting.IR_abs_plot(DAO_df, '1,8-diacetoxyoctane/urea')
DAN_fig, DAN_ax = plotting.IR_abs_plot(DAN_df, '1,9-diacetoxynonane/urea')
DAD_fig, DAD_ax = plotting.IR_abs_plot(DAD_df, '1,10-diacetoxydecane/urea')
DADD_fig, DADD_ax = plotting.IR_abs_plot(DADD_df, '1,12-diacetoxydodecane/urea')



# just plot the carbonyl region
all_ax = [KBr_ax, Hen_ax, DAB_ax, DAH_ax, DAO_ax, DAN_ax, DAD_ax, DADD_ax]
for ax in all_ax:
    ax.set_xlim(1760, 1700)
    ax.set_ylim(0, 2)

fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, sharex=True)
fig.set_size_inches(8.5, 11)

plt.show()