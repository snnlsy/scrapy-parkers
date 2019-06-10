import scrapy
import urllib.request
import re
import os
from random import randint
import requests
from os import system


proxies = {'http':  'socks5://127.0.0.1:9050',
           'https': 'socks5://127.0.0.1:9050'
	      }


def changIP():
    session = requests.session()
    session.proxies = proxies
    #print (session.get("http://httpbin.org/ip").text)
    system("sudo service tor reload") #sudo apt-get install tor


class CarsSpider(scrapy.Spider):
    name = "cars"
    website = "https://www.parkers.co.uk"
    count_page = 1

    file = open("cars1.txt","w", 1, encoding = "UTF-8")
    start_urls = [
        "https://www.parkers.co.uk/cars-for-sale/used/?page=11339"
    ]


    def blackList(self, black):
        blackList = ["Aston", "Alfa"]
        
        for x in blackList:
            if(black == x):
                return True
        return False
    

    # e.g. title = 'Aston Martin DB9 (2008) '  
    def parseTitle(self, title):
        # e.g. list_title = ['Renault', 'Laguna', 'Hatchback', '(2003)', '']
        list_title = title.split(" ")

        # e.g. year = '(2003)'
        year = list_title[-2]
        
        # e.g. year 2003
        year = re.sub("\(|\)", "", year)

        # e.g. list_title = ['Renault', 'Laguna', 'Hatchback']
        list_title.pop(-1)
        list_title.pop(-1)
        
        
        make = list_title[0]
        
        if( self.blackList(make) ):
            # e.g. Aston_Martin
            make = list_title[0] + "_" + list_title[1]
            list_title.pop(1)
        
        list_title.pop(0)
        
        # e.g. "Laguna_Hatcback"
        model = '_'.join(list_title)
        # "abc-fgh" -> "abc_fgh"
        model = model.replace('-', '_')

        
        return make, model, year


    def createDir(self, make, model, year):
        path_dir_photo = "/home/ekin/Desktop/MMR/2/" + make + "/" + model + "/" + year + "/"
        if not os.path.exists(path_dir_photo):
            os.makedirs(path_dir_photo)
        return path_dir_photo

    
    # inside of post
    def parse2(self, response):
        title = response.css("h1.main-heading__title::text").extract_first()
        make, model, year = self.parseTitle(title)
        list_photo = response.css("a.rsImg::attr(href)").extract()
        """
        self.file.write( "--------------------------------------------------\n")
        self.file.write( make + "\n")
        self.file.write( model + "\n")
        self.file.write( year + "\n")
        self.file.write( "--------------------------------------------------\n")
        """

        changIP()

       
        for photo in list_photo:
            path_dir_photo = self.createDir(make, model, year)

            id_photo = randint(1111111,9999999)
            name_photo = str(id_photo) + "_" + make + "-" + model + "-" + str(year) 

            path_photo = path_dir_photo + name_photo

            # save photo to location:"photo"
            urllib.request.urlretrieve(photo, path_photo)





    def parse(self, response):

        # visits posts one by one
        list_post = response.css("a.panel__primary-link::attr(href)").extract()
        for post in list_post:
            post = self.website + post
            yield scrapy.Request(url = post, callback = self.parse2)
        
        # passes next page
        next_url = self.website + response.css("div.results-paging__next a::attr(href)").extract_first()
        yield scrapy.Request(url = next_url, callback = self.parse)



