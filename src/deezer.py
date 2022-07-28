import requests


async def getDeezerData(artist, track):
    try:
        trackId = await search(artist, track)
        if trackId is None:
            return None

        trackData = await lookupTrack(trackId)

        if trackData is None:
            return None

        payload = {
            'track': track,
            'artist': artist,
            'dzid': trackId,
            'isrc': trackData.get('isrc'),
            'release_date': trackData.get('release_date'),
            'artist_thumb': trackData.get('artist_thumb'),
            'bpm': trackData.get('bpm')
        }

        return payload
    except Exception as e:
        return None


async def search(artist, track):
    try:
        params = {
            'q': f'artist:"{artist}" track:"{track}"'
        }
        response = requests.get(
            f"https://api.deezer.com/search", params=params)
        # print('Deezer Search Result: ', response.json())
        jsonData = response.json().get('data')[0]
        # print('Json Data: ', jsonData)
        deezerTrackId = jsonData.get('id')
        # print('deezerTrackId: ', deezerTrackId)
        return deezerTrackId
    except Exception as e:
        print(f'Deezer Search Error: {e}')
        return None


async def lookupTrack(trackId):
    try:
        response = requests.get(f"https://api.deezer.com/track/{trackId}")

        jsonData = response.json()
        # print('Json Data: ', jsonData)
        dataPayload = {
            'isrc': jsonData.get('isrc'),
            'release_date': jsonData.get('release_date'),
            'artist_thumb': jsonData.get('artist').get('picture_big'),
            'bpm': jsonData.get('bpm')
        }
        return dataPayload
    except Exception as e:
        print(f"Deezer Track Lookup Error: {e}")
        return None
