import unittest
from ledcontroller import LedController

class TestRgbwLights(unittest.TestCase):
    def setUp(self):
        self.led = LedController("127.0.0.1", pause_between_commands=0, repeat_commands=0)

    def test_default_constructor(self):
        led = LedController("127.0.0.1")
        self.assertEqual(led.gateway_ip, "127.0.0.1")
        self.assertEqual(led.gateway_port, 8899)
        self.assertEqual(led.repeat_commands, 3)
        self.assertEqual(led.pause_between_commands, 0.1)

    def test_changing_port(self):
        led = LedController("127.0.0.1", port=123)
        self.assertEqual(led.gateway_port, 123)
        led = LedController("127.0.0.1", port="123")
        self.assertEqual(led.gateway_port, 123)

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
        self.assertEquals(self.led.set_brightness(-1), 0, "negative brightness not clamped properly")
        self.assertEquals(self.led.set_brightness(101), 100, ">100 brightness not clamped properly")
        self.assertEquals(self.led.set_brightness(50), 50, "50% outputs != 50%")

    def test_set_brightness_float(self):
        self.assertEquals(self.led.set_brightness(0.1), 10, "float(0.1) not parsed to 10%")
        self.assertEquals(self.led.set_brightness(1.0), 100, "float(1.0) not parsed to 100%")
        self.assertEquals(self.led.set_brightness(50.0), 50, "float(50.0) not parsed to 50%")

    def test_disco(self):
        self.led.disco(1)
        self.led.disco()

    def test_disco_faster(self):
        self.led.disco_faster(1)
        self.led.disco_faster()

    def test_disco_slower(self):
        self.led.disco_slower(1)
        self.led.disco_slower()

    def test_nightmode(self):
        self.led.nightmode()
        self.led.nightmode(1)

    def test_warmer(self):
        self.led.warmer()
        self.led.warmer(1)

    def test_cooler(self):
        self.led.cooler()
        self.led.cooler(4)

    def test_brightness_up(self):
        self.led.brightness_up()
        self.led.brightness_up(4)

    def test_brightness_down(self):
        self.led.brightness_down()
        self.led.brightness_down(4)

    def test_batch_run(self):
        led = self.led
        led.batch_run((led.set_brightness, 10, 3), (led.set_color, "red"), (led.off,))

class TestWhiteLights(TestRgbwLights):
    def setUp(self):
        self.led = LedController("127.0.0.1", pause_between_commands=0, repeat_commands=0, group_1="white", group_2="white", group_3="white", group_4="white")

class TestCombinedSetup(TestRgbwLights):
    def setUp(self):
        self.led = LedController("127.0.0.1", pause_between_commands=0, repeat_commands=0, group_1="rgbw", group_2="white", group_3="rgbw", group_4="white")



if __name__ == '__main__':
    unittest.main()
