# fm-transfer
### A graphical front-end for gg-transfer and quiet-transfer

---

`fm-transfer` is a GUI that allows you to send and receive files through a transceiver.
It is designed to directly control the push-to-talk of devices equipped with a Kenwood connector
(like many Baofeng, Quansheng etc.).

Transmission and reception are done using two libraries, ggwave and quiet: the former implements FSK modulation 
and reaches a peak of about 80 bytes per second, the latter implements a large series of modulation algorithms,
including GMSK and QAM.

It is possible to transfer ~240 bytes/s in very good conditions.

Under development!

https://github.com/matteotenca/fm-transfer
