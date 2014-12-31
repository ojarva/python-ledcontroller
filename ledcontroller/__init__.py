"""
Library for controlling limitless/milight/easybulb RGBW leds.

Currently only RGBW commandset is implemented. Before using this, you need to use
smartphone/tablet app to configure light groups to the gateway. Configuring remotes
does not enable same groups on the gateway.

See https://github.com/ojarva/python-ledcontroller for more information.

Based on the documentation available at http://www.limitlessled.com/dev/ .
"""

import socket
import time

__all__ = ["LedController"]

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
    GROUP_ON =  [(b"\x45",), (b"\x47",), (b"\x49",), (b"\x4b",)]
    GROUP_OFF = [(b"\x46",), (b"\x48",), (b"\x4a",), (b"\x4c",)]
    GROUP_X_TO_WHITE = [(b"\xc5",), (b"\xc7",), (b"\xc9",), (b"\xcb",)]
    GROUP_X_NIGHTMODE = [(b"\xc6",), (b"\xc8",), (b"\xca",), (b"\xcc",)]
    COMMANDS = {
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

    def __init__(self, ip, **kwargs):
        """ Optional keyword arguments:
            - repeat_commands (default 3): how many times safe commands are repeated to ensure successful execution.
            - port (default 8899): UDP port on wifi gateway
            - pause_between_commands (default 0.1 (in seconds)): how long pause there should be between sending commands to the gateway.
            """
        self.ip = ip
        self.port = int(kwargs.get("port", 8899))
        self.last_command_at = 0
        self.repeat_commands = int(kwargs.get("repeat_commands", 3))
        if self.repeat_commands == 0:
            self.repeat_commands = 1
        self.pause_between_commands = float(kwargs.get("pause_between_commands", 0.1))

    def send_command(self, input_command):
        """ You shouldn't use this method directly.

            Sends a single command. If previous command was sent
            recently, sleep for 100ms (configurable with pause_between_commands
            constructor keyword). """
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
        sock.sendto(command, (self.ip, self.port))
        sock.close()

    def send_to_group(self, group, command, send_on=True, retries=None):
        """ You shouldn't use this method directly.

        Sends a single command to specific group.
        """
        if retries is None:
            retries = self.repeat_commands
        for _ in range(retries):
            if group is None or group == 0:
                if send_on:
                    self.send_command(self.COMMANDS["all_on"])
                self.send_command(command)
            elif group < 1 or group > 4:
                raise AttributeError("Group must be between 1 and 4 (was %s)" % group)
            else:
                if send_on:
                    self.send_command(self.GROUP_ON[group-1])
                self.send_command(command)

    def on(self, group=None):
        """ Switches lights on. If group (1-4) is not specified,
            all four groups will be switched on. """
        if group is None or group == 0:
            self.send_to_group(group, self.COMMANDS["all_on"], False)
            return
        self.send_to_group(group, self.GROUP_ON[group-1], False)

    def off(self, group=None):
        """ Switches lights off. If group (1-4) is not specified,
            all four groups will be switched off. """
        if group is None or group == 0:
            self.send_to_group(group, self.COMMANDS["all_off"], False)
            return
        self.send_to_group(group, self.GROUP_OFF[group-1], False)

    def white(self, group=None):
        """ Switches lights on and changes color to white.
            If group (1-4) is not specified, all four groups
            will be switched on and to white. """
        if group is None or group == 0:
            self.send_to_group(group, self.COMMANDS["all_white"])
            return
        self.send_to_group(group, self.GROUP_X_TO_WHITE[group-1])

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
            self.send_to_group(group, self.COMMANDS["color_to_"+color])

    def set_brightness(self, percent, group=None):
        """ Sets brightness. Percent is int between 0 (minimum brightness) and 100 (maximum brightness).

            See also .nightmode().

            If group (1-4) is not specified, brightness of all four groups will be adjusted.
            """
        if percent < 0:
            percent = 0
        if percent > 100:
            percent = 100
        # Map 0-100 to 2-27
        value = int(2 + ((float(percent) / 100) * 25))
        self.send_to_group(group, (b"\x4e", bytes([value])))

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
        self.send_to_group(group, self.COMMANDS["disco"], True, 1)

    def disco_faster(self, group=None):
        """ Adjusts up the speed of disco mode (if enabled; does not start disco mode). """
        self.send_to_group(group, self.COMMANDS["disco_faster"], True, 1)

    def disco_slower(self, group=None):
        """ Adjusts down the speed of disco mode (if enabled; does not start disco mode). """
        self.send_to_group(group, self.COMMANDS["disco_slower"], True, 1)

    def nightmode(self, group=None):
        """ Enables nightmode (very dim white light).

            The command is sent only once, as multiple commands would blink lights rapidly.
            There is no way to automatically detect whether transmitting the command succeeded or not.
            """
        if group is None or group == 0:
            self.off()
            self.send_command(self.COMMANDS["all_nightmode"])
            return
        self.off(group)
        self.send_command(self.GROUP_X_NIGHTMODE[group-1])

def main():
    led = LedController("192.168.1.6")
    led.set_color("red")
    led.set_brightness(100)

if __name__ == '__main__':
    main()
