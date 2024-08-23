import numpy as np
import scipy.linalg as ln


class PauliBasis():
    '''
    A class to represent Pauli's spin basis.
    '''
    def _init__(self):
        return self

    def matrices(self):
        '''

        Returns:
            a list of 4 :math:`2\\times 2` matrices corresponding to :math:`I_2, \\sigma_x, \\sigma_y, \\sigma_z`
        '''
        sigx = np.array([[0, 1], [1, 0]])
        sigy = np.array([[0, -1j], [1j, 0]])
        sigz = np.array([[1, 0], [0, -1]])
        Id = np.eye(2)
        return np.array([Id, sigx, sigy, sigz])

    def decompose(self, A):
        '''
        Decomposes given non-singular :math:`2\\times 2` matrix in the Pauli basis.

        Args:
            A: :math:`2\\times 2` matrix to be decomposed.

        Returns:
            list of 4 components.
        '''
        assert np.array(A).shape==(2,2), "Not a 2x2 matrix to decompose in pauli basis."
        l = self.matrices()
        M = np.zeros((4,4), dtype=complex)
        for i in range(4):
            for j in range(4):
                M[i, j] = l[j].flatten()[i]
        try:
            return ln.inv(M)@(np.array(A).flatten())
        except ln.LinAlgError:
            raise(ln.LinAlgError, "Matrix singular! Unique decomposition doesn't exist!")

class GellMannBasis():
    def _init__(self):
        self.structureConstants()
        return self

    def matrices(self):
        I = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        l1 = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
        l2 = np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]])
        l3 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]])
        l4 = np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]])
        l5 = np.array([[0, 0,-1j], [0, 0, 0], [1j, 0, 0]])
        l6 = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
        l7 = np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]])
        l8 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]])/np.sqrt(3)
        return np.array([I, l1, l2, l3, l4, l5, l6, l7, l8])

    def structureConstants(self):
        f = np.zeros((8, 8, 8), dtype=complex)
        l = self.matrices()
        for i in range(8):
            for j in range(8):
                for k in range(8):
                    f[i,j,k] = -1j*np.trace(np.dot(np.dot(l[i+1], l[j+1]), l[k+1]) - np.dot(np.dot(l[j+1], l[i+1]), l[k+1]))/4
        self.f = f
        return self.f

    def structureConstant(self, i, j, k):
        return self.f[i-1, j-1, k-1]

    def decompose(self, A):
        l = self.matrices()
        result = np.zeros(9, dtype=complex)
        result[0] = np.trace(A)/3
        A = A-np.trace(A)*np.eye(3)/3
        for i in range(1, len(l)):
            result[i] = np.trace(A@l[i])/2 # Since, Gellmann matrices are trace normalized to 2
        return result

    def compose(self, decomposition):
        assert len(decomposition)==9, 'Provided decomposition is not of size 9!'
        l = self.matrices()
        result = np.zeros((3,3), dtype=complex)
        for i in range(9):
            result += decomposition[i]*l[i]
        return result