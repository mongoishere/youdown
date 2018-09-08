#!/usr/bin/python3
import sys, json, os, request, spotify_search
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib import request

class GoogleImageGrabber(object):

    def __init__(self):

        gig_driver_opt = webdriver.FirefoxOptions()
        gig_driver_opt.add_argument('--headless')

        self.gig_browser = webdriver.Firefox(options=gig_driver_opt)

    def find_images(self, page, img_count):

        images = page.find_element_by_id('rg_s')

        image_meta_divs = images.find_elements_by_class_name('rg_meta')

        image_meta_data = []

        for ind, image_meta in enumerate(image_meta_divs):

            #print(ind)

            if ind == img_count:
                break

            else:   
                start_elem = image_meta.get_attribute('outerHTML').find('{')
                end_elem = image_meta.get_attribute('outerHTML').find('}') + 1

                # image_meta.get_attribute('outerHTML')[start_elem:end_elem]

                image_json_string = str(image_meta.get_attribute('outerHTML')[start_elem:end_elem])

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

            request.urlretrieve(img['ou'], ("%s/%s/%s.jpg" % ('downloads', img_search, ind)))

        return image_host_set

    def download_paths(self, img_search):

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        if not os.path.exists('downloads/' + img_search):
            os.makedirs('downloads/' + img_search)
        
    def download_images(self, search_target, limit=100, return_host=False):

        self.download_paths(search_target)

        search_query = "https://www.google.com/search?hl=en&site=imghp&tbm=isch&source=hp&q="

        self.gig_browser.get(search_query + search_target)

        source = self.gig_browser.find_element_by_tag_name("body")

        imgset = self.find_images(source, limit)

        image_hosts = self.download_image_set(imgset, search_target)

        if return_host:
            return image_hosts


if __name__ == '__main__':

    Application = GoogleImageGrabber()
    sp_srch = spotify_search.Spotify_Search()
    image_hosts = Application.download_images(sys.argv[1], int(sys.argv[2]), True)

    song_info = [sp_srch.find_song_info(host) for host in image_hosts]
    