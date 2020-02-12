from lxml import etree
import csv

""" A Release should contain:
        rID
        rDate
        rStyle
        rCountry
        rCount
        rName
        aID
        lID
        gName
        rReviewCount
"""
def parse_releases(xmlfile):

    print("Parsing Releases")
    tree = etree.parse(xmlfile)
    releases = tree.findall('./release')
    print("Parsed Releases")

    rows = []

    for release in releases:
        rID = release.get('id')
        rDate = release.find('released').text if release.find('released') is not None else ''
        rStyle = release.findall('./styles/style')[0].text if len(release.findall('./styles/style')) != 0 else ''
        rCountry = release.find('country').text if release.find('country') is not None else ''
        rCount = 0
        rName = release.find('title').text
        aID = 0 # TODO replace with real value
        lID = 0 # TODO replace with real value
        gName = release.findall('./genres/genre')[0].text if len(release.findall('./genres/genre')) != 0 else ''
        rReviewCount = 0

        rows.append([rID, rDate, rStyle, rCountry, rCount, rName, aID, lID, gName, rReviewCount])

    print("Parsed Releases")

    print("Writing Rows")
    with open('data/releases.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("Wrote Rows")
    print(len(rows))
    print("Finished")


""" A Track should contain:
        rID
        tPosition
        tURL
        tName
        tDuration
"""
def parse_tracks(xmlfile):

    print("Parsing Releases")
    tree = etree.parse(xmlfile)
    releases = tree.findall('./release')
    print("Parsed Releases")

    rows = []

    print("Parsing Songs")
    for release in releases:
        rID = release.get('id')
        tracks = release.findall('./tracklist/track')
        for index, track in enumerate(tracks):
            tPosition = index
            tURL = ''
            tName = track.find('title').text
            tDuration = track.find('duration').text
            rows.append([rID, tPosition, tURL, tName, tDuration])
    print("Parsed Songs")

    print("Writing Rows")
    with open('data/tracks.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("Wrote Rows")
    print(len(rows))
    print("Finished")

    
#parse_tracks('data/release_subset.xml')
parse_releases('data/release_subset.xml')