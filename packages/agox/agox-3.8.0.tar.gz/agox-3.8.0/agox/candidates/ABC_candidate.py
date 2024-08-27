from abc import ABC, abstractmethod
from ase import Atoms
import numpy as np

import functools
from copy import deepcopy
from ase.calculators.singlepoint import SinglePointCalculator

from agox.module import Module
from agox.utils.cache import Cache
    
class CandidateBaseClass(ABC, Atoms, Module):

    """
    Base-class for Candidate objects.

    Parameters
    ------------
    template: ase.Atoms
        Atoms object of the template structure. Does not need to be supplied
        if 'template_indices' are given. 
    template_indices: np.array
        Indices of template atoms. 
    kwargs: 
        Everything that can be supplied to an ASE atoms object, specifically 
        cell, positions and numbers of ALL atoms - including template atoms.
    """

    def __init__(self, template=None, template_indices=None, use_cache=True, **kwargs):
        Atoms.__init__(self, **kwargs) # This means all Atoms-related stuff gets set. 
        Module.__init__(self, use_cache=use_cache)
        self.meta_information = self.info
        
        self.use_cache = use_cache
        self._cache = Cache()

        # Template stuff:        
        if template_indices is not None:
            self.template_indices = template_indices.astype(int)
            self.template = self.get_template()
        elif template is not None:
            self.template = template
            self.template_indices = np.arange(len(template))
        else:
            print('You have not supplied a template, using an empty atoms object without PBC and no specified cell.')
            self.template = Atoms(pbc=self.pbc)            
            self.template_indices = np.arange(0)
        
        self.set_pbc(self.template.get_pbc()) # Inherit PBC's from template.
        
        self.postprocess_immunity = False

        # This will happen eventually when work starts on using multiple templates.
        # But the check doesnt work as intended at the moment.
        # if len(template) > 0:            
        #     assert (self.positions[:len(template)] == template.positions).all(), 'Template and positions do not match'


    @classmethod
    def cache(cls, key):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, atoms, *args, **kwargs):
                if not self.use_cache:
                    return func(self, atoms, *args, **kwargs)
                
                full_key = self.cache_key + '/' + key
                if isinstance(atoms, CandidateBaseClass):
                    value = atoms.get_from_cache(full_key)
                    if value is None:
                        value = func(self, atoms, *args, **kwargs)
                        if atoms.use_cache:
                            atoms.set_to_cache(full_key, value)
                else:
                    value = func(self, atoms, *args, **kwargs)
                    
                return value
            return wrapper
        return decorator
        
    def get_from_cache(self, key):
        if not self.use_cache:
            return None
        
        identifier, value = self._cache.get(key, (None, None))
        if identifier is not None:
            if self.compare_identity(identifier):
                return value
        else:
            return None

    def set_to_cache(self, key, value):
        self._cache.put(key, (self.get_identifier(), value))

    def compare_identity(self, identifier):
        for a,b in zip(identifier, self.get_identifier()):
            equal = (a == b).all()
            if not equal:
                return equal
        return equal

    def get_identifier(self):
        return (self.get_atomic_numbers(), self.get_positions(), self.get_cell())


    def add_meta_information(self, name, value):
        """
        Adds an entry to the meta_information dictionary

        Parameters
        -----------
        name: str (preferably, but can take anything that indexes a dict)
            Key to the dict
        value:
            Value to be set in the dict. 
        """
        self.meta_information[name] = value

    def add_write_key(self,value):
        """
        Adds a write key to the candidates meta information.

        Parameters
        -----------
        value: str
            key to add to the write information

        """

        try:
            keys=self.get_meta_information("write_keys")
            if isinstance(keys, str):
                keys=list(keys.split(" "))
            if value not in keys: 
                keys.append(value)
        except: 
            keys=[value]
        self.add_meta_information("write_keys",keys)

    
    def print_properties(self,writer,iteration):
        keys=self.get_meta_information("write_keys")
        strings_list=[]
        write_string="Energy: "+str(iteration)+"  "+str(self.get_potential_energy())+"  "
        
        if keys is not None:
            for key in keys:
                addendum="["+key+":"+" "+self.get_meta_information(key)+"] "
                if len(write_string)+len(addendum) > 120:  
                    strings_list.append(write_string)
                    write_string = ""
                
                write_string+=addendum
                #self.writer('Energy {:06d}: {}'.format(self.get_iteration_counter(), candidate.get_potential_energy()), flush=True)
        strings_list.append(write_string)
        if strings_list is not None:
            for string in strings_list:
                writer(string,flush=True)


    def get_meta_information(self, name):
        """
        Get from the meta_information dict. 

        Parameters
        -----------
        name: str
            Key to get with. 
        
        Returns
        --------
        value - any type
            A copy of the wanted entry in the dict or None if it is not set. 
        """
        try:
            return self.meta_information.get(name, None).copy()
        except AttributeError: 
            # This catches for example 'int' that dont have a copy method. 
            # Ints won't change in-place, but it perhaps custom classes will. 
            return self.meta_information.get(name, None)

    def get_meta_information_no_copy(self, name):
        """
        Get from the meta_information dict without copying

        Parameters
        -----------
        name: str
            Key to get with. 
        
        Returns
        --------
        value - any type
            The wanted entry in the dict or None if it is not set. 
        """
        return self.meta_information.get(name, None)

    def has_meta_information(self, name):
        """
        Get from the meta_information dict without copying

        Parameters
        -----------
        name: str
            Key to get with.         

        Returns
        --------
        bool
            True if the 'name' is a key to meta_information. 
        """
        return name in self.meta_information.keys()

    def pop_meta_information(self, name):
        """
        Pop from the meta_information dict. 

        Parameters
        -----------
        name: str
            Key to get with. 
        
        Returns
        --------
        value - any type
            The wanted entry in the dict or None if it is not set. 
        """
        return self.meta_information.pop(name, None)

    def reset_meta_information(self):
        """
        Resets meta_information
        """
        self.meta_information = dict()

    def get_template(self) -> Atoms:
        """
        Get the template atoms object. 

        Returns
        --------
        atoms
            Template as an Atoms object. 
        """
        return Atoms(numbers=self.numbers[self.template_indices], positions=self.positions[self.template_indices], cell=self.cell, pbc=self.pbc)

    def copy(self):
        """
        Return a copy of candidate object. 

        Not sure if template needs to be copied, but will do it to be safe.

        Returns
        --------
        candidate
            A copy of the candidate object. 
        """
        candidate = self.__class__(template=self.template.copy(), cell=self.cell, pbc=self.pbc, info=self.info,
                               celldisp=self._celldisp.copy())
        candidate.meta_information = self.meta_information.copy()
        
        candidate.arrays = {}
        for name, a in self.arrays.items():
            candidate.arrays[name] = a.copy()

        candidate.constraints = deepcopy(self.constraints)
        
        return candidate

    def copy_calculator_to(self, atoms):
        '''
        Copy current calculator and attach to the atoms object
        '''
        if self.calc is not None and 'energy' in self.calc.results:
            if 'forces' in self.calc.results:
                calc = SinglePointCalculator(atoms, energy=self.calc.results['energy'],
                                             forces=self.calc.results['forces'])
            else:
                calc = SinglePointCalculator(atoms, energy=self.calc.results['energy'])
            atoms.set_calculator(calc)

    def set_postprocess_immunity(self, state):
        """
        Set postprocess immunity. 

        Parameters
        -----------
        state: bool
            True if Candidate should ignore postprocessor steps. 
        """
        self.postprocess_immunity = state

    def get_postprocess_immunity(self):
        """
        Get postprocess immunity: 

        Returns
        --------
        bool
            True if immune to postprocessing
        """
        return self.postprocess_immunity

    def get_property(self, key):
        """
        Get property from calculator. 

        Parameters
        -----------
        key
            Key used to index calc.get_property

        Returns
        --------
        value
            Value of calc.get.property(key)
        """

        return self.calc.get_property(key)

    def get_template_indices(self):
        """
        Returns
        --------
        np.array
            Array of template indices
        """
        return self.template_indices

    def get_optimize_indices(self) -> np.array:
        """
        Returns
        --------
        np.array
            Indices of of atoms that are part of the search. 
        """
        return np.arange(len(self.template), len(self))

    def get_center_of_geometry(self, all_atoms=False) -> np.array:
        """
        Returns the center of geometry.

        Parameters
        -----------
        all_atoms: bool
            If True all atoms are included, if False only non-template atoms are. 
        """

        if all_atoms:
            return np.mean(self.positions, axis=0).reshape(1, 3)
        else:
            return np.mean(self.positions[self.get_optimize_indices()], axis=0).reshape(1, 3)

    def set_calculator(self, calc):
        """
        "Old" ASE syntax for setting calculator, avoids the annoying warning and 
        uses this better syntax.

        Parameters
        -----------
        calc: calculator
            Calculator to set.
        """
        self.calc = calc

def disable_cache(candidate):
    # Can be either Candidate or Atoms.
    if isinstance(candidate, CandidateBaseClass):
        candidate.use_cache = False

def switch_cache(candidate, state):
    prev_state = False
    if isinstance(candidate, CandidateBaseClass):
        prev_state = candidate.use_cache
        candidate.use_cache = state
    return prev_state
