from MARS_CI.DataTypes import Mat

mat = Mat()
mat.load(input('Lattice? '))
writer = open(input('Where to save?'), 'w')
writer.write(f'{mat.size} {mat.size * (mat.size + 1) // 2}\n')
for i in range(mat.size):
    for j in range(i, mat.size):
        writer.write(f'{i} {j} {mat[i, j]}\n')
