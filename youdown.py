#!/usr/bin/python3
import youtube_dl as yd
import os, requests, eyed3, gig, spotify_search, sys, urllib
from bs4 import BeautifulSoup
from sys import argv

class YouDown(object):

    def __init__(self):

        self.music_dest = os.environ['HOME'] + '/Music/'
        self.google_img_query = "https://www.google.com/search?tbm=isch&q="

        self.yd_opts = {
            "outtmpl": self.music_dest + "%(title)s.%(ext)s",
            "format": "bestaudio/best",
            "postprocessors": [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

    def download_youtube_song(self, you_url):

        youtube_song_info = self.find_youtube_song(you_url)
        
        sp_srch = spotify_search.Spotify_Search()

        #print(youtube_song_info)

        youtube_audio_info = self.download_youtube_audio(you_url)

        youtube_song_location = os.environ['HOME'] + '/Music/' + str(youtube_audio_info.get('title', None)).replace(":", "_").replace("\"", "'") + '.mp3'

        target_num = None

        if all(value for value in youtube_song_info.values()):

            self.youdown_debug_print("Searching the RIGHT Way!")

            song_name = youtube_song_info['song']
            song_artist = youtube_song_info['artist']

            artwork_hosts = self.download_artwork("%s - %s spotify" % (song_name, song_artist)) # get artwork

            if any([self.check_image_uri(host) for host in artwork_hosts]):

                for index, host in enumerate(artwork_hosts):

                    if self.check_image_uri(host):

                        target_num = index
                        break
                
                youdown_artwork_dir = self.find_image_path("%s - %s spotify" % (song_name, song_artist))

            else:

                artwork_hosts = self.download_artwork("%s spotify" % (song_name))

                for index, host in enumerate(artwork_hosts):

                    if self.check_image_uri(host):

                        target_num = index
                        break
                
                youdown_artwork_dir = self.find_image_path("%s spotify" % (song_name))


        else:
            
            artwork_hosts = self.download_artwork(youtube_audio_info.get('title', None) + " spotify") # get artwork

            if any([self.check_image_uri(host) for host in artwork_hosts]):

                #import pdb; pdb.set_trace()

                for index, host in enumerate(artwork_hosts):

                    if self.check_image_uri(host):

                        target_num = index
                        break

                youdown_artwork_dir = self.find_image_path(youtube_audio_info.get('title', None) + ' spotify')
        
            else:

                artwork_hosts = self.download_artwork(youtube_audio_info.get('title', None))

                for index, host in enumerate(artwork_hosts):

                    if self.check_image_uri(host):

                        target_num = index
                        break
                
                youdown_artwork_dir = self.find_image_path(youtube_audio_info.get('title', None))

        #import pdb; pdb.set_trace()

        if target_num == None:

            target_num = 0
       

        #import pdb; pdb.set_trace()

        image_name = [f for d, s, f in os.walk(youdown_artwork_dir)][0][target_num]

        if youtube_song_info['song']:
            song_title = youtube_song_info['song']

        else:
            song_title = youtube_audio_info.get('title', None)       

        song_info = sp_srch.find_song_info(artwork_hosts[target_num], song_title)

        song_info['artwork_location'] = ("%s/%s" % (youdown_artwork_dir, image_name))

        #import pdb; pdb.set_trace()

        # Handle file not found error
        try:
            os.rename(youtube_song_location, os.environ['HOME'] + '/Music/' + song_info['song_name'] + '.mp3')

        except FileNotFoundError:
            
            if self.query_yes_no("%s was not found, provide location manually?" % (youtube_song_location)):

                usr_filename = str(self.youdown_debug_print("Enter Filename Path > ", True))
                os.rename(usr_filename, os.environ['HOME'] + '/Music/' + song_info['song_name'] + '.mp3')


        song_info['song_location'] = os.environ['HOME'] + '/Music/' + song_info['song_name'] + '.mp3'
        self.format_youtube_song(song_info, True)

    def print_song_info(self, song_info):

        self.youdown_debug_print("Song Name: %s" % (song_info['song_name']))
        self.youdown_debug_print("Artist Name: %s" % (song_info['artist_name']))
        self.youdown_debug_print("Album Name: %s" % (song_info['album_name']))
        self.youdown_debug_print("Song Location: %s" % (song_info['song_location']))

    def query_yes_no(self, question, default="yes"):

        valid = {
            "yes": True,
            "y": True,
            "ye": True,
            "no": False,
            "n": False
        }
        
        if default is None:
            prompt = "[y/n]"
            
        elif default == "yes":
            prompt = "[Y/n]"
            
        elif default == "no":
            prompt = "[y/N]"

        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:

            self.youdown_debug_print("%s %s " % (question, prompt))

            choice = input().lower()
            
            if default is not None and choice == '':
                return valid[default]

            elif choice in valid:
                return valid[choice]

            else:
                self.youdown_debug_print("Please respond with 'yes' or 'no' "
                                "(or 'y' or 'n').\n")

    def find_youtube_song(self, you_url):

        youtube_song_info = {
            "song": None,
            "artist": None,
        }

        self.youdown_debug_print("Trying to find name of song...")

        you_resp = requests.get(you_url)
        
        you_soup = BeautifulSoup(you_resp.text, 'html.parser')
        
        if you_soup.find("div", {"id": "watch-description-extras"}):

            self.youdown_debug_print("Found Description Extras...")

            you_extras = you_soup.find("div", {"id": "watch-description-extras"})
            you_titles = you_soup.find_all("h4", {"class": "title"})
            you_unlists = you_extras.find_all("ul")

            for index, title in enumerate(you_titles):
                
                format_title = str(title.getText()).strip()
                
                if(format_title in ["Song", "Artist"]):

                    #print(you_unlists[index + 1])
                    self.youdown_debug_print("%s Categorey Found" % (format_title))
                    youtube_song_info[format_title.lower()] = you_unlists[index + 1].getText().strip()
        
        return youtube_song_info

    def format_youtube_song(self, song_info, confirm=False):

        artwork_data = open(song_info['artwork_location'], "rb").read()

        if confirm:
            self.print_song_info(song_info)
            
            usr_check = self.query_yes_no("[YouDown] Is this correct?")

            if not usr_check:

                song_info['song_name'] = self.youdown_debug_print("Enter Song Name > ", True)
                song_info['artist_name'] = self.youdown_debug_print("Enter Artist Name > ", True)
                song_info['album_name'] = self.youdown_debug_print("Enter Album Name > ", True)

                while True:
                    custom_image_link = self.youdown_debug_print("Enter Cover Art URL > ", True)

                    try:
                        image_data = urllib.request.urlopen(custom_image_link)
                        artwork_data = image_data.read()
                        break

                    except urllib.error.HTTPError:
                        self.youdown_debug_print("That URL is forbidden...Try another?")

        audio_file = eyed3.load(song_info['song_location'])
        audio_file.tag.artist = song_info['artist_name'] 
        audio_file.tag.album = song_info['album_name']
        audio_file.tag.title = song_info['song_name']
        audio_file.tag.release_date = song_info['release_date']
        audio_file.tag.images.set(3, artwork_data, 'image/jpeg')
        audio_file.tag.save()

    def find_image_path(self, search_query):

        download_directory = os.environ['PWD'] + '/downloads/'

        downloaded_queries = [(d, s, f) for d, s, f in os.walk(download_directory)]

        downloads_subdirs = downloaded_queries[0][1]
        
        downloaded_artwork_dir = [(download_directory + search_query) if search_query in downloads_subdirs else None]

        return downloaded_artwork_dir[0]

    def check_image_uri(self, image_url):

        #print(image_url)
        if "open.spotify.com" in image_url:

            #self.youdown_debug_print("Found Spotify source link")
            return True

        else:
            return False

    def download_youtube_audio(self, url):

        with yd.YoutubeDL(self.yd_opts) as yt_down:
            yt_down.download([url]);
            info_dict = yt_down.extract_info(url,download=False)

        return info_dict

    def download_artwork(self, search_query):

        image_grabber = gig.GoogleImageGrabber()
        sp_srch = spotify_search.Spotify_Search()
        #passing the arguments to the function
        #arguments = {"keywords":search_query,"limit":3, "print_urls":True}   #creating list of arguments  
        image_hosts = image_grabber.download_images(search_query, 3, True)

        return image_hosts

        #self.find_downloaded_image(search_query)

        #song_info = sp_srch.find_song_info(image_hosts[0])
    
        #return song_info

    def youdown_debug_print(self, debug_str, prn_input=False):

        if prn_input:
            ret = input("[YouDown] {}".format(debug_str))
            return ret

        else:
            print("[YouDown] {}".format(str(debug_str)))

if __name__ == '__main__':

    target_url = argv[1]

    youdown = YouDown()

    youdown.download_youtube_song(target_url)

    #video_info = youdown.download_audio(target_url)

    #youdown.download_artwork(video_info.get('title', None)) # get artwork\
