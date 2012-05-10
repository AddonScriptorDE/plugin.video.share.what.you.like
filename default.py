#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, locale, sys, urllib, urllib2, re, os, base64, StoredSession, datetime, base64
from dropbox import client, rest, session
from operator import itemgetter

def index():
        if os.path.exists(TOKEN_FILE):
          addDir(translation(30002),"",'showAllPlaylists',"")
          addDir(translation(30003),"",'addCurrentUrl',"")
          xbmcplugin.endOfDirectory(pluginhandle)

def addCurrentUrl():
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        if playlist.getposition()>=0:
          title = playlist[playlist.getposition()].getdescription()
          title = str(datetime.date.today()).replace("-",".") + " - " + title
          url = playlist[playlist.getposition()].getfilename()
          if url.find("http://")==0 or url.find("rtmp://")==0 or url.find("rtmpe://")==0 or url.find("rtmps://")==0 or url.find("rtmpt://")==0 or url.find("rtmpte://")==0 or url.find("mms://")==0 or url.find("plugin://")==0:
            dialog = xbmcgui.Dialog()
            pl = myPlaylists[dialog.select('Choose playlist', myPlaylists)]
            playlistEntry="###TITLE###="+title+"###URL###="+url+"###PLAYLIST###="+pl+"###END###"
            if os.path.exists(myPlaylist):
              fh = open(myPlaylist, 'r')
              content=fh.read()
              fh.close()
              if content.find(playlistEntry)==-1:
                fh=open(myPlaylist, 'a')
                fh.write(playlistEntry+"\n")
                fh.close()
            else:
              fh=open(myPlaylist, 'a')
              fh.write(playlistEntry+"\n")
              fh.close()
            fh = open(myPlaylist)
            response = dp_client.put_file('/'+username, fh.read(), overwrite=True)
            fh.close()
          else:
            xbmc.executebuiltin('XBMC.Notification(Info:,Current File is no URL!,5000)')
        else:
          xbmc.executebuiltin('XBMC.Notification(Info:,No File playing!,5000)')

def showAllPlaylists():
        resp = dp_client.metadata(current_path)
        if 'contents' in resp:
          for f in resp['contents']:
            name = os.path.basename(f['path'])
            encoding = locale.getdefaultlocale()[1]
            title=('%s' % name).encode(encoding)
            addDir(title,title,'playListMain',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def playListMain(user):
        playListFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+user)
        if user!=username:
          out = open(playListFile, 'w')
          f = dp_client.get_file('/'+user).read()
          out.write(f)
          out.close()
        playlists=[]
        if os.path.exists(playListFile):
          fh = open(playListFile, 'r')
          for line in fh:
            pl=line[line.find("###PLAYLIST###=")+15:]
            pl=pl[:pl.find("###END###")]
            if not pl in playlists:
              playlists.append(pl)
          fh.close()
          for pl in playlists:
            addDir(pl,user+":"+pl,'showPlaylist',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def showPlaylist(url):
        allEntrys=[]
        spl=url.split(":")
        user=spl[0]
        playlist=spl[1]
        fh = open(xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+user), 'r')
        all_lines = fh.readlines()
        for line in all_lines:
          pl=line[line.find("###PLAYLIST###=")+15:]
          pl=pl[:pl.find("###END###")]
          url=line[line.find("###URL###=")+10:]
          url=url[:url.find("###PLAYLIST###")]
          title=line[line.find("###TITLE###=")+12:]
          title=title[:title.find("###URL###")]
          if pl==playlist:
            entry=[title,urllib.quote_plus(url)]
            allEntrys.append(entry)
        fh.close()
        allEntrys=sorted(allEntrys, key=itemgetter(0), reverse=True)
        for entry in allEntrys:
          if user==username:
            addRemovableLink(entry[0],entry[1],'playVideoFromPlaylist',"",pl)
          else:
            addLink(entry[0],entry[1],'playVideoFromPlaylist',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def playVideoFromPlaylist(url):
        listitem = xbmcgui.ListItem(path=urllib.unquote_plus(url))
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def getUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0')
        response = urllib2.urlopen(req,timeout=30)
        link=response.read()
        response.close()
        return link

def parameters_string_to_dict(parameters):
        ''' Convert parameters encoded in a URL to a dict. '''
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict

def addLink(name,url,mode,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=urllib.unquote_plus(url),listitem=liz)
        return ok

def addRemovableLink(name,url,mode,iconimage,playlist):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        playlistEntry="###TITLE###="+name+"###URL###="+urllib.unquote_plus(url)+"###PLAYLIST###="+playlist+"###END###"
        liz.addContextMenuItems([('Remove from Playlist', 'XBMC.RunScript(special://home/addons/'+addonID+'/removeFromPlaylist.py,'+urllib.quote_plus(playlistEntry)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

pluginhandle=int(sys.argv[1])

addonID = "plugin.video.share.what.you.like"
settings = xbmcaddon.Addon(id=addonID)
translation = settings.getLocalizedString

username=settings.getSetting("user")
if username=="":
  settings.openSettings()
  username=settings.getSetting("user")

myPlaylist=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+username)
TOKEN_FILE=xbmc.translatePath("special://profile/addon_data/"+addonID+"/dropbox.token")
str1=base64.b64decode('bWJzdjhxN3JlZ3FhNWNn')
str2=base64.b64decode('OTRiMmpvN3kzaDhpYW84')

sess = StoredSession.StoredSession(str1, str2, access_type='app_folder')
dp_client = client.DropboxClient(sess)
sess.load_creds()
current_path = ''
if not sess.is_linked():
  sess.link()

playlistsTemp=[]
for i in range(0,9,1):
  playlistsTemp.append(settings.getSetting("pl"+str(i)))
myPlaylists=[]
for pl in playlistsTemp:
  if pl!="":
    myPlaylists.append(pl)

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'addCurrentUrl':
    addCurrentUrl()
elif mode == 'showAllPlaylists':
    showAllPlaylists()
elif mode == 'playListMain':
    playListMain(url)
elif mode == 'showPlaylist':
    showPlaylist(url)
elif mode == 'playVideoFromPlaylist':
    playVideoFromPlaylist(url)
elif mode == 'managePlaylist':
    managePlaylist()
else:
    index()