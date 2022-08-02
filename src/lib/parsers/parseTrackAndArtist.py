import re


def parseTrackAndArtist(title, channel):
    regex = '^([\w\s]*)?(?:[\s]+[-][\s]+)([\w\s\(\)]*)'
    result = re.match(regex, title)
    if result:
        payload = {
            'artist': result.group(1) or channel,
            'track': result.group(2) or title
        }
    else:
        payload = {
            'artist': channel,
            'track': title
        }

    if " - Topic" in payload['artist']:
        cleanArtist = payload['artist'].replace(' - Topic', '')
        payload['artist'] = cleanArtist

    if "(Original Mix)" in payload['track']:
        cleanTrack = payload['track'].replace(' (Original Mix)', '')
        payload['track'] = cleanTrack

    print('Parsed Track: ', payload['track'])
    print('Parsed Artist: ', payload['artist'])
    return payload
