
    init_popcorn("#st_video", "#audio");
    function init_popcorn(VIDEO, AUDIO) {
        var medias = {
            video: Popcorn(VIDEO),
            audio: Popcorn(AUDIO)
        },
            loadCount = 0,
            events = "play pause timeupdate seeking".split(/\s+/g);

        // iterate both media sources
        Popcorn.forEach(medias, function (media, type) {

            // when each is ready... 
            media.on("canplayall", function () {

                // trigger a custom"sync" event
                this.emit("sync");

                // Listen for the custom sync event...    
            }).on("sync", function () {

                // Once both items are loaded, sync events
                if (++loadCount == 2) {
                    // Uncomment this line to silence the audio
                    //medias.audio.mute();

                    // Iterate all events and trigger them on the audio 
                    // whenever they occur on the video
                    events.forEach(function (event) {

                        medias.video.on(event, function () {

                            // Avoid overkill events, trigger timeupdate manually
                            if (event === "timeupdate") {

                                if (!this.media.paused) {
                                    return;
                                }
                                medias.audio.emit("timeupdate");
                                return;
                            }

                            if (event === "seeking") {
                                medias.audio.currentTime(this.currentTime());
                            }

                            if (event === "play" || event === "pause") {
                                medias.audio[event]();
                            }
                        });
                    });
                }
            });
        });
    }


    // Video.js Player Global Variables
    var trackedPlayer = videojs('st_video');
    var trackedAudio = document.getElementById("audio");
    var trackedAudioFlag = trackedVideoFlag = 0;
    var timesTried = 0;
    var requestedPlay = 0;
    var seekedFlag = 0;

    // Fixing a bug on Firefox, remove when irrelevent.
    function checkLoadAndPlay() {
        if (trackedAudio.readyState == 4 && trackedAudioFlag == 0) {
            trackedAudio.load();
        }        
        
        if (trackedPlayer.readyState() == 4 && trackedVideoFlag == 0) {
            trackedPlayer.load();
        }
    }
    setTimeout(checkLoadAndPlay, 1500);
    
    // Check sync currenTime
    function checkTimeAndPause() {
        if (trackedAudio.currentTime - trackedPlayer.currentTime() + 0.5 < 0 || trackedAudio.currentTime - trackedPlayer.currentTime() - 0.5 > 0) {
            // When client changes video from video list on the page, trackedAudio needs to be played from the code manually! 
            if (trackedAudio.paused && !trackedPlayer.paused()) {
                trackedAudio.play()
            }
            // Set Audio / Video to same currentTime
            trackedAudio.currentTime = trackedPlayer.currentTime();
            // Check If buffered State is as desired
            if (trackedAudioFlag == 0 || trackedVideoFlag == 0) {
                checkBufferedState();
            }
        }    
    }
    setInterval(checkTimeAndPause, 5000);

    function checkMediaAndPause() {
        if (trackedPlayer.paused() == 0) {
            var videoPlayPromise = trackedPlayer.play();
            if (videoPlayPromise !== undefined) {
                videoPlayPromise.then(_ => {
                    trackedPlayer.addClass("vjs-waiting");
                    trackedPlayer.pause();
                })
            }
        }
        if (trackedAudio.paused == 0) {
            var audioPlayPromise = trackedAudio.play();
            if (audioPlayPromise !== undefined) {
                audioPlayPromise.then(_ => {
                    trackedPlayer.addClass("vjs-waiting");
                    trackedAudio.pause();
                })
            }
        }
    }

    function checkMediaAndPlay() {
        var videoPlayPromise = trackedPlayer.play();
        if (videoPlayPromise !== undefined) {
            videoPlayPromise.then(_ => {
                if (trackedPlayer.paused())
                    trackedPlayer.play();
                if (!trackedAudio.paused)
                    trackedPlayer.removeClass("vjs-waiting");
            })
        }

        if (trackedAudio.paused) {
            var audioPlayPromise = trackedAudio.play();
            if (audioPlayPromise !== undefined) {
                audioPlayPromise.then(_ => {
                    trackedPlayer.removeClass("vjs-waiting");
                    trackedAudio.play();
                })
            }
        }
    }

    // Code to Invoke checkBufferState()
    var playButton = document.getElementsByClassName("vjs-big-play-button")[0];
    var playControllerButton = document.getElementsByClassName("vjs-play-control")[0];
    var playPlayerController = document.getElementsByClassName("vjs-tech")[0];

    playPlayerController.addEventListener("click", function () {
        checkBufferedState();
    });
    playControllerButton.addEventListener("click", function () {
        checkBufferedState();
    });
    playButton.addEventListener("click", function () {
        checkBufferedState();
    });

    // Code to check if playable
    trackedAudio.oncanplaythrough = function () {
        trackedAudioFlag = 1;
    };
    trackedPlayer.on("canplaythrough", function () {
        trackedVideoFlag = 1;
    });
    trackedPlayer.on("waiting", function () {
        trackedVideoFlag = 0;
        checkBufferedState();
    });

    trackedAudio.onwaiting = function () {
        trackedAudioFlag = 0;
        checkBufferedState();
    };

    // Check if audio or video is buffering, if buffering keep the other one paused, else, play them when play is requested.
    function checkBufferedState() {
        if (trackedAudioFlag == 0 || trackedVideoFlag == 0) {
            checkMediaAndPause();
            if (timesTried < 6) {
                setTimeout(checkBufferedState, 5000);
                return;
            }
            else {
                alert("Buffered Failed, Download course or refresh to try again.");
                return;
            }
        }
        else if (requestedPlay || seekedFlag) {
            timesTried = 0;
            seekedFlag = 0;
            checkMediaAndPlay();
        }
    }

    trackedPlayer.on("seeked", function () {
        seekedFlag = 1;
    });

    trackedPlayer.on("play", function () {
        requestedPlay = 0;
    });

    trackedPlayer.on("pause", function () {
        requestedPlay = 1;
    });

    // Set Volume 
    trackedPlayer.on("volumechange", function () {
        trackedAudio.volume = trackedPlayer.volume();
        if (trackedPlayer.muted())
            trackedAudio.muted = true;
        else
            trackedAudio.muted = false;
    });
    // Set Playback Rate
    trackedPlayer.on("ratechange", function () {
        trackedAudio.playbackRate = trackedPlayer.playbackRate();
    });