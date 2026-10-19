import json
import matplotlib.pyplot as plt
import numpy as np
filename="r_alphaaa"
f=open(".\\saves\\{}.json".format(filename))
data=json.load(f)
#R = np.arange(1.5, 6.1, 0.2)
#Beta = [0.2, 0.3, 0.4, 0.6, 0.8]
#Alpha = [0.5, 0.8, 1.0, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5]
Alpha = [0.5, 1.0, 1.5, 3.0]
R = np.arange(1.5, 6.5, 0.5)

#Alpha = [0.5, 0.8, 1.0, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5]
#colors=['red', 'green', 'blue', 'black']
colors = ['red', 'green', 'blue', 'black', 'yellow', 'orange', 'purple', 'magenta', 'gray']
#markers=['o', 's', 'p', '^', 'v', 'd']
plt.figure(figsize=(8, 8))
for i in range(4):
    plt.plot(R, data["{:.2f}".format(Alpha[i])][0:50], lw=1, marker='o', markersize=10, color=colors[i], label=("α = " + str(Alpha[i])))
plt.xlabel("$r$", fontsize=22)
plt.ylabel("$f_c$", fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.ylim([-0.1, 1.1])
plt.legend(fontsize=20, loc='best')
plt.savefig(".\\saves\\{}.pdf".format(filename), dpi=400)
plt.show()