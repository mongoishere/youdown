import os, sys, urllib
from selenium import webdriver
from bs4 import BeautifulSoup

class Spotify_Search(object):

    def __init__(self):

        pass

    def get_link_info(self, tgt_link):

        link_type_str = 