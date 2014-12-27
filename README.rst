Wi-Fi LED controller
====================

Controller for LimitlessLED RGBW lights (should be compatible with easybulb/milight as well).

Installation:

::

  pip install ledcontroller

Usage:

::

  import ledcontroller
  led = ledcontroller.LedController("192.168.1.6")
  led.on()
  led.set_color("red", 1)
  led.white(2)
  led.set_brightness(50, 2)
  led.disco(3)
  led.disco_faster(3)
  led.off(4)
