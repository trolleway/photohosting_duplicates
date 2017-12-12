
import publicator
import os




def printer(event):
     print ("Как всегда очередной 'Hello World!'")
     

import sys
#encoding = sys.getfilesystemencoding()
                
files=[]
cnt=0
for arg in sys.argv:
    #print arg
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
