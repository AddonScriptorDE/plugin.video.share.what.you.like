import xbmc,os,xbmcgui
from dropbox import client, rest, session

class StoredSession(session.DropboxSession):
    addonID = "plugin.video.share.what.you.like"
    addon_work_folder=xbmc.translatePath("special://profile/addon_data/"+addonID)
    TOKEN_FILE=xbmc.translatePath("special://profile/addon_data/"+addonID+"/dropbox.token")

    if not os.path.isdir(addon_work_folder):
      os.mkdir(addon_work_folder)

    def load_creds(self):
        try:
            stored_creds = open(self.TOKEN_FILE).read()
            self.set_token(*stored_creds.split('|'))
        except IOError:
            pass

    def write_creds(self, token):
        f = open(self.TOKEN_FILE, 'w')
        f.write("|".join([token.key, token.secret]))
        f.close()

    def delete_creds(self):
        os.unlink(self.TOKEN_FILE)

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        url1=url[:url.find("?oauth")+1]
        url2=url[url.find("?oauth")+1:]
        dialog = xbmcgui.Dialog()
        done=False
        while (done==False):
          try:
            ok = dialog.ok('Open authentication Link to continue:', url1 + "\n" + url2)
            if ok==False:
              done=True
            if done==False:
              self.obtain_access_token(request_token)
              self.write_creds(self.token)
              done=True
          except:
            pass

    def unlink(self):
        self.delete_creds()
        session.DropboxSession.unlink(self)