
import os


import sys
import datetime
import pyexiv2
import re
from dateutil.tz import tzlocal
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import urllib2
import json
import shutil
import exiftool

from flickr import flickr

import time 
import dateutil.parser as dateparser

          
class Publicator:  

    def _get_if_exist(self, data, key):
        if key in data:
            return data[key]
        return None
        
    def get_photo_timestamp(self,exif_data):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        caption = ""
        caption=self._get_if_exist(exif_data, "EXIF:DateTimeOriginal")
        
        return caption
    
   
    
    def cycle_folder(self,folder):
    #Прочитать список фото в каталоге
        photos=[]
        cnt=1
        for dirpath, dnames, fnames in os.walk(folder):
            for f in fnames:
                if f.lower().endswith(".jpg"):
                    d = dict(filepath=os.path.join(dirpath, f),cnt=cnt)
                    photos.append(d)
                    cnt+1    
        self.search_at_flickr(photos)
                    
    def cycle_files(self,photos):
    #Прочитать список фото в каталоге
        
        self.search_at_flickr(photos)
    
    def search_at_flickr(self,photos):
        
        #Прочитать дату сьёмки, наличие подписи
        for photo in photos:

            exiftool.executable ='g:\PHOTO\z_bat\publicator\exiftool.exe'
            with exiftool.ExifTool() as et:
                #metadata = et.get_metadata(photo['filepath'])
                metadata = et.get_metadata(photo)
                datetimestring = self.get_photo_timestamp(metadata)

                
                l = list(datetimestring)
                l[4] = '-'
                l[7] = '-'
                datetimestring=''.join(l)

                #print datetimestring[4]
                #datetimestring[8]='-'

                dt = dateparser.parse(datetimestring)

                timestamp = int(time.mktime(dt.timetuple()))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')

                #Поискать это фото по времени на flickr
                
                flickr_instance = flickr()
                flickr_state = flickr_instance.search_flickr(timestamp)
                print str(photo).ljust(50),str(flickr_state).ljust(3)
        #вывести на экран

