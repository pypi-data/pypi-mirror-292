import numpy as np
from ase.optimize import BFGS
from numpy.linalg import eigh

class SafeBFGS(BFGS):

    def step(self, f=None):
        atoms = self.atoms

        if f is None:
            f = atoms.get_forces()

        r = atoms.get_positions()
        f = f.reshape(-1)
        self.update(r.flat, f, self.r0, self.f0)
        omega, V = eigh(self.H)

        if not np.all(np.fabs(omega) > 0):
            # Hessian is singular - Probably due a bad step taken with very large 
            # force. This just resets the Hessian. 
            self.H = np.eye(3 * len(self.atoms)) * self.alpha
            omega, V = eigh(self.H)

        dr = np.dot(V, np.dot(f, V) / np.fabs(omega)).reshape((-1, 3))
        steplengths = (dr**2).sum(1)**0.5
        dr = self.determine_step(dr, steplengths)
        atoms.set_positions(r + dr)
        self.r0 = r.flat.copy()
        self.f0 = f.copy()
        self.dump((self.H, self.r0, self.f0, self.maxstep))

