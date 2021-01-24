"""
Unit tests for ledcontroller.

"""

# pylint: disable=line-too-long

import time
import unittest

from ledcontroller import LedController, LedControllerPool


class TestDefaultOptions(unittest.TestCase):
    """
    Tests that require creating a new LedController object. For example, tests related to
    constructor options.
    """
    def test_default_constructor(self):
        """ Verify default settings """
        led = LedController("127.0.0.1")
        self.assertEqual(led.gateway_ip, "127.0.0.1")
        self.assertEqual(led.gateway_port, 8899)
        self.assertEqual(led.repeat_commands, 3)
        self.assertEqual(led.pause_between_commands, 0.1)

    def test_changing_port(self):
        """ Validate port parsing """
        led = LedController("127.0.0.1", port=123)
        self.assertEqual(led.gateway_port, 123)
        led = LedController("127.0.0.1", port="123")
        self.assertEqual(led.gateway_port, 123)
        with self.assertRaises(ValueError):
            LedController("127.0.0.1", port=0)

    def test_sleep(self):  # pylint: disable=no-self-use
        """ Verify sleeps between subsequent commands """
        led = LedController("127.0.0.1", pause_between_commands=0.5, repeat_commands=1)
        start_time = time.time()
        led.on()
        self.assertLess(time.time() - start_time, 0.45)  # there is no sleep for a single command
        led.off()  # this command needs to wait almost 0.5 seconds
        self.assertGreater(time.time() - start_time, 0.45)

    def test_changing_pause(self):
        """ Change pause times """
        led = LedController("127.0.0.1", pause_between_commands=0.8)
        self.assertEqual(led.pause_between_commands, 0.8)
        with self.assertRaises(ValueError):
            LedController("127.0.0.1", pause_between_commands=-0.1)

    def test_changing_repeat_commands(self):
        """ Change number of repeated commands """
        led = LedController("127.0.0.1", repeat_commands=0)
        self.assertEqual(led.repeat_commands, 1)
        led = LedController("127.0.0.1", repeat_commands=1)
        self.assertEqual(led.repeat_commands, 1)
        led = LedController("127.0.0.1", repeat_commands=2)
        self.assertEqual(led.repeat_commands, 2)
        with self.assertRaises(ValueError):
            LedController("127.0.0.1", repeat_commands=-1)


class TestRgbwLights(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Common tests for different setups (light combinations). Also default tests (rgbw only).
    """
    def setUp(self):
        self.led = LedController("127.0.0.1", pause_between_commands=0, repeat_commands=0)

    def test_on(self):
        """ Turn on lights """
        self.led.on()
        for group_id in range(5):
            self.led.on(group_id)

    def test_off(self):
        """ Turn off lights """
        self.led.off()
        for group_id in range(5):
            self.led.off(group_id)

    def test_white(self):
        """ Set lights to white """
        self.led.white()
        for group_id in range(5):  # intentionally includes 0-4, as 0 is a special case
            self.led.white(group_id)
        self.led.white(None)

    def test_set_color(self):
        """ Set lights to predefined colors """
        self.led.set_color("white")
        self.led.set_color("red")

    def test_set_color_by_int(self):
        """ Set lights to color (int) """
        self.led.set_color(0)
        self.led.set_color(1)
        self.led.set_color(156)
        self.led.set_color(255)
        with self.assertRaises(AttributeError):
            self.led.set_color(-1)
        with self.assertRaises(AttributeError):
            self.led.set_color(256)

    def test_set_brightness(self):
        """ Set brightness """
        self.assertEqual(self.led.set_brightness(-1), 0, "negative brightness not clamped properly")
        self.assertEqual(self.led.set_brightness(101), 100, ">100 brightness not clamped properly")
        self.assertEqual(self.led.set_brightness(50), 50, "50% outputs != 50%")

    def test_set_brightness_float(self):
        """ Set brightness (float) """
        self.assertEqual(self.led.set_brightness(0.1), 10, "float(0.1) not parsed to 10%")
        self.assertEqual(self.led.set_brightness(1.0), 100, "float(1.0) not parsed to 100%")
        self.assertEqual(self.led.set_brightness(50.0), 50, "float(50.0) not parsed to 50%")

    def test_disco(self):
        """ Enable disco mode """
        self.led.disco()
        for group_id in range(5):
            self.led.disco(group_id)

    def test_disco_faster(self):
        """ Increase disco mode speed """
        self.led.disco_faster()
        for group_id in range(5):
            self.led.disco_faster(group_id)

    def test_disco_slower(self):
        """ Decrease disco mode speed """
        self.led.disco_slower()
        for group_id in range(5):
            self.led.disco_slower(group_id)

    def test_nightmode(self):
        """ Enable nightmode """
        self.led.nightmode()
        for group_id in range(5):
            self.led.nightmode(group_id)

    def test_warmer(self):
        """ Test white light -> warmer """
        self.led.warmer()
        for group_id in range(5):
            self.led.warmer(group_id)

    def test_cooler(self):
        """ Test white light -> cooler """
        self.led.cooler()
        for group_id in range(5):
            self.led.cooler(group_id)

    def test_brightness_up(self):
        """ Increase brightness """
        self.led.brightness_up()
        for group_id in range(5):
            self.led.brightness_up(group_id)

    def test_brightness_down(self):
        """ Decrease brightness """
        self.led.brightness_down()
        for group_id in range(5):
            self.led.brightness_down(group_id)

    def test_batch_run(self):
        """ Batch run multiple commands """
        led = self.led
        led.batch_run((led.set_brightness, 10, 3), (led.set_color, "red"), (led.off, ))

    def test_invalid_group_type(self):
        """ Set invalid group type """
        self.assertRaises(AttributeError, self.led.set_group_type, 1, "asdf")

    def test_invalid_group_number(self):
        """ Set invalid group number """
        self.assertRaises(AttributeError, self.led.on, 5)


class TestWhiteLights(TestRgbwLights):
    """
    Tests for white-only bulbs
    """
    def setUp(self):
        self.led = LedController(
            "127.0.0.1",
            pause_between_commands=0,
            repeat_commands=0,
            group_1="white",
            group_2="white",
            group_3="white",
            group_4="white"
        )


class TestCombinedSetup(TestRgbwLights):
    """
    Tests for combined (both rgbw and white) setups.
    """
    def setUp(self):
        self.led = LedController(
            "127.0.0.1",
            pause_between_commands=0,
            repeat_commands=0,
            group_1="rgbw",
            group_2="white",
            group_3="rgbw",
            group_4="white"
        )


class TestConnectionPool(unittest.TestCase):
    # pylint: disable=missing-docstring
    """
    Tests commands sent using connection pools (multiple gateways)
    """
    def setUp(self):
        self.ledpool = LedControllerPool(["127.0.0.1", "127.0.0.2"])

    def test_set_color_0(self):
        """ Test setting color in controller 0 """
        self.ledpool.execute(0, "set_color", "red", 1)

    def test_set_color_1(self):
        """ Test setting color in controller 1 """
        self.ledpool.execute(1, "set_color", "aqua", 3)

    def test_on(self):
        """ Test turning lights on """
        self.ledpool.execute(0, "on")
