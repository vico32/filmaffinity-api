import requests

def get_movie_info(movie_name):
    # Primero, realizar la búsqueda por nombre de la película
    search_url = f"http://localhost:22049/api/search?query={movie_name}"
    response = requests.get(search_url)
    
    # Verificamos que la respuesta sea correcta
    if response.status_code == 200:
        search_results = response.json()
        
        # Mostramos los resultados y pedimos al usuario que seleccione una película
        print("Resultados de la búsqueda:")
        for idx, movie in enumerate(search_results):
            print(f"{idx+1}. {movie['title']} ({movie['year']}) - Rating: {movie['rating']}")
        
        # Solicitar al usuario que elija la película correcta
        movie_index = int(input(f"\nElige la ID de la película (1-{len(search_results)}): ")) - 1
        movie_id = search_results[movie_index]['id']
        
        # Hacemos la consulta para obtener detalles de la película seleccionada
        movie_url = f"http://localhost:22049/api/film?id={movie_id}"
        movie_response = requests.get(movie_url)
        
        if movie_response.status_code == 200:
            movie_info = movie_response.json()
            
            # Mostramos la información de la película de forma organizada
            print("\n" + "❕" + movie_info["title"] + "❕")
            print("➖➖➖➖➖➖➖➖➖➖")
            print(f"🎭 Género ➤ {movie_info['genre']}")
            print(f"📅 Año ➤ {movie_info['year']}")
            print(f"🖥 Calidad ➤ HD 1080p")
            print(f"🔊 Audio ➤🇪🇸Castellano")
            print(f"🎬 Tráiler ➤ Ver en YouTube")
            print("➖➖➖➖➖➖➖➖➖➖")
            print(f"⭐️⭐️➤ {movie_info['rating']}")
            print("➖➖➖➖➖➖➖➖➖➖")
            print(f"✨ Sinopsis: {movie_info['summary']}")
            print("➖➖➖➖➖➖➖➖")
        else:
            print("Error al obtener los detalles de la película.")
    else:
        print("Error al realizar la búsqueda.")

# Solicitar al usuario que ingrese el nombre de la película
movie_name = input("Introduce el nombre de la película: ")
get_movie_info(movie_name)
