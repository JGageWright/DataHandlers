import pandas as pd
import matplotlib.pyplot as plt
from DataHandlers import importer_snippets, importer_snippets_2020, plotting


# Filename library:
path_list = importer_snippets_2020.get_filenames_from_folder(r'..\data\JGW-A-53', extension='csv')
# for path in path_list:
#     print(path)

KBr_df = importer_snippets.cary630(r'..\data\JGW-A-53\kbr_jgw-a-53-03.csv')
DAN_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,9-dan_jgw-a-53-12.csv')
DAO_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,8-dao_jgw-a-53-14.csv')
DAH_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,6-dah_jgw-a-53-15.csv')
DADD_df = importer_snippets.cary630(r'..\data\JGW-A-53\1,12-dadd_jgw-a-53-17.csv')

KBr_fig, KBr_ax = plotting.IR_abs_plot(KBr_df, 'Pure KBr')
DAN_fig, DAN_ax = plotting.IR_abs_plot(DAN_df, '1,9-diacetoxynonane/urea')
DAO_fig, DAO_ax = plotting.IR_abs_plot(DAO_df, '1,8-diacetoxyoctane/urea')
DAH_fig, DAH_ax = plotting.IR_abs_plot(DAH_df, '1,6-diacetoxyhexane/urea')
DADD_fig, DADD_ax = plotting.IR_abs_plot(DADD_df, '1,12-diacetoxydodecane/urea')

# just plot the carbonyl region
all_ax = [KBr_ax, DAN_ax, DAO_ax, DAH_ax, DADD_ax]
for ax in all_ax:
    ax.set_xlim(1760, 1700)
    ax.set_ylim(0, 2)

plt.show()