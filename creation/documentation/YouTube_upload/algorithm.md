# You Tube Data API
---

### Editing file

in cron folder create a __upload_videos.py__ and __client_secrets.json__

---

### Upload tutorial to Channel process  

---

##### API used

* You Tube Data API
* google-api-python-client

---

##### Algorithm
* We used the You Tube Data API to upload the video.
* As it provide its own sample code to upload the video files to the channel.
* Only we have to create a client_secrets.json file , which stores the channel and token credentials.
```diff
  {
    "web": {
      "client_id": "1785498628-tu3mivvpbequuel8nfh1m44ju3sbh6jv.apps.googleusercontent.com",
      "client_secret": "bIPRMRUgiDFGrQ5SvhAKq4kY",
      "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob","http://localhost"],
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
  }
+ file name : clients_secrets.json  
```
* Follow to steps given in following link to understand and configure script file in the folder :
  [upload_video](https://developers.google.com/youtube/v3/guides/uploading_a_video)
  
* We have to make some changes to link this script with the project :
  * Call the main function from the file in which we are fetching the tutorials  which are not yet uploaded and sending  
    their file path as a parameter to the upload script
  * After the successful upload return the video_id returned from the You-Tube and update the database ot make it as uploaded.
  * Replace the main function of the upload script with the given below :
  ```diff
    def main_function(argu):
      youtube = get_authenticated_service(argu)
      try:
        value=initialize_upload(youtube, argu)
        return value
      except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  + get_authenticated_service() : returns a you tube channel object
  + initialize_upload() : initiates the upload and returns the you-tube uploaded video_id
  ```
* When you runs the script first time it will ask for authentication.
* Once authenticated it creates a upload_video.py-aouth2.json file which stores the login and token verification credentials.
* For next time we don't need to authenticate manually it will automatically authenticate.
```diff
  {
    "_module": "oauth2client.client", 
    "scopes": ["https://www.googleapis.com/auth/youtube.upload"], 
    "token_expiry": "2017-06-17T20:43:07Z", 
    "id_token": null, 
    "user_agent": null, 
    "access_token": "ya29.GltsBP6ji3WaBS9UVbNoSpBe9zCB8GxLjEa8ceiC8A1Vw5jdPweA5GU3bK0_e6j9tjQQ4ucj1HYlsuuRi7Rm0910LaCJ0dotjl_hvs-wtPQXCy6cwiDvc4HForKq", 
    "token_uri": "https://accounts.google.com/o/oauth2/token", 
    "invalid": false, 
    "token_response": {"access_token": "ya29.GltsBP6ji3WaBS9UVbNoSpBe9zCB8GxLjEa8ceiC8A1Vw5jdPweA5GU3bK0_e6j9tjQQ4ucj1HYlsuuRi7Rm0910LaCJ0dotjl_hvs-wtPQXCy6cwiDvc4HForKq", 
    "token_type": "Bearer", 
    "expires_in": 3600, 
    "refresh_token": "1/R3v4lF6sLge92W8bkpBY6_9Alp8CueO2C6i4oRubC2Q71TPOSFp3QQdmTHikroof"}, 
    "client_id": "1785498628-tu3mivvpbequuel8nfh1m44ju3sbh6jv.apps.googleusercontent.com", 
    "token_info_uri": "https://www.googleapis.com/oauth2/v3/tokeninfo", 
    "client_secret": "bIPRMRUgiDFGrQ5SvhAKq4kY", 
    "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", 
    "_class": "OAuth2Credentials", 
    "refresh_token": "1/R3v4lF6sLge92W8bkpBY6_9Alp8CueO2C6i4oRubC2Q71TPOSFp3QQdmTHikroof", 
    "id_token_jwt": null
  }
 + file name upload_video.py-aouth2.json will be automatically created
```
* The returned video id will be returned after successful upload.

---

[Register your application here](https://developers.google.com/youtube/registering_an_application) for OAuth 2.0 protocol to  
 authorize access to user data.

---
