from enum import Enum


class Messages(Enum):

    ARTISTS_OF_THE_MOST_POPULAR_SONGS = (("Artistas de las canciones más populares"),)
    SEARCHING_RELATED_ARTISTS = (("Bucando Artistas similares"),)
    NOTE_FOR_RELEASES = (
        (
            "Se buscará un número de canciones de cualquier género musical que recién se han subido. Luego se añadirán a esos artistas."
        ),
    )
    NOTE_FOR_TOP_TRACKS = (("Se buscará y se creará un dataframe las canciones populares de tu perfil"),)
    NOTE_FOR_CANDIDATES_TRACKS = (("Se creará un dataframe con las canciones candidatas"),)
    SEARCHING_ALBUMS_FROM_ARTISTS = (("Se buscará un número de album de cada artista"),)
    SEARCHING_SONGS_FROM_ALBUMS = (("Se buscará un número de canciones de cada albúm"),)
    SEARCHING_ARTIST_WITH_NEW_REALEASES = (
        ("Buscando artistas con nuevos lanzamientos"),
    )
    ENTER_FOR_CONTINUED = (("Presiona [ENTER] para continuar"),)
    WAIT_FOR_DATAFRAME = (("Espera un momento se está creando el dataframe..."),)
    SONGS_RECOMMENDED = (("Ha terminado el proceso de recomendación con éxito!!!!"))

    def __init__(self, value: str) -> None:
        self._value_ = value

    def __str__(self):
        BANNER = "==================================="
        return f"{BANNER}\n{self._value_}\n{BANNER}"

