#REQUIREMENTS
#https://github.com/yoavaviram/python-google-spreadsheet
#http://code.google.com/p/gdata-python-client/
#https://github.com/maxcutler/python-wordpress-xmlrpc/
#https://github.com/soundcloud/soundcloud-python
#http://code.google.com/p/mutagen/


from google_spreadsheet.api import SpreadsheetAPI


from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

import urllib2

import httplib, urllib

import datetime, time

import soundcloud

#sitedetails

siteURL = 'theWebsiteURL'
s3IconURL = 'theIconURL'
s3AudioURL = 'theAudioURL'

#connect to WP - use a seperate account from your admin account
wp = Client( siteURL + 'xmlrpc.php', 'wpUser', 'wpPassword')

#connect to Soundcloud - you'll need to register an app with Soundcloud
sc = soundcloud.Client(client_id='scID', client_secret='scSecret',username='scUsername', password='scPassword')

#connect to google spreadsheets, again, don't use your own, create a new user and share the spreadsheet with them
googapi = SpreadsheetAPI('gEmail', 'gPassword', 'gUser')

# get the spreadsheet. You'll need it's unique ID. You can find this by playing with the API
spreadsheet = googapi.get_worksheet('ssUID','ssSheet')
rows = spreadsheet.get_rows()

#get information on today's post from the spreadsheet
today = datetime.date.today()

for x in rows:
    if x['pubdate'] == today.strftime('%d/%m/%Y'):
        print("Posting Chapter " + x['chapter'])
        
        chapNum = x['chapter']
        chapTitle = x['title']
        Reader = x['reader']
        Artist = x['artist']
        Recorder = x['recorder']
        SoundCloudURL = x['audio']
        Image = x['image']
        Image2 = x['image2']
        Image3 = x['image3']
        Image4 = x['image4']
        Video = x['video']
        Credit = x['credit']
        AltCode = x['altcode']
        Loop = x['videoloop']
        
        #Check if there's already a post made (change/remove as you need)
        if SoundCloudURL != 'http://soundcloud.com/test.../':
        
            #add artwork to mp3 file
            
            audio = MP3('audio/' + SoundCloudURL, ID3=ID3)
            
            # add ID3 tag if it doesn't exist
            try:
                audio.add_tags()
            except error:
                pass
            
            audio.tags.add(
                APIC(
                    encoding=3, # 3 is for utf-8
                    mime='image/png', # image/jpeg or image/png
                    type=3, # 3 is for the cover image
                    desc=u'Cover',
                    data=open('audio/artwork.jpg').read()
                )
            )
            audio.save()
            
            
            #Build the SoundCloud post
            theDescription = ''
            
            if Recorder != 'none':
                theDescription = theDescription + '<p>Recorded by '+Recorder+'</p>'
            else:
                theDescription = theDescription + '<p></p>'
            
            theDescription = theDescription + '<p>Blurb</p>'    
            
            track = sc.post('/tracks', track={
                'title': 'Chapter ' + chapNum + ': ' + chapTitle + ' - Read by ' + Reader + ' - http://mobydickbigread.com',
                #'asset_data':trackresponse.read()
                'downloadable': True,
                'streamable': True,
                'artwork_data': open('audio/artwork.jpg', 'rb'),
                'embeddable_by': 'all',
                'sharing': 'public',
                'genre': 'Spoken',
                'description': theDescription,
                'tag_list': 'list-of-tags',
                'asset_data': open('audio/' + SoundCloudURL, 'rb')
            })
            
#get the url of the uploaded SoundCloud post
            SoundCloudURL = track.permalink_url
        
        
        #create the wordpress post
        
        post = WordPressPost()
        
        post.title = 'Chapter ' + str(chapNum) + ': ' + chapTitle
        HTMLtitle = '<span class="altcolor">Chapter ' + str(chapNum) + ':</span> ' + chapTitle
        
        post.custom_fields = []
        post.custom_fields.append({'key': 'HTML_title','value': HTMLtitle})
        
        post.content = '<span class="list-text"><em><strong>Read by ' + Reader + '</strong></em>\n'
        post.content = post.content + '<em>Artist: ' + Artist + '</em></span>\n'
        post.content = post.content + '<!--more-->\n'
        post.content = post.content + '<div id="the_player">\n'
        post.content = post.content + '<strong>Read by ' + Reader + '</strong>\n'
        if Recorder != 'none':
            post.content = post.content + 'Introduced by Peter Donaldson and Recorded by '+Recorder+'\n'
        else:
            post.content = post.content + 'Introduced by Peter Donaldson <span class=\"invisRec\">Recorded by '+Recorder+'</span>\n'
        post.content = post.content + '<a class="sc-player" href="'+SoundCloudURL+'">'+chapTitle+'</a>\n'
        
        post.content = post.content + '</div>\n'
        post.content = post.content + '<div class="bigborder artwork">\n'
        post.content = post.content + 'Artist: ' + Artist + '\n'
        if Video == 'none':
            if AltCode != 'none':
                post.content = post.content + AltCode
            else:
                post.content = post.content + '<a href="'+Image+'"><img class="aligncenter size-large" title="'+chapTitle+'" src="'+Image+'" alt=""/></a>\n'
                if x['multiple'] == "yes":
                    if Image2 != 'none':
                        post.content = post.content + '<a href="'+Image2+'"><img class="aligncenter size-large" title="'+chapTitle+'" src="'+Image2+'" alt=""/></a>\n'
                    if Image3 != 'none':
                        post.content = post.content + '<a href="'+Image3+'"><img class="aligncenter size-large" title="'+chapTitle+'" src="'+Image3+'" alt=""/></a>\n'
                    if Image4 != 'none':
                        post.content = post.content + '<a href="'+Image4+'"><img class="aligncenter size-large" title="'+chapTitle+'" src="'+Image4+'" alt=""/></a>\n'    
        else:
            post.content = post.content + '<video class="sublime aligncenter size-large" poster="'+Image+'" preload="none" height="480" width="720">\n'
            post.content = post.content + '<source src="'+ Video +'" />\n'
            post.content = post.content + '</video>\n'
                
        if Credit != 'none':
            post.content = post.content + '<p>'+ Credit +'</p>\n'
        post.content = post.content + '</div>\n'
        
        if Loop == "yes":
            post.content = post.content + '<script type=\"text/javascript\">'
            post.content = post.content + 'sublimevideo.ready(function() {'
            post.content = post.content + 'sublimevideo.onEnd(function(sv) {'
            post.content = post.content + 'sublimevideo.play(sv.element);'
            post.content = post.content + '});'
            post.content = post.content + '});'
            post.content = post.content + '</script>\n'
        
        
        # set to the path to your file
        filename = s3IconURL + 'chap' + str(chapNum) + '.png'
        
        # prepare metadata
        data = {
                'name': 'chap' + str(chapNum) + '.png',
                'type': 'image/png',  # mimetype
        }
        
        IconResponse = urllib2.urlopen(filename)
        #html = response.read()
        data['bits'] = xmlrpc_client.Binary(IconResponse.read())
        
        #with open(filename, 'rb') as img:
        #        data['bits'] = xmlrpc_clent.Binary(img.read())
        
        the_response = wp.call(media.UploadFile(data))
        attachment_id = the_response['id']
        post.thumbnail = attachment_id
        
        #publish it
        post.post_status = 'publish'
        
        wp.call(posts.NewPost(post))
        print("Posted!")
