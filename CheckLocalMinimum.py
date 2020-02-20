from Modules.DataTypes import Mat

##########################################################################
# Local minimum checker by aryavorskiy                                   #
# Input: Mat file, spin values                                           #
# Output: Hamiltonian (Respecting diagonal elements), local minimum info #
##########################################################################

mat = Mat()
mat.load(input('Mat filename? '))
while True:
    spins = [float(k) for k in input('Spins? ').split()]
    print(f'Hamiltonian: {mat.hamiltonian(spins)}')
    is_local_minimum = mat.is_local_minimum(spins)
    print({True: 'Local minimum', False: 'Not local minimum'}[is_local_minimum])
