# Creation module
---

### Editing file

static/spoken/templates-watch_tutorial.html

---

### Integrating AVS-Player wiht the current project 
```diff
+ Require .webm and .mp3 files separately
```
---

#### Algorithm

```diff
+ AVS-Player is designed and coded already, we have integrated it with the current project  
+ by selecting suitable file formats and solving all syncing problems.
```
---

* Include the js and css files of AVS-Player in the folder :
  * static/spoken/css : for avs.player.css file
  ```
    <link href="{% static 'spoken/css/avs.player.css' %}" rel="stylesheet" type="text/css">
  ```
  * static/spoken/js : avs.player.min.js file
  ```
    <script src="{% static 'spoken/js/avs.player.min.js' %}"></script>
  ```
* Replaced the video tag of video.js with the AVS-Player one. 
```diff
  <video id="video1" preload="none" width="100%" height="430"  poster="{{ tr_rec.tutorial_detail|get_thumb_path:'Big' }}" data-setup="{}">
    <source src="{{ media_url }}videos/{{ tr_rec.tutorial_detail.foss_id }}/{{ tr_rec.tutorial_detail_id }}/{{video}}.webm" type="video/webm" />
    {{ tr_rec|get_srt_path|safe }}
  </video>
  <audio id="audio1" preload="none">
    <source id="audio" src="{{ media_url }}videos/{{ tr_rec.tutorial_detail.foss_id }}/{{ tr_rec.tutorial_detail_id }}/{{video}}-{{lang}}.mp3" type="audio/mpeg">
  </audio>
  
+ line number : 265
+ {{ tr_rec|get_srt_path|safe }} : for including the subtitle files
```
---

## Audio and Video sync
Calling a function and sending the ID's as the parameters .
```diff
<script>
(function() {
        new syncAudioVideo('video1', 'audio1');
    })();
</script>

+ inside compressinlinejsblock
```
---

## Forums question sync
Calling a function which is sending the **current time** of  the playing video to the function which is responsible  
for changing the css of the question when it matches the raised time .
```diff
window.setInterval(function(){trigger(formatTime(trackedPlayer.currentTime).toString());},1000);
               
$("#text").click(function(e){
  var trackaudio=document.getElementById('audio1');
  var trackedvideo = document.getElementById('video1');
  var currentTime = trackedvideo.currentTime;
  var cur_time = formatTime(currentTime).toString();
  trackaudio.pause();
  trackedvideo.pause();
  $('#video1-play-control').removeClass("avs-playing");
  $('#video1-play-control').addClass("avs-paused"); 
  setForum(cur_time);
});

+ formatTime(currentTime) : converts the time in seconds to the min:sec format.
+ setForum(cur_time) : comparing the cur_time of the video with the raised time of every question if matched then highlighting it.
+ all these scripts inside compressinlinejsblock 
```
---

### Language change option on loaded page
* Modified the context sent to this page from views.py by adding list of langages in which given tutorial is pubished.
* Defining form to change the language.
* Displaying that list through SELECT tag.
```diff
  <form id="myform" action="" method="GET">
    <SELECT id="language" onchange="report(this.value)">
      {% for i in list %}
      <OPTION value="{{ i }}">{{ i }}
      </OPTION>
      {% endfor %}
    </SELECT>
    <input type="submit" value="Change">
  </form>
  
+ inside the block on line number : 242
```
* On selecting any language, changing the page source which contain tutorial language with selected language.
* Setting this new url as FORM ACTION
```diff
  <script type="text/javascript">
    function report(language){
    var array="{{video}}".split('-');
    var data=array.join('%2B');
    $("#myform").attr("action", "http://localhost:8000/watch/{{ concept }}/"+data+"/"+language);
    }
  </script>
  
+ inside compressinlinejsblock
```
* On clicking Change button the page is loading again with the selected language.
---

[AVS-Player](https://github.com/Spoken-tutorial/avs-player)

