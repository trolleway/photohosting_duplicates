
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
        self.search_at_flickr(photos)
    
    def search_at_flickr(self,photos):
        for photo in photos:
            exiftool.executable ='exiftool.exe'
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
                flickr_state = flickr_instance.search_flickr(timestamp)
                print str(photo).ljust(50),str(flickr_state).ljust(3)
        
        
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
     

     
processor = publicator.Publicator()

processor.cycle_files(files)

raw_input('press any key')
quit()
