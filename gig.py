#!/usr/bin/python3
import sys, json, os, spotify_search, urllib.request, urllib.parse
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
#from urllib import request

class GoogleImageGrabber(object):

    def __init__(self):

        #gig_driver_opt = webdriver.FirefoxOptions()
        #gig_driver_opt.add_argument('--headless')

        #self.gig_browser = webdriver.Firefox(options=gig_driver_opt)
        pass

    def find_images(self, page, img_count):

        #images = page.find_element_by_id('rg_s')

        #import pdb; pdb.set_trace()

        #image_meta_divs = images.find_elements_by_class_name('rg_meta')
        image_meta_divs = page.find_all("div", {"class": "rg_meta"})

        image_meta_data = []

        for ind, image_meta in enumerate(image_meta_divs):

            #print(ind)

            if ind == img_count:
                break

            else:

                start_elem = str(image_meta).find('>{') + 1
                end_elem = str(image_meta).find('}<') + 1

                # image_meta.get_attribute('outerHTML')[start_elem:end_elem]

                image_json_string = str(str(image_meta)[start_elem:end_elem])

                image_json_byte = bytes(image_json_string, "utf-8").decode('unicode_escape')

                #print(image_json_string)

                image_json = json.loads(image_json_string)

                #print(image_json['ow'])

                image_meta_data.append(image_json)

        return image_meta_data

        '''for num in range(img_count):

            target_images.append(images[num])

        return(target_images, page)'''

    def download_image_set(self, image_set, img_search):

        image_host_set = []
        
        for ind, img in enumerate(image_set):

            if not os.path.exists('downloads'):
                os.mkdir("downloads")

            #print(img['ru'])
            image_host_set.append(img['ru'])
            
            #import pdb; pdb.set_trace()

            try:
                urllib.request.urlretrieve(img['ou'], ("%s/%s/%s/%s.jpg" % (os.environ['PWD'], 'downloads', img_search, ind)))

            except Exception as e:
                
                print(str(e))

        return image_host_set

    def download_paths(self, img_search):

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        if not os.path.exists('downloads/' + img_search):
            os.makedirs('downloads/' + img_search)
        
    def download_images(self, search_target, limit=100, return_host=False):

        self.download_paths(search_target)

        search_query = "https://www.google.com/search?hl=en&site=imghp&tbm=isch&source=hp&q="
        search_query = search_query + search_target + "&tbs=iar:s"
        search_query = search_query.replace(" ", "+")

        import pdb; pdb.set_trace()

        #self.gig_browser.get(search_query + search_target + "&tbs=iar:s")

        #source = self.gig_browser.find_element_by_tag_name("body")

        try:

            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
            image_search_req = urllib.request.Request(search_query, headers=headers)

            image_search_resp = urllib.request.urlopen(image_search_req)
            image_search_page = image_search_resp
            image_search_soup = BeautifulSoup(image_search_page, 'html.parser')

            source = image_search_soup.find("body")

        except UnicodeEncodeError:

            if return_host:

                hosts = ['None']

                return hosts

    
        #images
        #import pdb; pdb.set_trace()

        imgset = self.find_images(source, limit)

        image_hosts = self.download_image_set(imgset, search_target)

        if return_host:
            return image_hosts


if __name__ == '__main__':

    Application = GoogleImageGrabber()
    sp_srch = spotify_search.Spotify_Search()
    image_hosts = Application.download_images(sys.argv[1], int(sys.argv[2]), True)

    song_info = [sp_srch.find_song_info(host) for host in image_hosts]
    
