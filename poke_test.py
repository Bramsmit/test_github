import requests
import time
from typing import List, Dict

class PokemonListFetcher:
    def __init__(self):
        # Base URL for the PokéAPI
        self.base_url = "https://pokeapi.co/api/v2"
        # We'll keep track of request timing to respect rate limits
        self.last_request_time = 0

    def wait_if_needed(self):
        """
        Ensures we don't overwhelm the API by waiting between requests.
        The PokéAPI asks users to be considerate with request rates.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < 1:
            time.sleep(1 - time_since_last_request)
        
        self.last_request_time = current_time

    def get_all_pokemon(self) -> List[Dict]:
        """
        Fetches a complete list of all Pokémon from the API.
        Returns a list of dictionaries containing Pokémon names and URLs.
        """
        # Start with the first page of results
        url = f"{self.base_url}/pokemon?limit=100"  
        all_pokemon = []
        
        while url:
            # Respect API rate limits
            self.wait_if_needed()
            
            try:
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Add this page's Pokémon to our list
                    all_pokemon.extend(data['results'])
                    
                    # Get URL for next page, will be None if we're on the last page
                    url = data['next']
                    
                    # Print progress update
                    print(f"Fetched {len(all_pokemon)} Pokémon so far...")
                else:
                    print(f"Error: Received status code {response.status_code}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                break
                
        return all_pokemon

    def save_pokemon_list(self, pokemon_list: List[Dict], filename: str = "pokemon_list.txt"):
        """
        Saves the Pokémon list to a file in a readable format.
        Each line contains the Pokémon's number and name.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            for index, pokemon in enumerate(pokemon_list, 1):
                # Extract just the name and format it nicely
                name = pokemon['name'].title()
                f.write(f"{index:03d}. {name}\n")

def main():
    # Create our fetcher object
    fetcher = PokemonListFetcher()
    
    print("Starting to fetch all Pokémon...")
    pokemon_list = fetcher.get_all_pokemon()
    
    if pokemon_list:
        print(f"\nSuccessfully retrieved {len(pokemon_list)} Pokémon!")
        
        # Save the list to a file
        fetcher.save_pokemon_list(pokemon_list)
        print("\nPokémon list has been saved to 'pokemon_list.txt'")
        
        # Display the first 10 Pokémon as a preview
        print("\nHere are the first 10 Pokémon as a preview:")
        for index, pokemon in enumerate(pokemon_list[:10], 1):
            print(f"{index:03d}. {pokemon['name'].title()}")

if __name__ == "__main__":
    main()