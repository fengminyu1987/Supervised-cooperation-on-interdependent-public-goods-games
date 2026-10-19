import json
import matplotlib.pyplot as plt
import numpy as np
filename="r_beta"
f=open(".\\saves\\{}.json".format(filename))
data=json.load(f)
R = np.arange(1.5, 6.5, 0.2)
Beta = [0.3, 0.5, 0.7, 0.9]
colors = ['red', 'green', 'blue', 'black', 'yellow', 'orange', 'purple', 'magenta', 'gray']
markers=['o', 's', 'p', '^', 'v', 'd']
plt.figure(figsize=(8, 8))
for i in range(4):
    plt.plot(R, data["{:.2f}".format(Beta[i])][0:50], lw=1, marker=markers[i], markersize=10, color=colors[i], label=("β = " + str(Beta[i])))
plt.xlabel("$r$", fontsize=22)
plt.ylabel("$f_c$", fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.ylim([-0.1, 1.1])
plt.legend(fontsize=20, loc='best')
plt.savefig(".\\saves\\{}.pdf".format(filename), dpi=400)
plt.show()