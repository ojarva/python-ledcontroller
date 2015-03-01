"""
Library for controlling limitless/milight/easybulb RGBW/white leds bulbs.

Commands for white and RGBW bulbs are implemented. Older RGB lights are not supported yet.

Before using this library, you need to use smartphone/tablet app to configure
light groups to the gateway. Configuring remotes does nothing to configure the gateway.

See https://github.com/ojarva/python-ledcontroller for more information.

Based on the documentation available at http://www.limitlessled.com/dev/ .
"""

import socket
import struct
import time

__all__ = ["LedController", "LedControllerPool"]

class LedControllerPool(object):
    def __init__(self, gateway_ips, **kwargs):
        self.controllers = []
        for ip in gateway_ips:
            self.controllers.append(LedController(ip, **kwargs))
        self.last_command_at = 0

    def execute(self, controller_id, command, *args, **kwargs):
        controller_instance = self.controllers[controller_id]
        controller_instance.last_command_at = self.last_command_at
        ret_val = getattr(controller_instance, command)(*args, **kwargs)
        self.last_command_at = controller_instance.last_command_at
        return ret_val

class LedController(object):
    """
    Main class for controlling limitless/milight/easybulb lights.

    Usage:
    # All keyword arguments are optional.
    led = LedController(ip, port=8899, repeat_commands=3, pause_between_commands=0.1)
    led.on()
    led.off(1)
    led.disco(4)
    led.nightmode(3)
    led.set_color("red", 2)
    led.set_brightness(50, 2)
    """

    WHITE_COMMANDS = {
     "all_on": (b"\x35",),
     "all_off": (b"\x39",),
     "all_full": (b"\xb5",),
     "all_nightmode": (b"\xb9",),
     "warmer": (b"\x3e",),
     "cooler": (b"\x3f",),
     "brightness_up": (b"\x3c",),
     "brightness_down": (b"\x34",),
    }

    WHITE_GROUP_X_ON = [(b"\x38",), (b"\x3d",), (b"\x37",), (b"\x32",)]
    WHITE_GROUP_X_OFF = [(b"\x3b",), (b"\x33",), (b"\x3a",), (b"\x36",)]
    WHITE_GROUP_X_FULL = [(b"\xb8",), (b"\xbd",), (b"\xb7",), (b"\xb2",)]
    WHITE_GROUP_X_NIGHTMODE = [(b"\xbb",), (b"\xb3",), (b"\xba",), (b"\xb6",)]


    RGBW_GROUP_X_ON = [(b"\x45",), (b"\x47",), (b"\x49",), (b"\x4b",)]
    RGBW_GROUP_X_OFF = [(b"\x46",), (b"\x48",), (b"\x4a",), (b"\x4c",)]
    RGBW_GROUP_X_TO_WHITE = [(b"\xc5",), (b"\xc7",), (b"\xc9",), (b"\xcb",)]
    RGBW_GROUP_X_NIGHTMODE = [(b"\xc6",), (b"\xc8",), (b"\xca",), (b"\xcc",)]
    RGBW_COMMANDS = {
     "all_on": (b"\x42",),
     "all_off": (b"\x41",),
     "all_white": (b"\xc2",),
     "disco": (b"\x4d",),
     "disco_faster": (b"\x44",),
     "disco_slower": (b"\x43",),
     "all_nightmode": (b"\xc1",),
     "color_to_violet": (b"\x40", b"\x00"),
     "color_to_royal_blue": (b"\x40", b"\x10"),
     "color_to_baby_blue": (b"\x40", b"\x20"),
     "color_to_aqua": (b"\x40", b"\x30"),
     "color_to_royal_mint": (b"\x40", b"\x40"),
     "color_to_seafoam_green": (b"\x40", b"\x50"),
     "color_to_green": (b"\x40", b"\x60"),
     "color_to_lime_green": (b"\x40", b"\x70"),
     "color_to_yellow": (b"\x40", b"\x80"),
     "color_to_yellow_orange": (b"\x40", b"\x90"),
     "color_to_orange": (b"\x40", b"\xa0"),
     "color_to_red": (b"\x40", b"\xb0"),
     "color_to_pink": (b"\x40", b"\xc0"),
     "color_to_fusia": (b"\x40", b"\xd0"),
     "color_to_lilac": (b"\x40", b"\xe0"),
     "color_to_lavendar": (b"\x40", b"\xf0"),
    }

    def __init__(self, gateway_ip, **kwargs):
        """ Optional keyword arguments:
            - repeat_commands (default 3): how many times safe commands are repeated to ensure successful execution.
            - port (default 8899): UDP port on wifi gateway. Port is 50000 for gw v1 and v2.
            - pause_between_commands (default 0.1 (in seconds)): how long pause there should be between sending commands to the gateway.
            - group_1, group_2, ...: set bulb type for group. Currently either rgbw (default) and "white" are supported. See also .set_group_type method.
            """
        self.group = {}
        self.has_white = False
        self.has_rgbw = False
        for group in range(1, 5):
            self.set_group_type(group, kwargs.get("group_%s" % group, "rgbw"))
        self.gateway_ip = gateway_ip
        self.gateway_port = int(kwargs.get("port", 8899))
        self.last_command_at = 0
        self.repeat_commands = int(kwargs.get("repeat_commands", 3))
        if self.repeat_commands == 0:
            self.repeat_commands = 1
        self.pause_between_commands = float(kwargs.get("pause_between_commands", 0.1))

    def get_group_type(self, group):
        """ Gets bulb type for specified group.

        Group must be int between 1 and 4.
        """
        return self.group[group]

    def set_group_type(self, group, bulb_type):
        """ Sets bulb type for specified group.

        Group must be int between 1 and 4.

        Type must be "rgbw" or "white".

        Alternatively, use constructor keywords group_1, group_2 etc. to set bulb types.
        """
        if bulb_type not in ("rgbw", "white"):
            raise AttributeError("Bulb type must be either rgbw or white")

        self.group[group] = bulb_type
        if "white" in self.group.values():
            self.has_white = True
        else:
            self.has_white = False

        if "rgbw" in self.group.values():
            self.has_rgbw = True
        else:
            self.has_rgbw = False

    def _send_command(self, input_command):
        """ You shouldn't use this method directly.

            Sends a single command. If previous command was sent
            recently, sleep for 100ms (configurable with pause_between_commands
            constructor keyword). """
        if input_command is None:
            return
        time_since_last_command = time.time() - self.last_command_at
        if time_since_last_command < self.pause_between_commands:
            # Lights require 100ms pause between commands to function at least almost reliably.
            time.sleep(self.pause_between_commands - time_since_last_command)
        self.last_command_at = time.time()
        command = b""
        for item in input_command:
            command = command + item
        if len(command) == 1:
            command = command + b"\x00"
        if len(command) == 2:
            command = command + b"\x55"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command, (self.gateway_ip, self.gateway_port))
        sock.close()
        return command

    def _send_to_group(self, group, **kwargs):
        """ You shouldn't use this method directly.

        Sends a single command to specific group.

        Handles automatically sending command to white or rgbw group.
        """
        retries = kwargs.get("retries", self.repeat_commands)
        for _ in range(retries):
            if kwargs.get("send_on", True):
                self.on(group)
            if group is None or group == 0:
                if self.has_white:
                    self._send_command(self.WHITE_COMMANDS.get(kwargs["command"]))
                if self.has_rgbw:
                    self._send_command(self.RGBW_COMMANDS.get(kwargs["command"]))
            else:
                if group < 1 or group > 4:
                    raise AttributeError("Group must be between 1 and 4 (was %s)" % group)
                if kwargs.get("per_group"):
                    self._send_command(kwargs.get("%s_cmd" % self.get_group_type(group), [None, None, None, None])[group-1])
                else:
                    if self.get_group_type(group) == "white":
                        cmd_tmp = self.WHITE_COMMANDS
                    elif self.get_group_type(group) == "rgbw":
                        cmd_tmp = self.RGBW_COMMANDS
                    self._send_command(cmd_tmp.get(kwargs["command"]))

    def on(self, group=None):
        """ Switches lights on. If group (1-4) is not specified,
            all four groups will be switched on. """
        if group is None or group == 0:
            self._send_to_group(group, send_on=False, command="all_on")
            return
        self._send_to_group(group, per_group=True, white_cmd=self.WHITE_GROUP_X_ON, rgbw_cmd=self.RGBW_GROUP_X_ON, send_on=False)

    def off(self, group=None):
        """ Switches lights off. If group (1-4) is not specified,
            all four groups will be switched off. """
        if group is None or group == 0:
            self._send_to_group(group, send_on=False, command="all_off")
            return
        self._send_to_group(group, per_group=True, send_on=False, rgbw_cmd=self.RGBW_GROUP_X_OFF, white_cmd=self.WHITE_GROUP_X_OFF)

    def white(self, group=None):
        """ Switches lights on and changes color to white.
            If group (1-4) is not specified, all four groups
            will be switched on and to white. """
        if group is None or group == 0:
            self._send_to_group(group, command="all_white")
            return
        self._send_to_group(group, per_group=True, rgbw_cmd=self.RGBW_GROUP_X_TO_WHITE)

    def set_color(self, color, group=None):
        """ Switches lights on and changes color. Available colors:

             - violet
             - royal_blue
             - baby_blue
             - aqua
             - royal_mint
             - seafoam_green
             - green
             - lime_green
             - yellow
             - yellow_orange
             - orange
             - red
             - pink
             - fusia
             - lilac
             - lavendar

            If group (1-4) is not specified, all four groups
            will be switched on and to specified color."""
        if color == "white": # hack, as commands for setting color to white differ from other colors.
            self.white(group)
        else:
            self._send_to_group(group, command="color_to_"+color)
        return color

    def brightness_up(self, group=None):
        """ Adjusts white bulb brightness up.

        Calling this method for RGBW lights won't
        have any effect on the brightness."""
        self._send_to_group(group, command="brightness_down")

    def brightness_down(self, group=None):
        """ Adjusts white bulb brightness down.

        Calling this method for RGBW lights won't
        have any effect on the brightness."""
        self._send_to_group(group, command="brightness_up")

    def cooler(self, group=None):
        """ Adjusts white bulb to cooler color temperature.

        Calling this method for RGBW lights won't
        have any effect. """
        self._send_to_group(group, command="cooler")

    def warmer(self, group=None):
        """ Adjusts white bulb to warmer color temperature.

        Calling this method for RGBW lights won't
        have any effect. """
        self._send_to_group(group, command="warmer")

    @classmethod
    def get_brightness_level(cls, percent):
        """ Gets internal brightness level.

            percent should be integer from 0 to 100.
            Return value is 2 (minimum) - 27 (maximum)
        """
        # Clamp to appropriate range.
        percent = min(100, max(0, percent))

        # Map 0-100 to 2-27
        value = int(2 + ((float(percent) / 100) * 25))
        return percent, value

    def set_brightness(self, percent, group=None):
        """ Sets brightness.

            Percent is int between 0 (minimum brightness) and 100 (maximum brightness), or
            float between 0 (minimum brightness) and 1.0 (maximum brightness).

            See also .nightmode().

            If group (1-4) is not specified, brightness of all four groups will be adjusted.
            """
        # If input is float, assume it is percent value from 0 to 1.
        if isinstance(percent, float):
            if percent > 1:
                percent = int(percent)
            else:
                percent = int(percent * 100)
        percent, value = self.get_brightness_level(percent)
        self.on(group)
        self._send_command((b"\x4e", struct.pack("B", value)))
        return percent

    def disco(self, group=None):
        """ Starts disco mode. The command is executed only once, as multiple commands would cycle
            disco modes rapidly. There is no way to automatically detect whether transmitting the command
            succeeded or not.

        Consecutive calls cycle disco modes:
            1. Static white color.
            2. White color smooth change.
            3. All colors smooth change.
            4. Red / Green / Blue colors smooth change.
            5. Seven Colors
            6. Three Colors
            7. Red / Green
            8. Red / Blue
            9. Blue / Green
            10. White Blink
            11. White Strobe
            12. Red Blink
            13. Red Strobe
            14. Green Blinks
            15. Green Strobe
            16. Blue Blinks
            17. Blue Strobe
            18. Yellow Blinks
            19. Yellow Strobe
            20. All of the above in an endless cycle.

            (Above list is copied from http://www.limitlessled.com/faqs/how-is-limitlessled-better-than-greenwave-led/)."""
        self._send_to_group(group, command="disco", retries=1)

    def disco_faster(self, group=None):
        """ Adjusts up the speed of disco mode (if enabled; does not start disco mode). """
        self._send_to_group(group, command="disco_faster", retries=1)

    def disco_slower(self, group=None):
        """ Adjusts down the speed of disco mode (if enabled; does not start disco mode). """
        self._send_to_group(group, command="disco_slower", retries=1)

    def nightmode(self, group=None):
        """ Enables nightmode (very dim white light).

            The command is sent only once, as multiple commands would blink lights rapidly.
            There is no way to automatically detect whether transmitting the command succeeded or not.

            This does not work with wifi gateway v3.

            Contrary to limitlessled documentation, this works with RGBW bulbs.
            """
        self.off(group)
        if group is None or group == 0:
            if self.has_rgbw:
                self._send_command(self.RGBW_COMMANDS["all_nightmode"])
            if self.has_white:
                self._send_command(self.WHITE_COMMANDS["all_nightmode"])
        else:
            self._send_to_group(group, per_group=True, rgbw_cmd=self.RGBW_GROUP_X_NIGHTMODE, white_cmd=self.WHITE_GROUP_X_NIGHTMODE, send_on=False, retries=1)

    def batch_run(self, *commands):
        """ Run batch of commands in sequence.

            Input is positional arguments with (function pointer, *args) tuples.

            This method is useful for executing commands to multiple groups with retries,
            without having too long delays. For example,

            - Set group 1 to red and brightness to 10%
            - Set group 2 to red and brightness to 10%
            - Set group 3 to white and brightness to 100%
            - Turn off group 4

            With three repeats, running these consecutively takes approximately 100ms * 13 commands * 3 times = 3.9 seconds.

            With batch_run, execution takes same time, but first loop - each command is sent once to every group -
            is finished within 1.3 seconds. After that, each command is repeated two times. Most of the time, this ensures
            slightly faster changes for each group.

            Usage:

            led.batch_run((led.set_color, "red", 1), (led.set_brightness, 10, 1), (led.set_color, "white", 3), ...)
        """
        original_retries = self.repeat_commands
        self.repeat_commands = 1
        for _ in range(original_retries):
            for command in commands:
                cmd = command[0]
                args = command[1:]
                cmd(*args)
        self.repeat_commands = original_retries
