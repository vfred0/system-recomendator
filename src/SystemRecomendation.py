from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ApiSpotify import ApiSpotify

class SystemRecommendation:    
    def __init__(self):
        self.__api_spotify: ApiSpotify = ApiSpotify()
        self.__user_tracks = None
        self.__candidates_tracks = None
        self.__cosine_similarity = None

    def interact(self) -> None:
        self.__user_tracks = self.__api_spotify.get_top_tracks()
        self.__candidates_tracks = self.__api_spotify.get_candidates_tracks()
        self.__api_spotify.create_playlist(self.__get_recommendations_tracks())

    def __set_cosine_similarity(self):
        scaler = StandardScaler()
        top_tracks_scaled = scaler.fit_transform(self.__user_tracks.iloc[:, 1:].values)
        candidate_tracks_scaled = scaler.fit_transform(
            self.__candidates_tracks.iloc[:, 1:].values
        )
        top_tracks_normalized = np.sqrt(
            (top_tracks_scaled * top_tracks_scaled).sum(axis=1)
        )
        candidates_tracks_normalized = np.sqrt(
            (candidate_tracks_scaled * candidate_tracks_scaled).sum(axis=1)
        )

        self.__cosine_similarity = cosine_similarity(
            top_tracks_scaled
            / top_tracks_normalized.reshape(top_tracks_scaled.shape[0], 1),
            candidate_tracks_scaled
            / candidates_tracks_normalized.reshape(candidate_tracks_scaled.shape[0], 1),
        )
       

    def __get_recommendations_tracks(self):
        self.__set_cosine_similarity()
        ids_top_tracks = []
        ids_playlist = []
        for i in range(self.__user_tracks.shape[0]):
            ids_top_tracks.append(self.__user_tracks["id"][i])
            for i in self.__get_candidates_tracks(i, 5):
                ids_playlist.append(self.__candidates_tracks["id"][i])
        return list(set([x for x in ids_playlist if x not in ids_top_tracks]))

    def __get_candidates_tracks(self, index, number_candidates, umbral=0.9):
        result = np.where(self.__cosine_similarity[index, :] >= umbral)[0]
        result = result[np.argsort(self.__cosine_similarity[index, result])[::-1]]
        if len(result) >= number_candidates:
            return result[0:number_candidates]
        return result


SystemRecommendation().interact()
