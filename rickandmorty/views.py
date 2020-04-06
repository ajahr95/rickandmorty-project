from django.http import HttpResponse
from django.shortcuts import render
import requests 

def extract_id(character_url):

    id = ""

    for i in reversed(character_url):

        if i == "/":
            break
        else:
            id = i + id

    return id


def get_all_episodes():

    total_episodes = {}
    first_request = requests.get("https://integracion-rick-morty-api.herokuapp.com/api/episode/").json()
    number_of_pages = int(first_request["info"]["pages"]) + 1
    is_first = True
    episodes_url = "https://integracion-rick-morty-api.herokuapp.com/api/episode?page="
    actual_page = 1

    while number_of_pages > actual_page:

        if not is_first:

            new_request = requests.get(episodes_url+str(actual_page)).json()
            new_request = new_request["results"]

        else:
            is_first = False
            new_request = first_request["results"]

        for episode in new_request:
            
            id = episode["id"]
            name = episode["name"]
            air_date = episode["air_date"]
            episode_code = episode["episode"]
            
            total_episodes[episode_code] = {"name": name, "air_date":air_date, "id":id}
        
        actual_page += 1


    return total_episodes


def get_one_location(id):

    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/location/" + str(id)

    one_location = requests.get(url_request).json()

    characters_urls = one_location["residents"]

    characters_ids = []

    for character in characters_urls:

        id = extract_id(character)
        characters_ids.append(id)

    characters = get_multiple_characters(characters_ids)

    characters_dict = {}

    for character in characters:

        characters_dict[character["id"]] = {"name":character["name"], "id": character["id"]}
    
    one_location = {"name": one_location["name"],
                    "type": one_location["type"],
                    "dimension": one_location["dimension"],
                    "characters": characters}

    return one_location


def get_one_episode(id):

    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/episode/" + str(id)

    one_episode = requests.get(url_request).json()

    characters_urls = one_episode["characters"]

    characters_ids = []

    for character in characters_urls:

        id = extract_id(character)
        characters_ids.append(id)

    characters = get_multiple_characters(characters_ids)
    
    one_episode = {"name": one_episode["name"], "air_date": one_episode["air_date"], "episode": one_episode["episode"], "characters": characters}

    return one_episode


def get_one_character(id):

    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/character/" + str(id)

    one_character = requests.get(url_request).json()

    episodes_urls = one_character["episode"]

    episodes_ids = []

    for episode in episodes_urls:

        id = extract_id(episode)
        episodes_ids.append(id)

    episodes = get_multiple_episodes(episodes_ids)

    location_name = one_character["location"]["name"]
    location_url = one_character["location"]["url"]
    if location_name == "unknown" or location_name == "":
        location_name = "unknown"
        location_id = ""
    else:
        location_id = extract_id(location_url)

    origin_name = one_character["origin"]["name"]
    origin_url = one_character["origin"]["url"]
    if origin_name == "unknown" or origin_name == "":
        origin_name = "unknown"
        origin_id = ""
    else:
        location_id = extract_id(location_url)

    origin_id = extract_id(origin_url)

    location = {"name": location_name, "id":location_id}
    origin = {"name": origin_name, "id":origin_id}
    
    one_character = {"name": one_character["name"],
                    "status": one_character["status"],
                    "species": one_character["species"],
                    "type": one_character["type"],
                    "gender": one_character["gender"],
                    "origin": origin,
                    "location": location,
                    "image_url": one_character["image"],
                    "episodes": episodes}

    return one_character


def get_multiple_characters(characters):

    characters_str = ""

    for character in characters:
        characters_str += character + ","

    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/character/" + str(characters_str)

    total_characters = requests.get(url_request).json()

    return total_characters


def get_multiple_episodes(episodes):

    episodes_str = ""

    for episode in episodes:
        episodes_str += episode + ","

    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/episode/" + str(episodes_str)

    total_episodes = requests.get(url_request).json()

    return total_episodes


def filtered_characters(word):
    
    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/character/?name=" + str(word)
    characters = requests.get(url_request).json()

    if "results" in characters:

        characters = characters["results"]

        characters_dict = {}

        for character in characters:

            characters_dict[character["id"]] = {"id":character["id"], "name": character["name"]}
    
    else: 
        return {}

    return characters_dict


def filtered_episodes(word):

    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/episode/?name=" + str(word)
    episodes = requests.get(url_request).json()

    if "results" in episodes:

        episodes = episodes["results"]

        episodes_dict = {}

        for episode in episodes:

            episodes_dict[episode["id"]] = {"id":episode["id"], "name": episode["name"]}
    
    else:
        return {}

    return episodes_dict


def filtered_locations(word):

    url_request = "https://integracion-rick-morty-api.herokuapp.com/api/location/?name=" + str(word)
    locations = requests.get(url_request).json()
    if "results" in locations:
        locations = locations["results"]
        locations_dict = {}

        for location in locations:

            locations_dict[location["id"]] = {"id":location["id"], "name": location["name"]}
    
    else:

        return {}

    return locations_dict


def search_bar(word):
    
    characters = filtered_characters(word)
    episodes = filtered_episodes(word)
    locations = filtered_locations(word)

    result = {"characters":characters, "episodes":episodes, "locations": locations}
    return result

def search(request):

    word = request.GET['word']

    print("WORD")
    print(word)
    
    result = search_bar(word)

    return render(request, 'search.html', {"result":result})


def location(request, id):
    
    location = get_one_location(id)

    return render(request, 'location.html', {"location":location})


def character(request, id):
    
    character = get_one_character(id)

    return render(request, 'character.html', {"character":character})


def episode(request, id):

    one_episode = get_one_episode(id)
    
    return render(request, 'episode.html',{"episode":one_episode})


def home(request):
    episodes = get_all_episodes()
    return render(request, 'home.html', {'episodes': episodes.items()})