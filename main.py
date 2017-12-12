
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
from mapillary import mapillary

import time 
import dateutil.parser as dateparser




          
class PhotohostingsModel:  

    def _get_if_exist(self, data, key):
        if key in data:
            return data[key]
        return None
        
    def get_photo_timestamp(self,exif_data):
        caption = ""
        caption=self._get_if_exist(exif_data, "EXIF:DateTimeOriginal")
        
        return caption

    def cycle_folder(self,folder):
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
        print 'FILENAME'.ljust(30),str('flickr').ljust(10),str('mapillary').ljust(10)
        for photo in photos:
            result=dict()
            result['flickr'] = self.search_at_flickr(photo)
            result['mapillary'] = self.search_at_mapillary(photo)
            
            print os.path.basename(str(photo)).ljust(30),str(result['flickr']).ljust(10),str(result['mapillary']).ljust(10)
    
    def search_at_flickr(self,photo):
        exiftool.executable ='exiftool'
        #convert vales from exiftool to webservice format
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(photo)
            datetimestring = self.get_photo_timestamp(metadata)
            l = list(datetimestring)
            l[4] = '-'
            l[7] = '-'
            datetimestring=''.join(l)

            dt = dateparser.parse(datetimestring)

            timestamp = int(time.mktime(dt.timetuple()))
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        
            flickr_instance = flickr()
            result = flickr_instance.search_flickr(timestamp)
        return result   
        
    def search_at_mapillary(self,photo):
        exiftool.executable ='exiftool'
        #convert vales from exiftool to webservice format
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(photo)
            datetimestring = self.get_photo_timestamp(metadata)
            l = list(datetimestring)
            l[4] = '-'
            l[7] = '-'
            datetimestring=''.join(l)

            dt = dateparser.parse(datetimestring)

            timestamp = int(time.mktime(dt.timetuple()))
            timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S')
        
            mapillry_instance = mapillary()
            result = mapillry_instance.search_mapillary(timestamp)
        return result

        
        
if __name__ == "__main__":        
    files=[]
    cnt=0
    for arg in sys.argv:
        if cnt>0:
            #arge=arg.decode(sys.getfilesystemencoding())
            files.append(arg)
        cnt=cnt+1

'''
если вы уверены, что ввод всегда в Виндовой codepage представим, то просто argv0 = sys.argv[0].decode(sys.getfilesystemencoding()) используйте
'''
     

     
model = PhotohostingsModel()

model.cycle_files(files)

raw_input('press any key')
quit()
