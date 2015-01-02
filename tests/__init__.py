import unittest
from ledcontroller import LedController

class TestLights(unittest.TestCase):
    def setUp(self):
        self.led = LedController("127.0.0.1", pause_between_commands=0, repeat_commands=0)

    def test_default_constructor(self):
        led = LedController("127.0.0.1")
        self.assertEqual(led.ip, "127.0.0.1")
        self.assertEqual(led.port, 8899)
        self.assertEqual(led.repeat_commands, 3)
        self.assertEqual(led.pause_between_commands, 0.1)

    def test_changing_port(self):
        led = LedController("127.0.0.1", port=123)
        self.assertEqual(led.port, 123)
        led = LedController("127.0.0.1", port="123")
        self.assertEqual(led.port, 123)

    def test_sleep(self):
        led = LedController("127.0.0.1")
        led.on()
        led.off()

    def test_changing_pause(self):
        led = LedController("127.0.0.1", pause_between_commands=0.8)
        self.assertEqual(led.pause_between_commands, 0.8)

    def test_changing_repeat_commands(self):
        led = LedController("127.0.0.1", repeat_commands=0)
        self.assertEqual(led.repeat_commands, 1)

    def test_on(self):
        self.led.on()
        self.led.on(1)

    def test_off(self):
        self.led.off()
        self.led.off(2)

    def test_white(self):
        self.led.white()
        for a in range(5):
            self.led.white(a)
        self.led.white(None)

    def test_set_color(self):
        self.led.set_color("white")
        self.led.set_color("red")

    def test_set_brightness(self):
        self.assertEquals(self.led.set_brightness(-1), 0)
        self.assertEquals(self.led.set_brightness(101), 100)
        self.assertEquals(self.led.set_brightness(50), 50)

    def test_set_brightness_float(self):
        self.assertEquals(self.led.set_brightness(0.1), 10)
        self.assertEquals(self.led.set_brightness(1.0), 100)
        self.assertEquals(self.led.set_brightness(50.0), 50)

    def test_disco(self):
        self.led.disco(1)
        self.led.disco()

    def test_disco_faster(self):
        self.led.disco_faster(1)
        self.led.disco_faster()

    def test_disco_slower(self):
        self.led.disco_slower(1)
        self.led.disco_slower()

    def test_invalid_group(self):
        self.assertRaises(AttributeError, self.led.set_color, "red", 5)

    def test_nightmode(self):
        self.led.nightmode()
        self.led.nightmode(1)

if __name__ == '__main__':
    unittest.main()
