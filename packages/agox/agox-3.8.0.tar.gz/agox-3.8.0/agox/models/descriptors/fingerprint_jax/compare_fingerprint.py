from ase.build import molecule
import matplotlib.pyplot as plt

from agox.models.descriptors.fingerprint_jax.fingerprint_jax import JaxFingerprint
import numpy as np

def main():

    #atoms = molecule('CH3CH2OH')
    atoms = molecule('C6H6')
    atoms.center(5)

    print(atoms.get_pbc(), len(atoms), atoms.get_chemical_formula())

    use_angular = True
    eta = 5
    r_cut_all = 5.0
    n_bins = 30
    descriptor = JaxFingerprint.from_atoms(atoms, r_cut_radial=r_cut_all, r_cut_angular=r_cut_all,
                                         n_bins_radial=n_bins, use_angular=use_angular, eta=eta)

    print(descriptor.pairs)
    print(descriptor.triplets)

    features = descriptor.get_features(atoms).flatten()

    from agox.models.descriptors.fingerprint_cython.angular_fingerprintFeature_cy import Angular_Fingerprint
    descriptor_agox = Angular_Fingerprint(atoms, Rc1=r_cut_all, Rc2=r_cut_all, binwidth1=r_cut_all/n_bins, nsigma=10,
                                        sigma1=0.2, sigma2=0.2, Nbins2=n_bins,
                                        eta=eta, gamma=2, use_angular=use_angular)
    features_agox = descriptor_agox.get_feature(atoms)

    plt.switch_backend('Agg')
    _, ax = plt.subplots(figsize=(6,4))
    x = np.arange(len(features))
    y1 = 2*features
    y2 = -features_agox
    ax.bar(x, y1, width=0.5)
    ax.bar(x, y2, width=0.5)
    ax.text(0, 10, 'Jax', color='C0')
    ax.text(0, -10, 'Cython', color='C1')
    
    x_bins = np.arange(0, len(features)+1, n_bins)
    
    labels = ['HH', 'HC', 'CC', 'HHH', 'HHC', 'HCC', 'CHH', 'CHC', 'CCC']
    for i in range(len(labels)):
        x = (x_bins[i+1] + x_bins[i]) / 2
        y = -25
        ax.text(x, y, labels[i], ha='center')
    ax.set_xticks(x_bins)
    ax.set_xticklabels(x_bins)

    ax.set_xlabel('Feature index')
    ax.set_ylabel('Feature value')

    ax.set_title('Fingerprint of C6H6 molecule')
    
    
    plt.savefig('fig-fingerprint-C6H6.png', dpi=200, bbox_inches='tight')

def compare_feature_computation_time(use_angular = True, calculate_gradient = False):
    print('compare_feature_computation_time')

    from tqdm import trange
    from ase.spacegroup import crystal

    a = 4.6
    c = 2.95
    rutile = crystal(['Ti', 'O'], basis=[(0, 0, 0), (0.3, 0.3, 0.0)],
                    spacegroup=136, cellpar=[a, a, c, 90, 90, 90])

    mol = molecule('CH3CH2OH')
    mol.center(5)

    systems = [mol, rutile]
    
    
    eta = 5
    r_cut_all = 5.0
    n_bins = 30

    n_runs = 1000

    for atoms in systems:
        print(atoms.get_pbc(), len(atoms), atoms.get_chemical_formula())
        trajs = []
        descriptor = JaxFingerprint.from_atoms(atoms, r_cut_radial=r_cut_all, r_cut_angular=r_cut_all,
                                         n_bins_radial=n_bins, use_angular=use_angular, eta=eta)

        from agox.models.descriptors.fingerprint_cython.angular_fingerprintFeature_cy import Angular_Fingerprint
        descriptor_cython = Angular_Fingerprint(atoms, Rc1=r_cut_all, Rc2=r_cut_all, binwidth1=r_cut_all/n_bins, nsigma=10,
                                            sigma1=0.2, sigma2=0.2, Nbins2=n_bins,
                                            eta=eta, gamma=2, use_angular=use_angular)

        for i in range(n_runs):
            new_atoms = atoms.copy()
            new_atoms.rattle(0.01, seed=i)
            trajs.append(new_atoms)
        
        print('jax-Fingerprint')
        for i in trange(n_runs):
            atoms.set_positions(trajs[i].get_positions())
            features = descriptor.create_features(atoms)
        
        print('cython-Fingerprint')
        for i in trange(n_runs):
            atoms.set_positions(trajs[i].get_positions())
            features = descriptor_cython.get_feature(atoms)
            if calculate_gradient:
                feature_grad = descriptor_cython.get_featureGradient(atoms)

if __name__ == '__main__':
    main()
    compare_feature_computation_time()
