import requests
from ..constants.headers import USER_AGENT

ROOT_ENDPOINT = "https://musicbrainz.org/ws/2"
LINK_TYPES = ["bandcamp", "discogs", "soundcloud", "youtube",
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
