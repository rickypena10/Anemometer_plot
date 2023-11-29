# Anemometer_plot
Quickly plot CSAT3b or Gill Windmaster data for on-the-fly analysis.

Running Anemometer_plot.py
    \tType “Anemometer_plot.py --help” into your terminal. You will see a full list of options.
        \t\t1.	“--directory” needs the path to the anemometer files you wish to analyze.
        \t\t2.	“--anemometer” needs the type of anemometer you are using
        \t\t3.	“--freq” is the frequency at which you’d like the data to be resampled to. For example, the data for the CSAT3b is logged at 10Hz. When the freq argument is left out, freq defaults to 1 minute averaging. So, the 10Hz data is reduced to 1 minute averages.
        \t\t4.	“--csv” doesn’t need an argument. If you simply have it typed, it will save a csv at the chosen resampled frequency. The csv is saved in your current working directory.
        \t\t5.	“--plot” doesn’t need an argument. If you simply have it typed, it will save a wind speed and temperature plot as pngs. The pngs are save in your current working directory. 