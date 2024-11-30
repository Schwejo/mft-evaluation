
import matplotlib.pyplot as plt
import statistics
####### IMPORT PACKAGES #######

from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
import scipy.interpolate as sip
import colour

start_value_list = []
end_value_list = []
zero_index_list = []

# probably not needed
# def find_zeros(list):
    # zero_index = np.where(list == 0)
    # return zero_index

# STEP 1
# works mostly

for i in range(0,3):
    file_name = f"HF_GA_AUP_{i+1}-spect_convert"
    spectrum_df = pd.read_csv(filepath_or_buffer=f"HF_GA_AUP/{file_name}.txt", index_col="#Wavelength [nm]", sep="\t")

    start_value = spectrum_df["0[s]"] / spectrum_df["White Std."] * 100
    start_value_list.append(start_value)
    end_value = spectrum_df.iloc[:, -1] / spectrum_df["White Std."] * 100
    end_value_list.append(end_value)

    # probably not needed
    # zero_index = find_zeros(np.array(end_value))
    # zero_index_list.append(zero_index)

# STEP 2
# TODO

plt.figure()
ax1 = plt.subplot(111)
ax1.plot(start_value_list[0], label='Start', color='green', linewidth=0.8)
ax1.plot(end_value_list[0], label='End', color='red', linewidth=0.8)
plt.ylim(0,80)
plt.xlim(420,720)
plt.grid(alpha=0.5)
ax1.set_title(f"Spektrum {file_name[0:17]}")
ax1.legend()
plt.ylabel("Recflectance [%]")
plt.xlabel("Wavelength [nm]")

# STEP 3
# works

average_start_value = (start_value_list[0] + start_value_list[1] + start_value_list[2]) / 3

print("start value", start_value_list)
print("avargae", average_start_value, len(average_start_value))
average_end_value = (end_value_list[0] + end_value_list[1] + end_value_list[2]) / 3
print("avg end",average_end_value, len(average_end_value))

plt.savefig(f"Spektrum_Einzelmessung_{file_name[0:17]}.png", dpi=1200)
plt.show()

plt.figure()
ax1 = plt.subplot(111)
ax1.plot(average_start_value, label='Start', color='green', linewidth=0.8)
ax1.plot(average_end_value, label='End', color='red', linewidth=0.8)
plt.ylim(0,80)
plt.xlim(420,720)
plt.grid(alpha=0.5)
ax1.set_title(f"Spektrum {file_name[0:17]}")
ax1.legend()
plt.ylabel("Recflectance [%]")
plt.xlabel("Wavelength [nm]")


def plot_confidence_interval(x, values, z=1.96, color='#2187bb', horizontal_line_width=0.25):
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    confidence_interval = z * stdev / np.sqrt(len(values))

    left = x - horizontal_line_width / 2
    top = mean - confidence_interval
    right = x + horizontal_line_width / 2
    bottom = mean + confidence_interval
    plt.plot([x, x], [top, bottom], color=color)
    plt.plot([left, right], [top, top], color=color)
    plt.plot([left, right], [bottom, bottom], color=color)
    plt.plot(x, mean, 'o', color='#f44336')

    return mean, confidence_interval


#for i in range(0, int(len(average_end_value)/20)):
#    data = [start_value_list[0][i * 20], start_value_list[1][i * 20], start_value_list[2][i * 20]]

# plt.xticks([1, 2, 3, 4], ['FF', 'BF', 'FFD', 'BFD'])
# plt.title('Confidence Interval')
# plot_confidence_interval(1, [10, 11, 42, 45, 44])



plt.savefig(f"Spektrum_Mittelwert_{file_name[0:17]}.png", dpi=1200)
plt.show()



# print(start_value_list[0][779.319], start_value_list)
# print(end_value_list[0][20])