import matplotlib.pyplot as plot
from matplotlib import rcParams
rcParams['font.family'] = 'serif'
#rcParams['font.size'] = '20'
#rcParams['text.usetex'] = 'true'
#rcParams['font.serif'] = ['Liberation']

def parse(datafile):
    raw_data = open(datafile, 'r').read()
    return [float(line.split(':')[1].split(' ')[2][1:-1]) for line in raw_data.split('\n')[2:] if line != '']

results = [parse('d%i_p16.txt' % i) for i in [5, 6, 7]]
proof = [i[0]*1000 for i in results]
validation = [i[1]*1000 for i in results]

width = 0.35
labels = ['6', '7', '8']
fig, ax = plot.subplots()
ax.bar(labels, proof, width, label='Root hash computation')
ax.bar(labels, validation, width, bottom=proof, label='STR validation')
ax.set_xlabel('Merkle tree depth')
ax.set_ylabel('Duration [ms]')
ax.legend()
plot.savefig('plot.pdf')
plot.show()

print(results)
print(proof)
print(validation)
