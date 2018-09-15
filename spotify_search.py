import os, sys, urllib, json
from selenium import webdriver
from bs4 import BeautifulSoup

class Spotify_Search(object):

    def __init__(self):

        pass
 
    def get_link_info(self, tgt_link):

        if tgt_link[:8] == "https://":

            link_type_str = tgt_link[8:]
            link_type = link_type_str.split("/")

        return link_type

    def get_spotify_page(self, tgt_link):

        #import pdb; pdb.set_trace()

        try:
            spotify_resp = urllib.request.urlopen(tgt_link)
            #print(spotify_resp)
            spotify_soup = BeautifulSoup(spotify_resp.read(), 'html.parser')
        
            return spotify_soup

        except urllib.error.HTTPError as http_error:

            return -1

    def find_artwork(self, page):

        pass

    def find_song_album(self, page, link_type):
        #import pdb; pdb.set_trace()
        
        script_divs = page.find_all("script")
        song_meta_data = script_divs[-4]

        song_info = {
            "song_name": "",
            "album_name": "",
            "artist_name": "",
            "release_date": ""
        }


        if link_type == "track":

            script_inner = song_meta_data.getText()

            json_start_line = script_inner[script_inner.find("Entity"):]
            json_start_elem = str(json_start_line[json_start_line.find("{"):])

            json_byte = bytes(json_start_elem, "utf-8").decode("unicode_escape").strip()[:-1]

            song_json = json.loads(json_byte)

            #import pdb; pdb.set_trace()

            song_info["song_name"] = song_json['name']
            song_info["album_name"] = song_json['album']['name']
            song_info["artist_name"] = song_json['album']['artists'][0]['name']
            song_info['release_date'] = song_json['album']['release_date']
            #import pdb; pdb.set_trace()

            #album_name_div = page.findAll("div", {"class": "mo-info"})
            #print(page)

            return song_info

        elif link_type == "album":

            album_tracks = []
            
            script_inner = song_meta_data.getText()

            json_start_line = script_inner[script_inner.find("Entity"):]
            json_start_elem = str(json_start_line[json_start_line.find("{"):])

            json_byte = bytes(json_start_elem, "utf-8").decode("unicode_escape").strip()[:-1]

            album_json = json.loads(json_byte)

            #album_name = album_json['name']
            #artist_name = album_json['artists'][0]['name']

            for index, track in enumerate(album_json['tracks']['items']):

                album_tracks.append(album_json['tracks']['items'][index]['name'])


            song_info['song_name'] = album_tracks
            song_info['album_name'] = album_json['name']
            song_info['artist_name'] = album_json['artists'][0]['name']

            #import pdb; pdb.set_trace()

            #print("Album name: %s" % (album_name))

            return song_info

        elif link_type == "artist":

            top_tracks = []
            track_albums = []

            script_inner = song_meta_data.getText()

            json_start_line = script_inner[script_inner.find("Entity"):]
            json_start_elem = str(json_start_line[json_start_line.find("{"):])

            json_byte = bytes(json_start_elem, "utf-8").decode("unicode_escape").strip()[:-1]

            artist_json = json.loads(json_byte)

            for index, track in enumerate(artist_json['top_tracks']):

                top_tracks.append(artist_json['top_tracks'][index]['name'])
                track_albums.append(artist_json['top_tracks'][index]['album']['name'])

            song_info['song_name'] = top_tracks
            song_info['artist_name'] = artist_json['name']
            song_info['album_name'] = track_albums

            return song_info


    def find_song_name(self, page, link_type):

        if link_type == "track":
            
            track_name_div = page.findAll("span", {"class": "track-name"})
            track_name = track_name_div[0].getText()

        else:

            track_name = None

        return track_name

    def find_song_info(self, tgt_link, song_title=None):

        song_info = {
                "song_name": song_title,
                "artist_name": "None",
                "album_name": "None",
                "release_date": None
        }

        link_info = self.get_link_info(tgt_link)
        spotify_page = self.get_spotify_page(tgt_link)

        if spotify_page == -1:
            
            return song_info

        song_name = self.find_song_name(spotify_page, link_info[1])
        song_info = self.find_song_album(spotify_page, link_info[1])

        #import pdb; pdb.set_trace()

        try:
            if isinstance(song_info['song_name'], list):

                if len(song_info['song_name']) == 1:
                    song_info['song_name'] = song_info['song_name'][0]

                else:
                    for index, song in enumerate(song_info["song_name"]):   
                        
                        if song_title.lower() in song.lower():
                            song_info['song_name'] = song
                            #import pdb; pdb.set_trace()

                            if isinstance(song_info['album_name'], list):
                                
                                song_info['album_name'] = song_info['album_name'][index]

        
        except:
            
            song_info = {
                "song_name": song_title,
                "artist_name": "None",
                "album_name": "None",
                "release_date": None
            }

            return song_info
        
        return song_info
