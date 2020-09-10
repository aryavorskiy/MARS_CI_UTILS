import csv

from MARS_CI.DataTypes import Mat

########################################################
# Lattice format converter by Yxbcvn410                #
# Input:                                               #
# CSV files to read lattice data;                      #
# Filename to export lattice                           #
# Output: None                                         #
########################################################

mat_vals = [[float(x) for x in line] for line in csv.reader(open(input('Mat? ')))]
lin_vals = [float(line[0]) for line in csv.reader(open(input('Lin? ')))]
mat = Mat()
mat.load_values(mat_vals, lin_vals)
mat.dump(input('Where to save?'), 'lattice')
print('Done')
