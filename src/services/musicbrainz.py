import requests

ROOT_ENDPOINT = "https://musicbrainz.org/ws/2"
USER_AGENT = "FastVibes/1.0"
LINK_TYPES = ["bandcamp", "discogs", "soundcloud", "youtube",
              "free streaming", "official homepage", "purchase for download"]


async def getMusicBrainzData(isrc):
    try:
        # data = await get_artist_links_by_artist_MBID(isrc)
        isrcMapping = await get_MBID_By_ISRC(isrc)
        mbid = isrcMapping.get('mbid')

        data = await get_recording_By_MBID(mbid)

        return data
    except Exception as e:
        return None


async def get_MBID_By_ISRC(isrc):
    try:
        params = {
            'fmt': 'json'
        }
        headers = {"User-Agent": USER_AGENT}

        response = requests.get(
            f"{ROOT_ENDPOINT}/isrc/{isrc}", params=params, headers=headers)
        jsonRecordings = response.json().get('recordings')

        firstRecording = jsonRecordings[0]

        if firstRecording is None:
            return None

        responsePayload = {
            'isrc': isrc,
            'mbid': firstRecording.get("id")
        }

        return responsePayload
    except Exception as e:
        print(f'MusicBrainz get_MBID_By_ISRC Error: {e}')
        return None


async def get_recording_By_MBID(mbid):
    try:
        params = {
            'inc': 'artists+releases+url-rels',
            'fmt': 'json'
        }

        headers = {"User-Agent": USER_AGENT}

        response = requests.get(
            f"{ROOT_ENDPOINT}/recording/{mbid}", params=params, headers=headers)

        jsonData = response.json()
        data = await formatRecordingInfo(jsonData)
        return data
    except Exception as e:
        return None


async def formatRecordingInfo(data):
    try:
        recording_mbid = data.get('id')
        title = data.get('title')
        first_release = data.get('first-release-date')

        artists = data.get('artist-credit')
        primary_artist = artists[0]
        artist = primary_artist.get('name')
        artist_mbid = primary_artist.get('artist').get('id')

        releases = data.get('releases')
        # primary_release = releases[0]
        releasesPayload = map(formatRelease, releases)

        responsePayload = {
            'recording_mbid': recording_mbid,
            'title': title,
            'artist': artist,
            'artist_mbid': artist_mbid,
            'first_release': first_release,
            'releases': list(releasesPayload)
        }

        return responsePayload
    except Exception as e:
        print(f'MusicBrainz Data Format Error: {e}')


async def get_artist_links_by_artist_MBID(mbid):
    try:
        params = {
            'inc': 'url-rels',
            'fmt': 'json'
        }

        headers = {"User-Agent": USER_AGENT}

        response = requests.get(
            f"{ROOT_ENDPOINT}/artist/{mbid}", params=params, headers=headers)

        jsonLinks = response.json().get("relations")

        filteredLinks = filter(filterLinkByType, jsonLinks)
        artistLinks = map(extractEssentialLinkInfo, filteredLinks)
        return list(artistLinks)
    except Exception as e:
        return None


def filterLinkByType(rawLink):
    return True if rawLink["type"] in LINK_TYPES else False


def extractEssentialLinkInfo(rawLink):
    linkType = rawLink.get('type')
    linkUrl = rawLink.get('url').get('resource')
    return {
        "type": linkType,
        "url": linkUrl
    }


def formatRelease(rawRelease):
    return {
        'status': rawRelease.get('status'),
        'title': rawRelease.get('title'),
        'release_mbid': rawRelease.get('id'),
        'release_date': rawRelease.get('date'),
        'release_country': rawRelease.get('country')
    }
