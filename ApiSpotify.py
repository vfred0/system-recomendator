from Console import Console
import spotipy
import pandas as pd
from Crendentials import Credentials
from Mesagges import Messages


class ApiSpotify:
    def __init__(self) -> None:
        self.__spotipy = self.__get_connection("user-read-recently-played")
        # self.__spotipy = self.__get_connection("user-top-read")
        self.__features = [
            "id",
            "acousticness",
            "danceability",
            "duration_ms",
            "energy",
            "instrumentalness",
            "key",
            "liveness",
            "loudness",
            "mode",
            "speechiness",
            "tempo",
            "valence",
        ]
        self.__top_tracks = None
        self.__top_tracks_raw = None

    def __set_top_tracks(self):
        Console.show_message(Messages.NOTE_FOR_TOP_TRACKS)
        number_tracks: int = Console.read_int("Ingresa el número de pistas: ")
        print(f"Obteniendo las {number_tracks} canciones")

        self.__top_tracks_raw = self.__spotipy.current_user_recently_played(
            limit=number_tracks
        )

        print(self.__top_tracks_raw)
        for i, item in enumerate(self.__top_tracks_raw["items"]):
            print(f"{i + 1} - {item['track']['name']}")
                
        print(Messages.WAIT_FOR_DATAFRAME)
        track_names = []
        audio_features = []
        for track in self.__top_tracks_raw["items"]:
            track = track["track"]
            track_names.append(track["name"])
            audio_features.append(self.__spotipy.audio_features(track["id"])[0])

        self.__top_tracks = pd.DataFrame(audio_features, index=track_names)[
            self.__features
        ]

        input(f"{self.__top_tracks}\n{Messages.ENTER_FOR_CONTINUED}")

    def get_top_tracks(self):
        self.__set_top_tracks()
        return self.__top_tracks

    def get_candidates_tracks(self):
        id_tracks = self.__get_tracks(self.__get_artists())
        track_names = []
        features = []
        Console.show_message(Messages.NOTE_FOR_CANDIDATES_TRACKS)
        for i, track_id in enumerate(id_tracks):
            print("Analizando canción:", i + 1, "de", len(id_tracks))
            audio_features = self.__spotipy.audio_features(track_id)
            if audio_features[0]:
                track_names.append(self.__spotipy.track(track_id)["name"])
                print(f"Canción: {track_names[-1]} ")
                features.append(audio_features[0])
            print("\n")

        input(Messages.ENTER_FOR_CONTINUED)
        return pd.DataFrame(features, index=track_names)[self.__features]

    def __get_tracks(self, ids_artists):
        id_albums = []
        Console.show_message(Messages.SEARCHING_ALBUMS_FROM_ARTISTS)
        number_albums = Console.read_int("Ingresa la cantidad de albumes: ")
        for i, artist in enumerate(ids_artists):
            print("Analizando artista: ", i + 1, "de", len(ids_artists))
            albums = self.__spotipy.artist_albums(artist, limit=number_albums)
            for album in albums["items"]:
                print(f"Album: {album['name']}")
                id_albums.append(album["id"])
            print("\n")

        print("Total de albumes: ", len(id_albums))
        input(Messages.ENTER_FOR_CONTINUED)

        id_tracks = []
        Console.show_message(Messages.SEARCHING_SONGS_FROM_ALBUMS)
        number_tracks = Console.read_int("Ingresa la cantidad de canciones: ")
        for i, id_album in enumerate(id_albums):
            print("Analizando álbum:", i + 1, "de", len(id_albums))
            album_tracks = self.__spotipy.album_tracks(id_album, limit=number_tracks)
            for track in album_tracks["items"]:
                print(f"Canción: {track['name']}")
                id_tracks.append(track["id"])
            print("\n")

        print("Total de canciones pre-candidatos: ", len(id_tracks))
        input(Messages.ENTER_FOR_CONTINUED)
        return id_tracks

    def __get_artists(self):
        Console.show_message(Messages.ARTISTS_OF_THE_MOST_POPULAR_SONGS)
        ids_artists = []
        for item in self.__top_tracks_raw["items"]:
            item = item["track"]
            print("> ", item["artists"][0]["name"])
            ids_artists.append(item["artists"][0]["id"])

        ids_artists = self.__remove_duplicates(ids_artists)        
        input(Messages.ENTER_FOR_CONTINUED)

        Console.show_message(Messages.SEARCHING_RELATED_ARTISTS)
        ids_similar_artists = []
        for id_artist in ids_artists:
            for item in self.__spotipy.artist_related_artists(id_artist)["artists"]:
                print("> ", item["name"])
                ids_similar_artists.append(item["id"])

        ids_artists.extend(ids_similar_artists)
        ids_artists = self.__remove_duplicates(ids_artists)
        input(Messages.ENTER_FOR_CONTINUED)
        Console.show_message(Messages.NOTE_FOR_RELEASES)
        number_releases = Console.read_int(
            "Ingresa la cantidad de nuevas canciones a buscar: "
        )
        new_releases = self.__spotipy.new_releases(limit=number_releases)["albums"]
        print(Messages.SEARCHING_ARTIST_WITH_NEW_REALEASES)
        for item in new_releases["items"]:
            print("> ", item["artists"][0]["name"], "//", item["name"])
            ids_artists.append(item["artists"][0]["id"])

        return self.__remove_duplicates(ids_artists)

    def __remove_duplicates(self, content: list):
        return list(set(content))

    def __get_connection(self, scope: str):
        return spotipy.Spotify(
            auth=spotipy.util.prompt_for_user_token(
                username=Credentials.USERNAME.value,
                scope=scope,
                client_id=Credentials.CLIENT_ID.value,
                client_secret=Credentials.CLIENT_SECRET.value,
                redirect_uri="http://localhost:8080",
            )
        )

    def create_playlist(self, recommendations):
        Console.show_message(
            f"{Messages.SONGS_RECOMMENDED} \nTotal de canciones recomendadas: {len(recommendations)}\n"
        )
        name = Console.read_str("Nombre para la playlist: ")
        description = Console.read_str("Descripción para la playlist: ")
        self.__spotipy = self.__get_connection("playlist-modify-public")
        playlist = self.__spotipy.user_playlist_create(
            user=Credentials.USERNAME.value,
            name=name,
            description=description,
        )
        self.__spotipy.playlist_add_items(playlist["id"], recommendations)
        print(f"Playlist '{name}' creada con éxito!!!")
