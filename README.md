### ALSA monitor source (as taken straight from arch wiki)
To be able to record from a monitor source (a.k.a. "What-U-Hear", "Stereo Mix"), use `pactl list` to find out the name of the source in PulseAudio (e.g. `alsa_output.pci-0000_00_1b.0.analog-stereo.monitor`). Then add lines like the following to `ic|/etc/asound.conf` or `ic|~/.asoundrc`:
```
 pcm.pulse_monitor {
   type pulse
   device alsa_output.pci-0000_00_1b.0.analog-stereo.monitor
 }
 
 ctl.pulse_monitor {
   type pulse
   device alsa_output.pci-0000_00_1b.0.analog-stereo.monitor
 }
```
Now you can select `pulse_monitor` as a recording source.

[sauce](https://wiki.archlinux.org/index.php?title=PulseAudio/)