
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

    exiftool_path = 'exiftool'
    mapillary_skip_words = ['crop','ShiftN']

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
                    
    def scan_files(self,photos):
        photos_data = list()
        mapillary_skip_words = self.mapillary_skip_words
        print 'FILENAME'.ljust(40),str('flickr').ljust(10),str('mapillary').ljust(10)
        for photo in photos:
            result=dict()
            result['filepath'] = str(photo)
            result['mapillary_ready'] = self.ready_for_mapillary(photo,mapillary_skip_words)
            result['flickr'] = 0
            #result['flickr'] = self.search_at_flickr(photo)
            result['mapillary'] = self.search_at_mapillary(photo)
            
            
            print os.path.basename(str(photo)).ljust(40),str(result['flickr']).ljust(10),str(result['mapillary']).ljust(10),str(result['mapillary_ready']).ljust(6)
            photos_data.append(result)
        return photos_data
    
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
        exiftool.executable = self.exiftool_path
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
    
    def ready_for_mapillary(self,photo,skip_words=None):
        #check if photo has lat, lon and direction tags
        exiftool.executable = self.exiftool_path
        #convert vales from exiftool to webservice format
        #import json
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(photo)
            #print(json.dumps(metadata, indent = 4))

            direction = self._get_if_exist(metadata, "EXIF:GPSImgDirection")
            if direction is None:
                return False
            lat = self._get_if_exist(metadata, "EXIF:GPSLatitude")
            if lat is None:
                return False
            if skip_words is not None:
                for word in skip_words:
                    if word in os.path.basename(str(photo)):
                        return False
            return True
    
    def copy_for_mapillary(self,photos_data):
        folder='C:/temp/mapillary/'
        import shutil
        try:
            shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder)
        except: #second time
            shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder)            
        for photo in photos_data:
            if photo['mapillary_ready'] == True and photo['mapillary'] ==0:

                print photo['filepath']
                shutil.copy(photo['filepath'],folder)

        
        
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

photos_data = model.scan_files(files)

command = None
while command not in (0,1):
    dir1 = os.path.dirname(os.path.realpath(__file__))
    command = raw_input('Enter 0 for quit, 1 for copy files for mapillary ')
    try: 
        command = int(command)
    except ValueError:
        command = None
    if command == 0:
        quit()
    elif command == 1:
        #run and not close at Win after error
        try:
            model.copy_for_mapillary(photos_data)
        except:
            import sys
            print sys.exc_info()[0]
            import traceback
            print traceback.format_exc()
            print "Press Enter to continue ..." 
            raw_input() 
        
        
