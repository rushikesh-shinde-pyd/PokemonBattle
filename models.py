import time
from utils import Generator, decor_iterator


class Manager:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get(self, name):
        return self.data.get(name)

    def count(self):
        return len(self.data)

    @decor_iterator
    def all(self):
        return self.data

    @decor_iterator
    def values_list(self):
        return self.data.keys()


class Base:
    def __init__(self):
        self.id = next(self._id)

    def __init_subclass__(cls):
        cls._id = Generator.get_instance()
        cls.data = {}
        cls.objects = Manager(data=cls.data)


class DamageAgainst(Base):
    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)


class Pokemon(Base):
    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self.data[self.name] = self.__dict__

    def damage_against(self, name):
        return self.damage_against.objects.get(name)

    @classmethod
    def all(cls):
        return [pokemon for pokemon in cls._pokemons.keys()]

    @classmethod
    def get(cls, name):
        pokemon = cls._pokemons.get(name.lower())
        return pokemon.objects if pokemon else None

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class Battle(Base):
    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

        self.id = Generator.get_instance('uuid')
        self.status = 'in_progress'
        self.winner = None
        self.damage = 0
        self.data[self.id] = self.__dict__


    def update(self, kwargs):
        self.__dict__.update(kwargs)


    def calculate_damage(self, switch=False):
        try:
            pokemon1, pokemon2 = (self.pokemon2, self.pokemon1) if switch else (self.pokemon1, self.pokemon2)
            against_type1 = pokemon2['damage_against'][pokemon1['type1']]
            against_type2 = pokemon2['damage_against'][pokemon1['type2']]

            return True, (pokemon1['attack'] / 200) * 100 - (((against_type1 / 4) * 100) + ((against_type2 / 4) * 100))

        except Exception as e:
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e, str(exc_tb.tb_lineno))
            return False, 0


    def start(self):
        status, round_1_damage = self.calculate_damage()
        time.sleep(3)

        if not status:
            self.update({'status': 'failed'})
            return

        status, round_2_damage = self.calculate_damage(True)
        time.sleep(3)

        if not status:
            self.update({'status': 'failed'})
            return

        winner = self.pokemon1 if round_1_damage > round_2_damage else self.pokemon2
        damage = max(round_1_damage, round_2_damage)

        self.update({
            'status':'completed',
            'damage':damage,
            'winner':winner
        })

    def __str__(self):        
        return str(self.id)


    def __repr__(self):
        return str(self.id)
