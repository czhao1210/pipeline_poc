import os
import sys
import subprocess
import matplotlib.pyplot as plt
import time
default_graph_name = time.strftime("%Y-%m-%d-%H-%M-%S")

# try:
#     import matplotlib.pyplot as plt
# except:
#     a=subprocess.check_output("python -m pip install install matplotlib --proxy=http://proxy-chain.intel.com:911",shell=True)
#     try:
#         import matplotlib.pyplot as plt
#     except:
#         print("no internet connectivity")
#         sys.exit(1)

def graph_creator(time_count=None,cycle_count=None,file_path=None,file_name=None):
    """
    :param time_count: mins time taken for the cycle [10, 4, 20, 25, 30, 35, 40, 12, 13, 14, 15]
    :param cycle_count: number of cycle [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    :param file_path: path where the file has to be stored
    :param file_name: name of the file, if nothing is passed based on the timestamp file will be generated
    :return: file_name in default mode
    """
    time_count = time_count
    # with open("cycle_count.txt",'r') as myfile1:
    #     for line in myfile1:
    #         time_count.extend(map(int, line.split(',')))
    left = time_count
    cycle_count = cycle_count
    # with open("cycle_time.txt",'r') as myfile:
    #     for line in myfile:
    #         data.extend(map(int, line.split(',')))
    height = cycle_count
    plt.bar(left, height, tick_label=left, align='center', alpha=0.9,
            width=0.8,
            color=['green', 'red', 'blue', 'orange', 'pink', 'black', 'yellow', 'grey', 'purple', 'violet', 'brown'])
    plt.title('Cycling Time Taken')
    plt.xlabel('No of Cycle Count', fontsize=10)
    plt.ylabel('Minutes Taken For one complete Cycle', fontsize=10)
    for i in range(len(height)):
        plt.text(x=left[i], y=height[i], s=height[i], size=9)
    # plt.show()  only to view
    if file_name == None:
        print("Plot Saved by Default In This Name -->", default_graph_name)
        if file_path == None:
            plt.savefig(default_graph_name)
        else:
            print(file_path+file_name)
            plt.savefig(file_path + default_graph_name)
    else:
        plt.savefig(file_path+file_name)

#graph_creator(time_count=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],cycle_count=[10, 4, 20, 25, 30, 35, 40, 12, 13, 14, 15],file_path=r"C:\Users\ssuresh2\Music\cycling_bmc\\",file_name="tesla.png")