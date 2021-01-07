'''
MIT License

Copyright (c) 2021 Skander Jeddi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

'''
Utility library to query the current Spotify track
PyPI page: https://pypi.org/project/SwSpotify/
GitHub page: https://github.com/SwagLyrics/SwSpotify
'''
from SwSpotify import spotify
'''
Utility library to quety the Genius database for track informations
PyPI page: https://pypi.org/project/lyricsgenius/
GitHub page: https://github.com/johnwmillr/lyricsgenius
'''
import lyricsgenius

import os
import re
import pathlib
from decouple import config

# Program version
VERSION = 'R1.0'
# This is generated through the Genius API: https://genius.com/api-clients
CLIENT_ACCESS_TOKEN = config('GENIUS_CLIENT_ACCESS_TOKEN')

# Store an instance of Genius
genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN)

'''
Fetch lyrics, given a track title and an artist.
This will check the cached files before attempting to query the Genius API.
'''
def fetch_lyrics(song, artist):
    from_disk = read_from_disk(artist, song)
    if from_disk == None:
        print('Lyrics not found in cache, querying the Genius API...')
        try:
            genius_query = genius.search_song(song, artist)
            album = genius_query.album
            if genius_query == None:
                print('Cound not find lyrics in the Genius database!')
                exit(-1)
            else:
                if album == None:
                    albium = '(None)'
                return ((genius_query.lyrics, 'G'), album)
        except:
            print('An exception occurred while fetching lyrics from the Genius database!')
            exit(-1)
    else:
        return ((from_disk[0], 'C'), from_disk[1])

'''
Reads lyrics from disk, given a track title and an artist.
Returns None is no cache file is present, else returns a (lyrics, album) tuple.
'''
def read_from_disk(artist, song):
    stripped_artist, stripped_song = re.sub('\W+', '', artist.lower().strip()), re.sub('\W+', '', song.lower().strip())
    cache_file_name = f'{stripped_artist}/{stripped_song}.lrcs'
    print(f"Looking for {cache_file_name} in cache...")
    try:
        cache_file = open(f'cache/{cache_file_name}', 'r')
        lines = cache_file.readlines()
        return (lines[1:], lines[0].strip())
    except FileNotFoundError:
        return None

'''
Writes lyrics to disk, given a track title and an artist.
First line will be the name of the album.
'''
def write_to_disk(artist, song, lyrics, album):
    print('\nSaving lyrics to cache...', end='')
    stripped_artist, stripped_song = re.sub('\W+', '', artist.lower().strip()), re.sub('\W+', '', song.lower().strip())
    cache_file_name = f'{stripped_artist}/{stripped_song}.lrcs'
    pathlib.Path(f'cache/{stripped_artist}').mkdir(parents=True, exist_ok=True)
    with open(f'cache/{cache_file_name}', 'w') as cache_file:
        cache_file.write((album if album != None else '(None)') + "\n")
        cache_file.writelines(lyrics)
    print('\tdone!', end='')

# Runs the main program indefinitely until user exit
def main():
    while True:
        # Get the current track & artist from Spotify (spotify must be running & playing!)
        current_track = spotify.current()
        song, artist = current_track[0], current_track[1]
        # Get the lyrics & the album, either from the disk or from the Genius API
        lyrics, album = fetch_lyrics(song, artist)
        # Print useful information
        print(f'\nTrack: {song}\nArtist: {artist}\nAlbum: {album}\nLyrics:\n')
        # Fix the formatting issues in the code issued by the Genius query (maybe create an issue on the GitHub down the line?)
        lyrics_formatter = lambda l: l.replace('(\n', '(').replace('\n (', '(').replace('\n)', ')').replace('[\n', '[').replace('\n]', ']').replace("&\n", '&').replace("\n & \n", ' &').replace("\n&", '&').replace("& \n", '& ').replace(",\n", ', ').replace("\n,", ',').replace(" \n", " ").replace(" \n)", ")")
        if lyrics[1] == 'G': # 'G' mode means the lyrics are fetched straight from the datbabase
            print(lyrics_formatter(lyrics[0]))
        else: # Lyrics have been loaded from the local cache
            for line in lyrics[0]:
                print(lyrics_formatter(line), end='')
            print()
        if lyrics[1] == 'G': # If the song is new, write the lyrics on the disk
            write_to_disk(artist, song, lyrics[0], album)
        print('\nEnter any key to refresh, q to quit: ', end='')
        prompt = input().lower()
        if prompt == 'q':
            exit(0)
        else:
            main()

# Entry point
if __name__ == "__main__":
    print(f'SpyMyLyrics {VERSION} - by Skander Jeddi\n')
    main()
