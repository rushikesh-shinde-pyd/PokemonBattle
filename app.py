import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, url_for
from flask_caching import Cache
import json
import threading
import sys
import uuid
import pandas as pd
from models import Pokemon, Battle, DamageAgainst
from constants import MAX_PER_PAGE, BATTLE_STATUSES, CACHE_TTL
from itertools import islice
from fuzzywuzzy import process


app = Flask(__name__)

# Configure caching
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_DEFAULT_TIMEOUT'] = CACHE_TTL

# Initialize cache
cache = Cache(app)


def get_closest_pokemon_name(query, threshold=80):
    if Pokemon.objects.count():
        names = Pokemon.objects.values_list()
        match, score = process.extractOne(query, names)
        return match if score >= threshold else None
    raise ValueError('No data available.')


@app.route('/v1/battle')
def battle():
    """
    Initiates a battle between two Pokémon.

    Expects JSON body with 'pokemon1' and 'pokemon2' fields.
    Uses fuzzy matching to find closest Pokémon names.
    Runs the battle logic in a separate thread.
    """
    try:
        # Load and validate JSON data
        data = request.get_json()

        if 'pokemon1' not in data or 'pokemon2' not in data:
            return jsonify({'error': 'Both pokemon1 and pokemon2 fields are required.'}), 400

        pokemon1 = data['pokemon1']
        pokemon2 = data['pokemon2']

        # Validate that Pokémon names are strings
        if not isinstance(pokemon1, str) or not isinstance(pokemon2, str):
            return jsonify({'error': 'pokemon1 and pokemon2 must be strings.'}), 400

        pokemon1, pokemon2 = pokemon1.lower(), pokemon2.lower()

        # Use fuzzy matching to find the closest Pokémon names
        closest_pokemon1 = get_closest_pokemon_name(pokemon1)
        closest_pokemon2 = get_closest_pokemon_name(pokemon2)

        if not closest_pokemon1 or not closest_pokemon2:
            return jsonify({'error': 'One or both Pokemon names are unrecognized.'}), 404

        # Prevent self-battles
        if pokemon1 == pokemon2:
            return jsonify({'error': 'A Pokemon cannot battle itself.'}), 400
        
        pokemon1 = Pokemon.objects.get(name=closest_pokemon1)
        pokemon2 = Pokemon.objects.get(name=closest_pokemon2)

        # Create and start the battle
        battle = Battle(pokemon1=pokemon1, pokemon2=pokemon2)
        thread = threading.Thread(target=battle.start)
        thread.start()

        return jsonify({'battle_id': str(battle.id)}), 201

    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        app.logger.error(f'{e} at {exc_tb.tb_lineno}')
        return jsonify({'error': 'Internal server error.'}), 500

@cache.cached(query_string=True)
@app.route('/v1/get_battle_status')
def get_battle_status():
    """
    Retrieves the status of a specific battle.

    Expects 'battle_id' as a query parameter.
    Validates if the battle_id is a valid UUID.
    """
    try:
        battle_id = request.args.get('battle_id')

        if not battle_id:
            return jsonify({'error': 'battle_id field is required.'}), 400

        try:
            battle_uuid = uuid.UUID(battle_id)
        except ValueError:
            return jsonify({'error': 'Invalid battle_id format. It must be a valid UUID.'}), 400

        battle = Battle.objects.get(battle_uuid)
        if not battle:
            return jsonify({'error': f'Battle with id {battle_id} not found.'}), 404


        status = battle.get('status')
        response = {
            'status': BATTLE_STATUSES.get(status)
        }

        if status in ('in_progress', 'failed'):
            response['result'] = None
        else:
            response['result'] = {
                'winner': battle.get('winner').get('name'),
                'damage': battle.get('damage')
            }

        return jsonify(response), 200

    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON.'}), 400
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        app.logger.error(f'{e} at {exc_tb.tb_lineno}')
        return jsonify({'error': 'Internal server error.'}), 500

@app.route('/v1/pokemons')
@cache.cached(query_string=True)
def pokemon_list():
    """
    Retrieves a paginated list of Pokémon.

    Supports pagination via 'page' and 'per_page' query parameters.
    Caches results to optimize performance.
    """
    try:
        # Retrieve and validate pagination parameters
        page = int(request.args.get('page', 1))
        per_page = min(MAX_PER_PAGE, int(request.args.get('per_page', 10)))

        pokemons = Pokemon.objects.values_list()

        # Pagination logic
        start = (page - 1) * per_page
        end = start + per_page
        paginated_pokemons = list(islice(pokemons, start, end))
        total = Pokemon.objects.count()
        pages = (total + per_page - 1) // per_page

        # Generate pagination links
        def create_url(page_number):
            return url_for('pokemon_list', page=page_number, per_page=per_page, _external=True)

        response = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "data": paginated_pokemons,
            "links": {
                "first": create_url(1),
                "last": create_url(pages),
                "prev": create_url(page - 1) if page > 1 else None,
                "next": create_url(page + 1) if page < pages else None,
            }
        }

        return jsonify(response), 200

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        app.logger.error(f'{e} at {exc_tb.tb_lineno}')
        return jsonify({'error': 'Internal server error.'}), 500


def load_pokemon_data(file_path):
    """
    Loads Pokémon data from a CSV file.

    Parses each row to create a Pokémon object and adds it to the Pokémon list.
    """
    try:
        df = pd.read_csv(file_path)
        pokemon_list = []

        for _, row in df.iterrows():
            damage_obj = DamageAgainst(
                bug=row['against_bug'],
                dark=row['against_dark'],
                dragon=row['against_dragon'],
                electric=row['against_electric'],
                fairy=row['against_fairy'],
                fight=row['against_fight'],
                fire=row['against_fire'],
                flying=row['against_flying'],
                ghost=row['against_ghost'],
                grass=row['against_grass'],
                ground=row['against_ground'],
                ice=row['against_ice'],
                normal=row['against_normal'],
                poison=row['against_poison'],
                psychic=row['against_psychic'],
                rock=row['against_rock'],
                steel=row['against_steel'],
                water=row['against_water']
            )

            pokemon = Pokemon(
                name=row['name'], 
                type1=row['type1'],
                type2=row['type2'],
                attack=row['attack'],
                damage_against=damage_obj.__dict__
            )

            pokemon_list.append(pokemon)

        return pokemon_list

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        app.logger.error(f'{e} at {exc_tb.tb_lineno}')


def setup_logger():
    log_level = logging.DEBUG
    file_handler = RotatingFileHandler('log/app.log', maxBytes=10000, backupCount=3)
    file_handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)


setup_logger()
load_pokemon_data('files/pokemon.csv')


if __name__ == '__main__':
    app.run(debug=True)
