#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
from shutil import copyfile
import os

import flickrapi
import flickr_keys
import sqlite3
import webbrowser

class flickr:

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def __init__(self):
    
        import flickr_keys
        
        #flickr
        self.data = []
        self.api_key=flickr_keys.api_key
        self.api_secret=flickr_keys.api_secret
        self.conf_user='24415554@N04'
        self.DEBUG = False
        


        
    def search_flickr(self,timestamp):
        self.flickrLogin()
        photo_data = self.flickr.photos.search(
        api_key=self.api_key,
        user_id=self.conf_user,
        per_page=4,
        min_taken_date=timestamp,
        max_taken_date=timestamp
        )

        return int(photo_data['photos']['total'])
        
    
    def getDescription(self,photoInfo):

        from alphabet_detector import AlphabetDetector
        ad = AlphabetDetector()
        
        text=u''
        
        descriptionString=photoInfo['photo']['description']['_content']
        for line in descriptionString.splitlines():
            if not 'CYRILLIC' in ad.detect_alphabet(line):
                text+="\n"+line
        
        return text
        
    def flickrLogin(self):
    


                
        #heroku+flickrapi hack
        #flickrapi does not allow change of path to local file with access token. It store in /tmp/.flickr/oauth-tokens.sqlite. My script deployed in heroku, and tmp folder is removed after script end.
        #so after login oauth-tokens.sqlite copying to script folder, and before login - copyng to temp folder.

        tokens_tmp_folder = os.path.expanduser(os.path.join("~", ".flickr"))
        tokens_filename = os.path.join(tokens_tmp_folder, 'oauth-tokens.sqlite') 

        tokens_tmp_path = tokens_filename
        tokens_longstore_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'oauth-tokens.sqlite')

        
        if not os.path.exists(tokens_tmp_folder):
            os.makedirs(tokens_tmp_folder)
        if os.path.isfile(tokens_longstore_path):
            copyfile(tokens_longstore_path,tokens_tmp_path)
            
        #end of heroku+flickrapi hack, use flickrapi normally

        self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret, format='parsed-json')

        # Only do this if we don't have a valid token already
        if not self.flickr.token_valid(perms='read'):

            # Get a request token
            self.flickr.get_request_token(oauth_callback='oob')

            # Open a browser at the authentication URL. Do this however
            # you want, as long as the user visits that URL.
            authorize_url = self.flickr.auth_url(perms=u'write')
            webbrowser.open_new_tab(authorize_url)
            print 'Authorize this app in browser: '+authorize_url

            # Get the verifier code from the user. Do this however you
            # want, as long as the user gives the application the code.
            verifier = unicode(raw_input('Verifier code: '))

            # Trade the request token for an access token
            self.flickr.get_access_token(verifier)

        #print('Step 2: use Flickr')

        copyfile(tokens_tmp_path, tokens_longstore_path) #heroku+flickrapi hack



        
        

        
    def loadSets(self,sqliteConn):
        
            try:
                collections = self.flickr.collections.getTree(collection_id = self.flickrCollection,)
            except Exception as e:
                print ('ERROR. Empty feeder '+self.flickrCollection)
                return 0
            else:
                pass  
            
            sql='CREATE TABLE sets (id INTEGER PRIMARY KEY, title text, name text, setId text);'
            sqliteConn.execute(sql)
            
            for collection in collections['collections']['collection']:

                if 'set' in collection:
                    currentCollection=collection['title']
                    print str(len(collection['set'])) + ' sets in collection '+ collection['title']
                    for set in collection['set']:

                        sql='INSERT INTO sets (title,name,setId) VALUES(?, ?, ?);'

                        sqliteConn.execute(sql,[collection['title'],set['title'],set['id']])
        

            self.sqlite.commit()
            
            for row in sqliteConn.execute('SELECT * FROM sets ORDER BY id'):

                pass
        
        
        
        
    def crawlPhotos(self,sqliteConn):
        
            #my home windows install sort of broken, so i did not use spatial extensions    
            sql='CREATE TABLE setsphotos (id INTEGER PRIMARY KEY, set_id INTEGER, photo_id INTEGER, title TEXT, urlOriginal text, urlLarge text, lat text, lon text, description TEXT, url TEXT, equirectangular Boolean);'
            sqliteConn.execute(sql)            
            sql='CREATE TABLE tags (id INTEGER PRIMARY KEY, photo_id INTEGER, tag TEXT, machine_tag BOOLEAN);'
            sqliteConn.execute(sql)
            
            for row in sqliteConn.execute('SELECT * FROM sets ORDER BY id'):
                print 'crawl photos in set ' + str(row[2].encode('utf-8'))
                feeder_photoset_id=row[3]
                
                try:
                    photos = self.flickr.photosets.getPhotos(photoset_id = feeder_photoset_id,user_id=self.conf_user)
                except Exception as e:
                    print ('ERROR. Cannot get photo in set '+feeder_photoset_id)
                    return 0

                    

                
                
                for photo in photos['photoset']['photo']:    
                    dbPhoto=dict()
                    photo_id=photo['id']
                    dbPhoto['id']=photo['id']
                    dbPhoto['title']=photo['title']
                    photo_data = self.flickr.photos.getSizes(photo_id=photo_id)
                    
                    for d in photo_data['sizes']['size']:
                        if d['label']=='Original':
                            dbPhoto['urlSource']=d['source']
                        if d['label']=='Large':
                            dbPhoto['urlLarge']=d['source']
                    if ('urlLarge' not in dbPhoto): 
                        dbPhoto['urlLarge'] = dbPhoto['urlSource']
                    

                    photoInfo=self.flickr.photos.getInfo(photo_id=photo_id)

                    location = photoInfo['photo'].get('location',dict())
                    dbPhoto['lat']=str(location.get('latitude',''))
                    dbPhoto['lon']=str(location.get('longitude',''))
                    dbPhoto['description']=photoInfo['photo']['description']['_content']
                    dbPhoto['url']=photoInfo['photo']['urls']['url'][0]['_content']
                    
                    #pp.pprint(photoInfo)
                    #quit()
                    equirectangular=0
                    for tag in photoInfo['photo']['tags']['tag']:
                        sql='INSERT INTO tags (photo_id, tag, machine_tag) VALUES(?, ?, ?);'
                        sqliteConn.execute(sql,[dbPhoto['id'], tag['_content'], tag['machine_tag'] ])
                        self.sqlite.commit()
                        if (tag['_content']=='equirectangular'):
                            equirectangular=1
                            
                    try:
                        sql='INSERT INTO setsphotos (set_id , photo_id , title , urlOriginal , urlLarge , lat,  lon , description, url, equirectangular) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                        sqliteConn.execute(sql,[feeder_photoset_id, dbPhoto['id'], dbPhoto['title'], dbPhoto['urlSource'], dbPhoto['urlLarge'], dbPhoto['lat'], dbPhoto['lon'], dbPhoto['description'], dbPhoto['url'],equirectangular ])
                        self.sqlite.commit()    
                        print dbPhoto['title']
                    except Exception as e:
                        print ('ERROR. photo='+str(dbPhoto['id']) , sys.exc_info())
                        return 0               

                    
    def render(self,sqliteConn):
            websitefolder='website'
            for row in sqliteConn.execute('SELECT * FROM sets ORDER BY id'):
                #print row[3]
                #feeder_photoset_id=row[3]
                #print cur.fetchone()["name"]
                import pprint 
                pp = pprint.PrettyPrinter()
                #pp.pprint(row)
                pagename=row[2]
                if not os.path.exists(os.path.join(websitefolder,'content','post')):
                    os.makedirs(os.path.join(websitefolder,'content','post'))
                filename = os.path.join(websitefolder,'content','post',pagename.replace(' ','_')+'.md')
                print 'write page to '+filename
                f = open(filename,'w')
                f.write('+++\n')
                f.write('title = "'+row[2]+'"\n')
                f.write('date = "1970-01-01"\n')
                f.write('tags = [ ]"\n')
                f.write('categories = [ ]"\n')

                f.write('+++\n')

                print 'SELECT * FROM setsphotos WHERE set_id ="'+row[3]+'" ORDER BY id '

                for rowPhoto in sqliteConn.execute('SELECT * FROM setsphotos WHERE set_id ="'+row[3]+'" ORDER BY id '):
                    f.write(u'<a data-flickr-embed="true" data-footer="true"  href="{url}" title="HARDCODED"><img src="{src}" alt="{alt}"></a><script async src="http://embedr.flickr.com/assets/client-code.js" charset="utf-8"></script>'.format(url=rowPhoto[9],src=rowPhoto[5],alt=rowPhoto[3]) )
                    f.write("</br> \n")

                f.close()
            
    def dropdb(self):
            if os.path.exists(self.dbPath):
                os.remove(self.dbPath)
    

    def procedure(self):
        #self.dropdb()
            
        self.sqlite=sqlite3.connect(self.dbPath)
        self.row_factory = self.dict_factory
        sqliteConn = self.sqlite.cursor()
        print "Database created and opened succesfully"

        
      


    
     
        self.flickrLogin(sqliteConn)
        self.loadSets(sqliteConn)
        self.crawlPhotos(sqliteConn)       
        self.render(sqliteConn)
                
        sqliteConn.close()
        quit()
        
