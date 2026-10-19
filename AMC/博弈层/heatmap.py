import json
import matplotlib.pyplot as plt
import numpy as np
font = {'family':  'Times New Roman',
        'color': 'black',
        'weight': 'normal',
        'size': 30,
        }

# r=3, k=0.6下绘制α和β的热力图

filename = "alpha_betaa"
f = open(".\\saves\\{}.json".format(filename))
data = json.load(f)
Alpha = np.arange(0, 3.1, 0.1)  # 惩罚成本
Beta = np.arange(0, 1.1, 0.1)  # 背叛者将这一轮中额外获得的beta收益给裁判
matrix = []
#SIGMA=SIGMA[::-1]
for alpha in Alpha:
    matrix.append(data["{:.2f}".format(alpha)])
for k in range(len(Alpha)):
    Alpha[k] = round(Alpha[k], 2)
for k in range(len(Beta)):
    Beta[k] = round(Beta[k], 2)
colname = list(Alpha)
temp = []
for i in range(len(matrix)):
    temp.append(np.array(matrix[i]))
z = np.array(temp)
z = z.T
z = z[::-1]
#z=matrix
xs, ys = np.meshgrid(Alpha, Beta)
plt.figure(figsize=(12, 11))
plt.imshow(z, cmap=plt.cm.jet, extent=(0, 3, 0, 1), interpolation='gaussian', aspect='auto', vmin=0, vmax=1)
cb=plt.colorbar()
cb.set_label(label="$f_c$", fontdict=font, rotation=0)
cb.ax.tick_params(labelsize=25)
plt.xlabel('$\u03B1$', fontdict=font)
plt.ylabel('$\u03B2$', fontdict=font)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.savefig(".\\saves\\"+filename+".pdf", dpi=400)
plt.show()