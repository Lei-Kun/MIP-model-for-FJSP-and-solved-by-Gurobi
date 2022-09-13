import numpy as np
import time
import os

from DataRead import getdata
from FJSPMIPModel import MIPModel

filename='./FJSSPinstances/2b_Hurink_edata\HurinkEdata1.fjs'
Data=getdata(filename)
print('data_j',Data['J'],Data['OJ'])
print('DATA_operations_machines',Data['operations_machines'])
print('DATA_operations_machines',Data['operations_times'])

num_operation = []
for i in Data['J']:
    num_operation.append(Data['OJ'][i][-1])
print(num_operation)
num_operation_max = np.array(num_operation).max()

time_window = np.zeros(shape=(Data['n'],num_operation_max,Data['m']))

for i in range(Data['n']):
    for j in range(Data['m']):
        mchForJob = Data['operations_machines'][(i+1,j+1)]
        for k in mchForJob:
            time_window[i][j][k-1] = Data['operations_times'][(i+1,j+1,k)]
print(time_window)





# n=Data['n']
# m=Data['m']
# J=Data['J']
# OJ=Data['OJ']
# operations_machines=Data['operations_machines']
# operations_times=Data['operations_times']
# largeM=Data['largeM']

#mipmodel=MIPModel(Data)
#ipmodel.optimize()
