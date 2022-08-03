import requests

from ..constants.headers import USER_AGENT


class Deezer:
    root_endpoint = "https://api.deezer.com"

    def __init__(self, id='Deezer'):
        self.id = id

    @staticmethod
    async def getTrackData(artist, track, raw=False):
        try:
            trackId = await Deezer.search(artist, track)
            if trackId is None:
                return None

            trackData = await Deezer.lookupTrack(trackId)

            if trackData is None:
                return None

            if raw is True:
                return trackData

            formattedTrackData = await Deezer._formatTrackData(trackData)
            return formattedTrackData
        except Exception as e:
            return None

    @staticmethod
    async def _formatTrackData(data):
        print('formatting data: ', data)
        try:
            formattedPayload = {
                'track': data.get('title'),
                'artist': data.get('artist').get('name'),
                'artist_thumb': data.get('artist').get('picture_big'),
                'dzid': data.get('id'),
                'isrc': data.get('isrc'),
                'release_date': data.get('release_date'),
                'bpm': data.get('bpm'),
                'gain': data.get('gain'),
                'album': data.get('album').get('title'),
                'album_art': data.get('album').get('cover_big'),
                'audio_preview': data.get('preview')
            }
            return formattedPayload
        except Exception as e:
            print(f'Deezer TrackData Format Error: {e}')
            return None

    @staticmethod
    async def search(artist, track):
        try:
            params = {
                'q': f'artist:"{artist}" track:"{track}"'
            }
            headers = {"User-Agent": USER_AGENT}

            response = requests.get(
                f"{Deezer.root_endpoint}/search", params=params, headers=headers)
            # print('Deezer Search Result: ', response.json())
            jsonData = response.json().get('data')[0]
            # print('Json Data: ', jsonData)
            deezerTrackId = jsonData.get('id')
            # print('deezerTrackId: ', deezerTrackId)
            return deezerTrackId
        except Exception as e:
            print(f'Deezer Search Error: {e}')
            return None

    @staticmethod
    async def lookupTrack(trackId):
        try:
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(
                f"{Deezer.root_endpoint}/track/{trackId}", headers=headers)
            jsonData = response.json()

            return jsonData
        except Exception as e:
            print(f"Deezer Track Lookup Error: {e}")
            return None
