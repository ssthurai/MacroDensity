from __future__ import print_function
import unittest
import sys
import os
import numpy as np

sys.path.insert(1, '/Users/keith/SCRIPTS/MacroDensity/MacroDensity')
import macrodensity as md

test_dir = os.path.abspath(os.path.dirname(__file__))


class TestReadingFunctions(unittest.TestCase):
    ''' Test the code for reading in charge and density files'''

    def test_read_vasp(self):
        '''Test the function for reading CHGCAR/LOCPOT'''
        charge, ngx, ngy, ngz, lattice = md.read_vasp_density('CHGCAR.test')
        self.assertEqual(charge[0], -.76010173913E+01)
        self.assertEqual(charge[56 * 56 * 56 -1], -4.4496715627)
        self.assertEqual(lattice[0,0], 2.7150000)
        self.assertEqual(ngx, 56)

    def test_matrix_2_abc(self):
        '''Test the function for converting the lattice to abc, alpha,beta, gamma format'''
        lattice = np.asarray([[2.715, 2.715, 0.], [0., 2.715, 2.715], [2.715, 0., 2.715]])
        a, b, c, a_vec, b_vec, c_vec = md.matrix_2_abc(lattice)
        self.assertAlmostEqual(a, 3.8395898218429529)
        self.assertAlmostEqual(b, 3.8395898218429529)
        self.assertAlmostEqual(c, 3.8395898218429529)

    def test_density_2_grid(self):
        '''Test the function for projecting the potential onto a grid'''
        charge, ngx, ngy, ngz, lattice = md.read_vasp_density('CHGCAR.test')
        grid_pot, electrons = md.density_2_grid(charge, ngx, ngy, ngz)
        self.assertAlmostEqual(grid_pot[0, 0, 0], - .76010173913E+01)
        self.assertAlmostEqual(grid_pot[55, 55, 55], -4.4496715627)
        self.assertAlmostEqual(electrons, 8.00000, places=4)


class TestAveragingFunctions(unittest.TestCase):
    '''Test various functions for manipulating and mesuring the density'''

    def test_planar_average(self):
        ''' Test the code for averaging the density'''
        test_grid = np.zeros(shape=(3,3,3))
        for i in range(3):
            test_grid[i, :, 0] = float(i)
        planar = md.planar_average(test_grid, 3, 3, 3)
        self.assertAlmostEqual(planar[0], 1.0)
        planar = md.planar_average(test_grid, 3, 3, 3, axis='x')
        self.assertAlmostEqual(planar[2], 0.66666667)

    def test_cube_potential(self):
        '''Test the cube_potential function'''
        test_grid = np.zeros(shape=(5, 5, 5))
        for i in range(5):
            for j in range(5):
                for k in range(5):
                    test_grid[i, j, k] = float(i * j * k)

        potential, variance = md.cube_potential([0, 0, 0], [0, 0, 0], [2, 2, 2], test_grid, 5, 5, 5)
        self.assertAlmostEqual(potential, 0.125)
        self.assertAlmostEqual(variance, 0.109375)
        potential, variance = md.cube_potential([1, 1, 1], [0, 0, 0], [2, 2, 2], test_grid, 5, 5, 5)
        potential, variance = md.cube_potential([1, 1, 1], [0, 0, 0], [3, 3, 3], test_grid, 5, 5, 5)
        self.assertAlmostEqual(potential, 1.0)
        self.assertAlmostEqual(variance, 3.6296296296296298)


class TestGeometryFunctions(unittest.TestCase):
    '''Test the functions that do geometry and trig'''
    def test_gradient_magnitude(self):
        '''Test the function for returning the magnitude of gradient at a voxel'''
        grid = np.zeros(shape=(3, 3, 3))
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    grid[i, j, k] = i * j * k
        gx, gy, gz = np.gradient(grid)
        magnitudes = md.gradient_magnitude(gx, gy, gz)
        self.assertEqual(magnitudes[1, 1, 1], 1.7320508075688772)
        self.assertEqual(magnitudes[2, 2, 2], 6.9282032302755088)

    def test_macroscopic_average(self):
        '''Test the macroscopic averaging function'''
        f = 2.
        fs = 100
        x = np.arange(fs)
        potential = [np.sin(2 * np.pi * f * (i/float(fs))) for i in np.arange(fs)]
        macro = md.macroscopic_average(potential, 50, 1)
        self.assertAlmostEqual(macro[20], 0.)

if __name__ == '__main__':
    unittest.main()