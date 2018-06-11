
    /* popcorn.js init fuction to enable a basic synchronization between the 
    audio / video file. */

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

    /* Synchronization at times of buffering or other related network faults.
    Set audio volume and playback speed. */

    // Video.js Player Global Variables
    var trackedPlayer = videojs('st_video');
    var trackedAudio = document.getElementById("audio");
    var trackedAudioFlag = trackedVideoFlag = 0;
    var timesTried = requestedPlay = seekedFlag = 0
    var userPause = false;


    function checkTimeAndPause() {
        // Fixing a bug on Firefox, remove when irrelevent.
        if (trackedAudio.readyState == 4 && trackedAudioFlag == 0) {
            trackedAudio.load();
        }        
        if (trackedPlayer.readyState() == 4 && trackedVideoFlag == 0) {
            trackedPlayer.load();
        }
        // Check sync currenTime
        if (trackedAudio.currentTime - trackedPlayer.currentTime() + 0.5 < 0 || trackedAudio.currentTime - trackedPlayer.currentTime() - 0.5 > 0) {
            // When client changes video from video list on the page, trackedAudio needs to be played from the code manually! 
            if (trackedAudio.paused && !trackedPlayer.paused()) {
                pauseTrackedMedia();
                playTrackedMedia();
                checkBufferedState();
            }
            // Set Audio / Video to same currentTime
            trackedAudio.currentTime = trackedPlayer.currentTime();
            if (trackedAudio.currentTime - trackedPlayer.currentTime() + 0.5 < 0 || trackedAudio.currentTime - trackedPlayer.currentTime() - 0.5 > 0) {
                location.reload();
            }
            // Check If buffered State is as desired
            if (trackedAudioFlag == 0 || trackedVideoFlag == 0) {
                checkBufferedState();
            }
        }    
    }
    setInterval(checkTimeAndPause, 1500);

    function pauseTrackedMedia() {
        var videoPlayPromise = trackedPlayer.play();
        if (videoPlayPromise !== undefined) {
            videoPlayPromise.then(_ => {
                // Can Successfully Pause
                trackedPlayer.pause();
            }).catch(error => {
                console.log(error);
            });
        }
        var audioPlayPromise = trackedAudio.play();
        if (audioPlayPromise !== undefined) {
            audioPlayPromise.then(_ => {
                // Can Successfully Pause
                trackedAudio.pause();
            }).catch(error => {
                console.log(error);
            });
        }
    }
    
    function  playTrackedMedia() {
        var videoPlayPromise = trackedPlayer.play();
        if (videoPlayPromise !== undefined) {
            videoPlayPromise.then(_ => {
                // Can Successfully Play
            }).catch(error => {
                console.log(error);
                pauseTrackedMedia();
                checkBufferedState();
            });
        }

        if (trackedAudio.paused) {
            var audioPlayPromise = trackedAudio.play();
            if (audioPlayPromise !== undefined) {
                audioPlayPromise.then(_ => {
                    // Can Successfully Play
                }).catch(error => {
                    console.log(error);
                    pauseTrackedMedia();
                    checkBufferedState();
                });
            }
        }
    }

    // Code to Invoke checkBufferState()
    var playButton = document.getElementsByClassName("vjs-big-play-button")[0];
    var playControllerButton = document.getElementsByClassName("vjs-play-control")[0];
    var playPlayerController = document.getElementsByClassName("vjs-tech")[0];

    playPlayerController.addEventListener("click", function () {
        userPause = true;
        checkBufferedState();
    });
    playControllerButton.addEventListener("click", function () {
        userPause = true;
        checkBufferedState();
    });
    playButton.addEventListener("click", function () {
        userPause = true;
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
            pauseTrackedMedia();
            if (timesTried < 6) {
                setTimeout(checkBufferedState, 1000);
                return;
            }
            else {
                alert("Bufferign Failed, Download video or refresh to try again.");
                return;
            }
        }
        else if (requestedPlay || seekedFlag) {
            timesTried = 0;
            seekedFlag = 0;
             playTrackedMedia();
        }
    }

    trackedPlayer.on("seeked", function () {
        seekedFlag = 1;
    });

    trackedPlayer.on("play", function () {
        requestedPlay = 0;
        if (trackedAudioFlag) {
            trackedPlayer.removeClass("vjs-waiting");
        }
    });

    trackedPlayer.on("pause", function () {
        requestedPlay = 1;
        if (userPause == false) {
            trackedPlayer.addClass("vjs-waiting");
        }
        userPause = false;
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