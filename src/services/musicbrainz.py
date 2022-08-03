import requests
from ..constants.headers import USER_AGENT

ROOT_ENDPOINT = "https://musicbrainz.org/ws/2"
LINK_TYPES = ["bandcamp", "discogs", "soundcloud", "youtube", "streaming",
              "free streaming", "official homepage", "purchase for download"]


class Brainz:
    root_endpoint = "https://musicbrainz.org/ws/2"
    fmt = "json"

    def __init__(self, id='Brainz'):
        self.id = id

    # Returns Recording ID associated with a given ISRC (Use to get the MBID of the recording)
    @staticmethod
    async def ISRC(isrc, populate=False):
        try:
            params = {
                'fmt': 'json'
            }
            headers = {"User-Agent": USER_AGENT}

            response = requests.get(
                f"{Brainz.root_endpoint}/isrc/{isrc}", params=params, headers=headers)
            jsonRecordings = response.json().get('recordings')

            firstRecording = jsonRecordings[0]

            if firstRecording is None:
                return None

            isrcPayload = {
                'isrc': isrc,
                'mbid': firstRecording.get("id")
            }
            if populate is False:
                return isrcPayload

            # Populate the response with recording data
            recordingData = await Brainz.findRecording(isrcPayload['mbid'], isrc)
            return recordingData
        except Exception as e:
            print(f'MusicBrainz ISRC Error: {e}')
            return None

    # Lookup Recording Data by its MBID, including artist & release data
    @staticmethod
    async def findRecording(mbid, isrc=None):
        try:
            params = {
                'inc': 'artists+releases+url-rels',
                'fmt': Brainz.fmt
            }

            headers = {"User-Agent": USER_AGENT}

            response = requests.get(
                f"{Brainz.root_endpoint}/recording/{mbid}", params=params, headers=headers)

            jsonData = response.json()
            data = await Brainz._formatRecordingData(jsonData, isrc)
            return data
        except Exception as e:
            return None

    @staticmethod
    async def findArtist(mbid):
        try:
            params = {
                'inc': 'url-rels',
                'fmt': Brainz.fmt
            }
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(
                f"{Brainz.root_endpoint}/artist/{mbid}", params=params, headers=headers)

            return response.json()
        except Exception as e:
            return None

    async def findArtistByName(artist, populate=False):

        try:
            params = {
                'query': f'artist:"{artist}"',
                'fmt': Brainz.fmt
            }

            headers = {"User-Agent": USER_AGENT}
            response = requests.get(
                f"{Brainz.root_endpoint}/artist", params=params, headers=headers)

            artists = response.json().get('artists')

            if artists is None:
                return None

            topArtistMatch = artists[0]
            artist_mbid = topArtistMatch.get('id')
            artistIdPayload = {
                'artist': artist,
                'mbid': artist_mbid
            }
            if populate is False:
                return artistIdPayload

            artistData = await Brainz.findArtist(artist_mbid)
            return artistData
        except Exception as e:
            return None

    @staticmethod
    async def _formatRecordingData(data, isrc=None):
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
            releasesPayload = map(Brainz._formatRelease, releases)

            responsePayload = {
                'isrc': isrc,
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

    @staticmethod
    def _formatRelease(rawRelease):
        return {
            'status': rawRelease.get('status'),
            'title': rawRelease.get('title'),
            'release_mbid': rawRelease.get('id'),
            'release_date': rawRelease.get('date'),
            'release_country': rawRelease.get('country')
        }

    @staticmethod
    def formatArtistLinks(linkList):
        jsonLinks = linkList.get("relations")
        filteredLinks = filter(filterLinkByType, jsonLinks)
        artistLinks = map(extractEssentialLinkInfo, filteredLinks)
        typedLinks = map(detectLinkType, artistLinks)
        return list(typedLinks)


def filterLinkByType(rawLink):
    return True if rawLink["type"] in LINK_TYPES else False


def extractEssentialLinkInfo(rawLink):
    linkUrl = rawLink.get('url').get('resource')
    linkType = rawLink.get('type')

    return {
        "type": linkType,
        "url": linkUrl
    }


def detectLinkType(link):
    linkUrl = link['url']
    rawLinkType = link['type']
    linkType = rawLinkType

    if rawLinkType == 'official homepage':
        linkType = 'official'
    elif (rawLinkType == 'free streaming') and ("spotify" in linkUrl):
        linkType = 'spotify'
    elif rawLinkType == 'purchase for download':
        if "apple" in linkUrl:
            linkType = 'apple_music'
        elif "beatport" in linkUrl:
            linkType = 'beatport'
        elif "junodownload" in linkUrl:
            linkType = 'juno'
        elif "google" in linkUrl:
            linkType = 'google_play'
        elif "7digital" in linkUrl:
            linkType = '7digital'

    return {
        **link,
        "type": linkType
    }
