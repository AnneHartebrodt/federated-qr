import os
import numpy as np
bytes_sent = []
Rprec = []
Qprec = []
elapsed = []
for files in os.listdir('logs'):
    with open(os.path.join('logs', files), 'r') as handle:
        for line in handle:
            if 'bytes sent' in line:
                bytes_sent.append(int(line.split('bytes sent: ')[1].strip()))
                
            if 'R:' in line:
                Rprec.append(float(line.split('R: ')[1].strip()))
            if 'Q:' in line:
                Qprec.append(float(line.split('Q: ')[1].strip()))
print(Qprec)
print(Rprec)

print('Average bytes sent:' + str(np.mean(bytes_sent)))
print('Average Q error: ' + str(np.nanmean(Qprec)))
print('Average R error: ' + str(np.nanmean(Rprec)))
