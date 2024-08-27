from abc import ABC, abstractmethod
import functools
from uuid import uuid4
from copy import copy

class Module:

    """
    Base class for all modules.

    Modules are the building blocks of the AGOX framework. They are used to define the
    different types of operations that are performed during a global optimization 
    algorithm.

    Parameters:
    -----------
    use_cache : bool
        If True, the module will use a cache to store the results of the methods.
    """
    kwargs = ['surname']

    def __init__(self, use_cache=False, surname=''):
        self.surname = surname
        
        self.use_cache = use_cache
        self.cache_key = str(uuid4())
        self.ray_key = str(uuid4())
        self.self_synchronizing = False

        self.dynamic_attributes = [] # Attributes that can be added and removed.
        self.tracked_attributes = [] # Attributes that the logger will track.
    
    def get_dynamic_attributes(self):
        return {key:self.__dict__.get(key, None) for key in self.dynamic_attributes}

    def add_dynamic_attribute(self, attribute_name):
        self.dynamic_attributes.append(attribute_name)

    def remove_dynamic_attribute(self, attribute_name):
        assert attribute_name in self.__dict__.keys()
        assert attribute_name in self.dynamic_attributes
        del self.dynamic_attributes[self.dynamic_attributes.index(attribute_name)]
    
    def get_tracked_attributes(self):
        attributes = dict()
        for key in self.tracked_attributes:
            try:
                attributes[key] = self.__dict__[key]
            except: # To avoid crashing if the attribute is not yet defined.
                attributes[key] = None
        return attributes
    
    def add_tracked_attribute(self, attribute_name):
        self.tracked_attributes.append(attribute_name)

    @property
    @abstractmethod
    def name(self):
        return NotImplementedError

    @property
    def dynamic_state(self):
        state = len(self.dynamic_attributes) > 0
        return state

    @property
    def __name__(self):
        """
        Defines the name.
        """
        if len(self.dynamic_attributes) > 0:
            last = 'Dynamic'
        else:
            last = ''
        return self.name + self.surname + last

    def find_submodules(self, in_key=None, only_dynamic=False):
        if in_key is None:
            in_key = []

        submodules = {}
        for key, value in self.__dict__.items():
            if issubclass(value.__class__, Module):
                key = in_key + [key]
                if only_dynamic:
                    if value.dynamic_state:                
                        submodules[tuple(key)] = value
                else:
                    submodules[tuple(key)] = value
                submodules.update(value.find_submodules(in_key=key, only_dynamic=only_dynamic))

        return submodules

    def set_for_submodule(self, submodule_keys, value):
        reference = self
        for key in submodule_keys[0:-1]:
            reference = self.__dict__[key]        
        reference.__dict__[submodule_keys[-1]] = value
        

    @classmethod
    def reset_cache_key(clc, func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.cache_key = str(uuid4())            
            return func(self, *args, **kwargs)
        return wrapper

def register_modules(object, modules, name):
    """
    Registers modules as attributes of an object. Used to let Tracker track 
    modules as attributes of modules that are only attributes of other modules.

    Parameters
    ----------
    object : object
        Object to register modules as attributes of.
    modules : list
        List of modules to register.
    name : str
        Name of the modules.

    Returns
    -------
    None.
    """
    for i, module in enumerate(modules):
        setattr(object, f'{name}_{i}', module)

    