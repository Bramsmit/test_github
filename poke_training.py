import requests
import time
import json
from typing import Dict, List, Optional

class PokemonAPI:
    def __init__(self):
        # Base URL for all API requests
        self.base_url = "https://pokeapi.co/api/v2"
        # Keep track of our last request time to respect rate limits
        self.last_request_time = 0
        
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """
        Helper method to make API requests with rate limiting.
        Ensures we wait at least 1 second between requests.
        """
        # Calculate time since last request
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # If less than 1 second has passed, wait
        if time_since_last_request < 1:
            time.sleep(1 - time_since_last_request)
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: Status code {response.status_code} for URL: {url}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def get_pokemon(self, name_or_id: str) -> Optional[Dict]:
        """Get detailed information about a specific Pokémon."""
        return self._make_request(f"pokemon/{str(name_or_id).lower()}")
    
    def get_pokemon_species(self, name_or_id: str) -> Optional[Dict]:
        """Get species-specific information about a Pokémon."""
        return self._make_request(f"pokemon-species/{str(name_or_id).lower()}")
    
    def get_ability(self, name_or_id: str) -> Optional[Dict]:
        """Get information about a specific ability."""
        return self._make_request(f"ability/{str(name_or_id).lower()}")
    
    def get_type(self, name_or_id: str) -> Optional[Dict]:
        """Get information about a specific Pokémon type."""
        return self._make_request(f"type/{str(name_or_id).lower()}")

def print_pokemon_summary(pokemon_data: Dict):
    """Print a nicely formatted summary of a Pokémon."""
    print("\n=== Pokémon Summary ===")
    print(f"Name: {pokemon_data['name'].title()}")
    print(f"Height: {pokemon_data['height']/10} meters")
    print(f"Weight: {pokemon_data['weight']/10} kg")
    print("\nTypes:", ", ".join(t['type']['name'] for t in pokemon_data['types']))
    print("\nAbilities:")
    for ability in pokemon_data['abilities']:
        print(f"- {ability['ability']['name'].replace('-', ' ').title()}")
    print("\nBase Stats:")
    for stat in pokemon_data['stats']:
        print(f"- {stat['stat']['name']}: {stat['base_stat']}")

# Example usage and practice exercises
def practice_exercises():
    api = PokemonAPI()
    
    # Exercise 1: Get and display information about your favorite Pokémon
    print("\nExercise 1: Get information about a Pokémon")
    pokemon_name = input("Enter a Pokémon name: ")
    pokemon_data = api.get_pokemon(pokemon_name)
    if pokemon_data:
        print_pokemon_summary(pokemon_data)
    
    # Exercise 2: Compare two Pokémon
    print("\nExercise 2: Compare two Pokémon")
    pokemon1 = input("Enter first Pokémon name: ")
    pokemon2 = input("Enter second Pokémon name: ")
    
    data1 = api.get_pokemon(pokemon1)
    data2 = api.get_pokemon(pokemon2)
    
    if data1 and data2:
        # Compare their stats
        print(f"\nComparing {pokemon1.title()} vs {pokemon2.title()}")
        print("\nStats Comparison:")
        for stat1, stat2 in zip(data1['stats'], data2['stats']):
            stat_name = stat1['stat']['name']
            val1 = stat1['base_stat']
            val2 = stat2['base_stat']
            winner = "===" if val1 == val2 else ">>>" if val1 > val2 else "<<<"
            print(f"{stat_name}: {val1} {winner} {val2}")
    
    # Exercise 3: Explore a Pokémon's abilities
    print("\nExercise 3: Explore abilities")
    if pokemon_data:
        print("\nChoose an ability to explore:")
        for i, ability in enumerate(pokemon_data['abilities'], 1):
            print(f"{i}. {ability['ability']['name']}")
        
        choice = int(input("Enter the number of the ability: ")) - 1
        ability_data = api.get_ability(pokemon_data['abilities'][choice]['ability']['name'])
        
        if ability_data:
            print("\nAbility Details:")
            print(f"Name: {ability_data['name'].title()}")
            # Find English effect entry
            effect_entry = next((entry for entry in ability_data['effect_entries'] 
                               if entry['language']['name'] == 'en'), None)
            if effect_entry:
                print(f"Effect: {effect_entry['effect']}")

if __name__ == "__main__":
    practice_exercises()

def analyze_type_advantages(api, pokemon_name):
    pokemon_data = api.get_pokemon(pokemon_name)
    if not pokemon_data:
        return
    
    print(f"\nAnalyzing type advantages for {pokemon_name.title()}")
    
    # Get type data for each of the Pokémon's types
    pokemon_types = [t['type']['name'] for t in pokemon_data['types']]
    
    weaknesses = set()
    resistances = set()
    immunities = set()
    
    for ptype in pokemon_types:
        type_data = api.get_type(ptype)
        if type_data:
            damage_relations = type_data['damage_relations']
            
            # Add weaknesses (2x damage)
            for entry in damage_relations['double_damage_from']:
                weaknesses.add(entry['name'])
                
            # Add resistances (0.5x damage)
            for entry in damage_relations['half_damage_from']:
                resistances.add(entry['name'])
                
            # Add immunities (0x damage)
            for entry in damage_relations['no_damage_from']:
                immunities.add(entry['name'])
    
    print("\nType Analysis:")
    print(f"Types: {', '.join(pokemon_types)}")
    print(f"Weaknesses: {', '.join(weaknesses)}")
    print(f"Resistances: {', '.join(resistances)}")
    print(f"Immunities: {', '.join(immunities)}")
