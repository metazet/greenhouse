This is a RaspberryPI based script for control your greenhouse, I developed it for control temperature and light for my in-house mini greenhouse. You can modify it for whatever you want to grow just changing temperature threshold (when it should stop heating) and light day.

What you need: indicators that each sensor works (2 light-emitted diode), one temperature sensor (I used DS18B20), main switcher (not required) with one light-emitted diode, one chain of light (I used LED lamps) and one chain of heating. 

Requirements
---
Of course you should run it under raspberry pi with installed RPi.GPIO and pigpiod daemon (for temperature sensor).

Developed with Py3, but should also work with Py2.

See requirements.txt for another libraries required.

How to use
---

Just clone the repo and run

`python pepper.py`

It is unfinished and less tested yet, see for further changes