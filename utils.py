from abc import ABC, abstractmethod
from constants import MAX_ID
import uuid
from functools import wraps


def decor_iterator(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return (i for i in func(*args, **kwargs))

    return inner


class GeneratorBase(ABC):
    @abstractmethod
    def generate(self): pass


class IDGenerator(GeneratorBase):
    def generate(self):
        return (number for number in range(MAX_ID))


class UUIDGenerator(GeneratorBase):
    def generate(self):
        return uuid.uuid4()


class Generator:    
    formats = {
        'int': IDGenerator,
        'uuid': UUIDGenerator
    }

    @classmethod
    def get_instance(cls, _format='int'):
        _instance = cls.formats.get(_format)

        if _instance:
            return _instance().generate()
        else:
            raise ValueError(f'Unsupported format {_format}.')
        
