import os
import requests


async def getLastFmData(artist):
    try:
        data = await getArtistInfo(artist)
        if data is None:
            return None

        info = await formatArtistInfo(data)

        return info
    except Exception as e:
        return None


async def getArtistInfo(artist):
    try:
        params = {
            'method': 'artist.getInfo',
            'artist': f'{artist}',
            'api_key': os.environ.get("LASTFM_API_KEY"),
            'format': 'json'
        }

        response = requests.get(
            "https://ws.audioscrobbler.com/2.0/", params=params)

        jsonData = response.json().get('artist')

        return jsonData
    except Exception as e:
        print(f'LastFM Search Error: {e}')
        return None


async def formatArtistInfo(data):
    try:
        name = data.get('name')
        mbid = data.get('mbid')
        bio = await parseArtistBio(data)
        tags = await parseArtistTags(data)
        similar = await parseSimilarArtists(data)

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

lastfm_bio_tag_delimiter = "<a href=\"https://www.last.fm"


async def parseArtistBio(data):
    try:
        bio = data.get('bio')
        if bio is None:
            bio = ""

        rawBioContent = bio.get('content')
        if rawBioContent is None:
            rawBioContent = ""

        bioContent = rawBioContent.split(lastfm_bio_tag_delimiter)[0]

        return bioContent
    except Exception as e:
        print(f'LastFM Artist Bio Format Error: {e}')
        return ""


async def parseArtistTags(data):
    try:
        rawTags = data.get('tags')
        if rawTags is None:
            return []

        rawTagList = rawTags.get('tag')
        if rawTagList is None:
            return []

        tags = map(isolateName, rawTagList)

        return list(tags)
    except Exception as e:
        print(f'LastFM Artist Tag Format Error: {e}')
        return []


async def parseSimilarArtists(data):
    try:
        rawArtists = data.get('similar')
        if rawArtists is None:
            return []

        rawArtistsList = rawArtists.get('artist')
        if rawArtistsList is None:
            return []

        similarArtists = map(isolateName, rawArtistsList)

        return list(similarArtists)
    except Exception as e:
        print(f'LastFM Similar Artists Format Error: {e}')
        return []


def isolateName(inputDict):
    return inputDict.get('name')


async def getArtistBio(artist):
    try:
        rawData = await getArtistInfo(artist)
        bio = await parseArtistBio(rawData)
        return bio
    except Exception as e:
        print(f'LastFM getArtistBio Error: {e}')
        return ""
