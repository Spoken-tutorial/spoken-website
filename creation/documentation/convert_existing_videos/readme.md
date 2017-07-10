# Convert existing files according to changed system
---

### existing .mov files to silent .webm files
---

##### to grant permissions
```
chmod 755 mov_to_silent_audio-video.py
```
##### to run the script
```diff
./mov_to_silent_audio-video.py "folder_path"
 
+ "/" should be present at the end of the folder_path ,i.e,
+ folder_path = "path to the project media folder ({{ media url }}"/videos/
```
 ---
 
 ### existing .ogv files to .mp3 files
 ---
 
##### to grant permissions
```
chmod 755 ogv_to_mp3.py
```
##### to run the script
```diff
./ogv_to_mp3.py "folder_path"

+ "/" should not be present at the end pf the folder_path ,i.e,
+ folder_path = "path to the project media folder ({{ media url }}"/videos
```
---


