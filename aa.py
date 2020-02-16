
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('src/data/results/aa.csv',usecols=["Player 1 Wins","Player 2 Wins","Nobody Wins"])

df.plot.bar()
plt.xlabel('Iterations')
plt.ylabel('Games')
plt.savefig('output.png')