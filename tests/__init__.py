import unittest
from ledcontroller import LedController

class TestLights(unittest.TestCase):
    def get_test_led(self):
        return LedController("127.0.0.1", pause_between_commands=0, repeat_commands=0)

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
        led = self.get_test_led()
        led.on()
        led.on(1)

    def test_off(self):
        led = self.get_test_led()
        led.off()
        led.off(2)

    def test_white(self):
        led = self.get_test_led()
        led.white()
        for a in range(5):
            led.white(a)
        led.white(None)

    def test_set_color(self):
        led = self.get_test_led()
        led.set_color("white")
        led.set_color("red")

    def test_set_brightness(self):
        led = self.get_test_led()
        led.set_brightness(-1)
        led.set_brightness(101)
        led.set_brightness(50)

    def test_disco(self):
        led = self.get_test_led()
        led.disco(1)

    def test_disco_faster(self):
        led = self.get_test_led()
        led.disco_faster(1)

    def test_disco_slower(self):
        led = self.get_test_led()
        led.disco_slower(1)

    def test_invalid_group(self):
        led = self.get_test_led()
        self.assertRaises(AttributeError, led.set_color, "red", 5)

    def test_nightmode(self):
        led = self.get_test_led()
        led.nightmode()
        led.nightmode(1)

if __name__ == '__main__':
    unittest.main()
