#!/Users/rickyrock/anaconda3/envs/COMP/bin/python

import pandas as pd
import numpy as np
import glob
import os

import matplotlib.pyplot as plt
import matplotlib.dates as md
import seaborn as sns
from datetime import datetime
from scipy import stats

from argparse import ArgumentParser


# functions
def input_arguments(): # arguments that are user defined
    # run script + -h to list current ports and see arguments.
    parser = ArgumentParser()
    parser.add_argument('--directory', type = str,
        help = 'Select the directory containing anemometer files to analyze (current dir is default).',
        default=".")
    parser.add_argument('--anemometer', type = str,
        help = 'csat3b (default) or windmaster.',
        default="csat3b")
    parser.add_argument('--freq', type = str,
        help = 'change the resampling frequency (must be > original sampling freq; default = 1min).',
        default="1min")
    parser.add_argument('--csv', action='store_true', help= 'output a csv resampled at a new frequency.')
    parser.add_argument('--plot', action='store_true', help= 'output windspeed and temperature time-series plots.')
    arguments = parser.parse_args()
    return arguments

def plot_timeseries(timestamps_x, Ux, Uy, Uz, Temp, name, save, save_name):
    # U, V, and W wind plot
    sns.set_theme('talk')
    sns.set_style("ticks")

    fig1,ax1 = plt.subplots( 1, 1, figsize = (8,6))
    plot1 = sns.lineplot(ax = ax1, x = timestamps_x,
                        y = Ux , alpha = 0.75, errorbar=None)
    plot2 = sns.lineplot(ax = ax1, x = timestamps_x,
                        y = Uy , alpha = 0.75, color="green", errorbar=None)
    plot3 = sns.lineplot(ax = ax1, x = timestamps_x,
                        y = Uz , alpha = 0.75, color="black", errorbar=None)
    ax1.xaxis.set_major_formatter(md.DateFormatter('%d-%m-%y %H:%M'))

    plt.xlabel("time")
    plt.xticks(rotation=45)
    plt.ylabel("windspeed (m/s)")
    plt.title(name +": Recorded Windspeeds", weight = "bold")
    plt.legend(loc="lower right", labels = ['u(m/s)','v(m/s)','w(m/s)'])
    sns.despine()

    plt.tight_layout()
    if save == True:
        plt.savefig(save_name+"_windspeed.png", dpi = 600)


    # Temperature plot
    sns.set_theme('talk')
    sns.set_style("ticks")

    fig2,ax2 = plt.subplots( 1, 1, figsize = (8,6))
    plot4 = sns.lineplot(ax = ax2, x = timestamps_x, color = "red",
                        y = Temp , alpha = 0.75, errorbar=None)
    ax2.xaxis.set_major_formatter(md.DateFormatter('%d-%m-%y %H:%M'))

    plt.xlabel("time")
    plt.xticks(rotation=45)
    plt.ylabel("Temperature (C)")
    plt.title(name +": Temperature", weight = "bold")
    plt.legend(loc="upper right", labels = ['T(C)'])
    sns.despine()

    plt.tight_layout()
    if save == True:
        plt.savefig(save_name+"_temp.png", dpi = 600)

    plt.show()



def main(args):
    # set global variables (not acutally global)
    anemometer_type = args.anemometer
    file_directory = args.directory
    freq = args.freq

    all_files = glob.glob(file_directory+'/*.csv')
    all_files.sort(key=os.path.getmtime)

    one_min_data = []
    for f in all_files:
        anemometer_file = pd.read_csv(f)

        #instrument specific
        if anemometer_type == "windmaster":
            anemometer_file['timestamp'] = pd.to_datetime(anemometer_file['Day_CPU(YYYY-MM-DD)'] + anemometer_file['time_CPU(HH:MM:SS.FFF)'], format='mixed')
            anemometer_file = anemometer_file.set_index('timestamp').drop(columns=['Index',
                                                                    'Day_CPU(YYYY-MM-DD)','time_CPU(HH:MM:SS.FFF)',
                                                                    'Start_codon', 'unit_ident', 'SOS(m/s)',
                                                                    'Error_code', 'Check_sum']).dropna()
            # some files have weird errors --> way to fix errors?
            # possible trips in serial logging
            # error_files: windmaster_data/windmaster_230709080003.csv,
            anemometer_file = anemometer_file.apply(pd.to_numeric, errors='coerce') # coerce sets these errors to NAN

        else: # for CSAT3b
            anemometer_file['timestamp'] = pd.to_datetime(anemometer_file['Day_CPU(YYYY-MM-DD)'] + anemometer_file['time_CPU(HH:MM:SS.FFF)'], format='mixed')
            anemometer_file = anemometer_file.set_index('timestamp').drop(columns=['Index','Day_CPU(YYYY-MM-DD)','time_CPU(HH:MM:SS.FFF)','Diagnostic_code', 'record_counter', 'sig_hex'])
            # errors seem to not be present for CSAT3b (if the damn thing works).

        one_min_avg = anemometer_file.resample(freq).mean()
        lst = [anemometer_file]
        del lst ; del anemometer_file
        one_min_data.append(one_min_avg)
    one_min_avg_df = pd.concat(one_min_data)

    # derive individual time, wind, and tmep vectors
    timestamps_xvar = one_min_avg_df.index
    if anemometer_type == "windmaster":
        name = "Gill Windmaster"
        Ux, Uy, Uz = one_min_avg_df['u(m/s)'], one_min_avg_df['v(m/s)'], one_min_avg_df['w(m/s)']
        temp = one_min_avg_df['T(Celsius)']
    else:
        name = "CSAT3b"
        Ux, Uy, Uz = one_min_avg_df['u_x(m/s)'], one_min_avg_df['u_y(m/s)'], one_min_avg_df['u_z(m/s)']
        temp = one_min_avg_df['T(Celsius)']

    #set arg to display if want csv or not.
    save_file = anemometer_type+'_'+freq
    if args.csv == True:
        one_min_avg_df.to_csv(save_file+'.csv')

    plot_timeseries(timestamps_xvar,Ux, Uy, Uz, temp, name, args.plot, save_file) # set arg for plot

if __name__ == '__main__':
    args = input_arguments()
    main(args)
