# Creation module
---

### video_upload process

---

##### Packages used

* ffmpeg
* SoX

---

##### Algorithm

* .mov file converted to .wav file to check for the noise and loudness parameter.  
```
  ffmpeg -y -i <video_file.mov> -ab 160k -ac 2 -ar 44100 -vn <audio_file.wav>
```
* .wav file is then processed through "numpy" & "scipy" library for calculating the  
signaltonoise ratio and mean amplitude as amplitude is the measure of loudness.  
```
  samplerate, data =wavfile.read("audio_file.wav")
  samplerate=numpy.sum(data,axis=1)
  norm=samplerate/ (max(numpy.amax(samplerate), -1*numpy.amin(samplerate)))
  ratio=signaltonoise(norm,axis=None)

  signal_to_noise_ratio = (ratio+2)/(4)

  sampFreq, snd = wavfile.read("audio_file.wav")
  snd=snd / (2.**15)
  s1=snd[:,0]

  mean_amplitude = numpy.sqrt(numpy.mean(numpy.square(s1)))
```
* If signal_to_noise_ratio__lt = 0.5 & mean_amplitude__lt = 0.2
* Then calling shell script to remove the noise from the wav file by selecting  
the noise profile b/w 0 - 1.0 sec and then removing the noise.  
```
  #!/bin/bash

  # $1 is file name
  # $2 is the signal_to_noise_ratio
  # Please install 'libav-tools' for Ubuntu 14.04 onwards
  # Usage example
  # $ bash noNoise.sh noisyVideo.mp4 noise-reduction-factor

  # noise-reduction-factor: 0 means no reduction, 1 means 
  # maximum damping of noise (recommended is 0.2 to 0.4)

  sox $1 -n trim 0 1.0  noiseprof myprofile
  # Removing noise using noise profile
  sox $1 /tmp/noisefree.wav noisered myprofile $2
```
* After removal of noise the .wav file is converted into .mp3 file.
```
  ffmpeg -y -i /tmp/noisefree.wav <output_file.mp3>
```
* Then .mov into silent .mov file
```
  ffmpeg -y -i <input_file.mov> -an -codec copy <output_file.mov>
```	
* Then silent .mov file to .webm file.
```
  ffmpeg -y -i <output_file.mov> -vcodec libvpx -cpu-used -5 -deadline realtime <output_file.webm>
```
* Finally .webm and .mp3 files are stored under their respective folder as :
  * Media/videos/foss/foss_category/<tutorial_name>.webm
  * Media/videos/foss/foss_category/<tutorial_name-language>.mp3
---

[ffmpeg documantation](http://ffmpeg.org/ffmpeg.html)

