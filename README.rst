Wi-Fi LED controller
====================

.. image:: https://travis-ci.org/ojarva/python-ledcontroller.svg?branch=master
    :target: https://travis-ci.org/ojarva/python-ledcontroller

.. image:: https://pypip.in/v/ledcontroller/badge.png
    :target: https://pypi.python.org/pypi/ledcontroller

Controller for LimitlessLED RGBW lights (should be compatible with easybulb/milight as well).

Before using this code, you need to configure your gateway to connect to wifi. After that, configure light groups to the gateway. Configuring remotes has nothing to do with configuring the gateway.

See `github repository <https://github.com/ojarva/python-ledcontroller>`_ for more information.

The code is based on the documentation available at `limitlessled.com/dev/ <http://www.limitlessled.com/dev/>`_

Installation
------------

::

  pip install ledcontroller

Usage
-----

::

  import ledcontroller
  led = ledcontroller.LedController("192.168.1.6")
  led.off() # Switches all groups off
  led.set_color("red", 1) # Switches group 1 on and changes color to red.
  led.white(2) # Group 2 on and color to white.
  led.set_brightness(50, 2) # Group 2 on and brightness to 50%.
  led.disco(3) # Group 3 on and enable disco mode.
  led.disco_faster(3) # Group 3 on and adjust disco mode speed.
  led.on(4) # Switch group 4 on. Bulb automatically restores previous color and brightness.

Using both white and RGBW bulbs:

::

  import ledcontroller
  # By default, all groups are RGBW bulbs.
  led = ledcontroller.LedController("192.168.1.6", group_1="white", group_4="white")
  led.set_group_type(1, "white") # This is same as using constructor keyword group_1.
  led.on()
  led.white(2) # Switches RGBW group on and changes color to white.
  led.white(1) # Turns white group on.
  led.warmer() # Adjusts all white groups to warmer color. Switches all groups on.
  led.cooler(1) # Adjusts group 1 white bulbs to cooler color.
  led.brightness_up() # Adjusts white group brightness up. Does not affect RGBW lights.
  led.brightness_up(2) # Does nothing to RGBW bulbs.
  led.brightness_up(4) # Adjusts group 4 brightness.
  led.set_brightness(50) # Adjusts all RGBW bulbs to 50%. Does not affect white lights.

Controller pools:

When using multiple controllers, it is important to keep same 100ms pause between each command. Use LedControllerPool class to automate this.

::

  import ledcontroller
  ledpool = ledcontroller.LedControllerPool(["192.168.1.6", "192.168.1.7"])
  ledpool.execute(0, "on")
  ledpool.execute(1, "disco", 3)
  ledpool.execute(0, "set_color", "red", 1)

Notes
-----

- There is automatic 100ms pause between each command. Almost every action requires sending more than one command, thus requiring several hundred milliseconds. You can change this with keyword argument "pause_between_commands". However, decreasing the delay will cause some commands to fail.
- As the gateway seems to be rather unreliable, all commands are sent multiple times (three by default). If you want to change this, use "LedController(ip, repeat_commands=n)" to create new lightcontroller instance. It is not possible to retrieve any status information from light bulbs.
- If for some reason you need to change gateway port, pass port=n argument to constructor.
- Run testsuite with "python setup.py test". Tests only run the code without checking whether proper commands were sent.
- RGBW/white bulb commands differ a bit. Obviously, it is not possible to change color for white bulbs. For white bulbs, there is no absolute brightness settings. Similarly, only white bulbs allow adjusting color temperature (with .cooler and .warmer). There is 10 steps for white bulb brightness and color temperature.
- Brightness settings are stored by bulbs. Brightness is saved separately for both white and RGB modes. Furthermore, bulbs store the last color. Sending .on() restores previous brightness and color.

Stores and brands
-----------------

- I bought my bulbs, remotes and gateway from `LimitlessLED <http://www.limitlessled.com/>`_. Unfortunately, they have really expensive shipping ($50 to Finland). Furthermore, when ordering to Finland, taxes and customs were about 30% in top of original price.
- `milight.com <http://www.milight.com/>`_ and `easybulb.com <http://easybulb.com/en/>`_ sell same products with two different brands. These are more expensive than LimitlessLED, but ship from UK.
- At least some products from s'luce iLight are exactly the same with different branding.
- Beware that at least milight.com and easybulb.com sell older version of the wifi gateway (v3, vs. v4 from LimitlessLED). v3 does not support nightmode, and seems to be less reliable than v4.
- Try `aliexpress.com <http://aliexpress.com/>`_ with search "milight". Beware of older versions (RGB bulbs) and non-remote-controlled bulbs sold with same brand.
