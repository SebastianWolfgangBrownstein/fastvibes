import os
import requests

from ..constants.headers import USER_AGENT


def isolateName(inputDict):
    return inputDict.get('name')


class LastFM:
    root = "https://ws.audioscrobbler.com/2.0/"
    fmt = "json"
    bio_tag_delimiter = "<a href=\"https://www.last.fm"

    def __init__(self, id='LastFMHandler'):
        self.id = id

    @staticmethod
    async def getArtistData(artist_name, raw=False):
        try:
            params = {
                'method': 'artist.getInfo',
                'artist': f'{artist_name}',
                'api_key': os.environ.get("LASTFM_API_KEY"),
                'format': 'json'
            }

            headers = {"User-Agent": USER_AGENT}

            response = requests.get(
                "https://ws.audioscrobbler.com/2.0/", params=params, headers=headers)

            artistData = response.json().get('artist')

            if raw is True:
                return artistData

            formattedArtistData = await LastFM._formatArtistData(artistData)
            return formattedArtistData
        except Exception as e:
            print(f'LastFM Search Error: {e}')
            return None

    @staticmethod
    async def _formatArtistData(data):
        try:
            name = data.get('name')
            mbid = data.get('mbid')
            bio = await LastFM._parseArtistBio(data)
            tags = await LastFM._parseArtistTags(data)
            similar = await LastFM._parseSimilarArtists(data)

            responsePayload = {
                'name': name,
                'mbid': mbid,
                'bio': bio,
                'tags': tags,
                'similar_artists': similar
            }

            return responsePayload
        except Exception as e:
            print(f'LastFM Data Format Error: {e}')
            return None

    @staticmethod
    async def getArtistBio(artist_name, options={
        'condensed': False
    }):
        try:
            artistData = await LastFM.getArtistData(artist_name, raw=True)

            responsePayload = await LastFM._parseArtistBio(artistData, {
                'with_summary': True if options['condensed'] is True else False
            })
            return responsePayload
        except Exception as e:
            print(f'LastFM getArtistBio Error: {e}')
            return None

    @staticmethod
    async def getArtistTags(artist_name):
        try:
            artistData = await LastFM.getArtistData(artist_name, raw=True)

            responsePayload = await LastFM._parseArtistTags(artistData)
            return responsePayload
        except Exception as e:
            print(f'LastFM getArtistTags Error: {e}')
            return None

    @staticmethod
    async def getSimilarArtists(artist_name):
        try:
            artistData = await LastFM.getArtistData(artist_name, raw=True)

            responsePayload = await LastFM._parseSimilarArtists(artistData)
            return responsePayload
        except Exception as e:
            print(f'LastFM getSimilarArtists Error: {e}')
            return None

    @staticmethod
    async def _parseArtistBio(data, options={
        'with_summary': False
    }):
        try:
            name = data.get('name')
            # Full Bio
            bio = data.get('bio')
            if bio is None:
                bio = ""

            rawBioContent = bio.get('content')
            if rawBioContent is None:
                rawBioContent = ""

            bioContent = rawBioContent.split(LastFM.bio_tag_delimiter)[0]
            # Bio Summary
            if options['with_summary'] is True:
                rawBioSummary = bio.get('summary')
                if rawBioSummary is None:
                    pass
                bioSummaryContent = rawBioSummary.split(
                    LastFM.bio_tag_delimiter)[0]
                return {
                    "artist": name,
                    "bio": bioContent,
                    "bioSummary": bioSummaryContent
                }

            return {
                "artist": name,
                "bio": bioContent
            }
        except Exception as e:
            print(f'LastFM Artist Bio Format Error: {e}')
            return ""

    @staticmethod
    async def _parseArtistTags(data):
        try:
            name = data.get('name')
            rawTags = data.get('tags')
            if rawTags is None:
                return {
                    'artist': name,
                    'tags': []
                }

            rawTagList = rawTags.get('tag')
            if rawTagList is None:
                return {
                    'artist': name,
                    'tags': []
                }

            tags = map(isolateName, rawTagList)

            return {
                'artist': name,
                'tags': list(tags)
            }
        except Exception as e:
            print(f'LastFM Artist Tag Format Error: {e}')
            return []

    @staticmethod
    async def _parseSimilarArtists(data):
        try:
            name = data.get('name')
            rawArtists = data.get('similar')
            if rawArtists is None:
                return {
                    'artist': name,
                    'similar': []
                }

            rawArtistsList = rawArtists.get('artist')
            if rawArtistsList is None:
                return {
                    'artist': name,
                    'similar': []
                }

            similarArtists = map(isolateName, rawArtistsList)

            return {
                'artist': name,
                'similar': list(similarArtists)
            }
        except Exception as e:
            print(f'LastFM Similar Artists Format Error: {e}')
            return []
