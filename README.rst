Wi-Fi LED controller
====================

.. image:: https://travis-ci.org/ojarva/python-ledcontroller.svg?branch=master
    :target: https://travis-ci.org/ojarva/python-ledcontroller

Controller for LimitlessLED RGBW lights (should be compatible with easybulb/milight as well).

Before using this, you need to use smartphone/tablet app to configure light groups to the gateway. Configuring remotes has nothing to do with configuring the gateway. You can not mix white lights and RGBW lights to same group.

See `github repository <https://github.com/ojarva/python-ledcontroller>`_ for more information.

The code is based on the documentation available at `limitlessled.com <http://www.limitlessled.com/dev/>`_

Installation
------------

::

  pip install ledcontroller

Usage
-----

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

Notes
-----

- There is automatic 100ms pause between each command. Almost every action requires sending more than one command, thus requiring several hundred milliseconds. You can change this with keyword argument "pause_between_commands". However, decreasing the delay will cause some commands to fail.
- As the gateway seems to be rather unreliable, all commands are sent multiple times (three by default). If you want to change this, use "LedController(ip, repeat_commands=n)" to create new lightcontroller object.
- If for some reason you need to change gateway port, use keyword port= to change it.
- Run testsuite with "python setup.py test". Tests only run the code without checking whether proper commands were sent.
