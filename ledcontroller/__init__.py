# Documentation: http://www.limitlessled.com/dev/
import socket
import time

class LedController(object):
    GROUP_ON =  [(b"\x45",), (b"\x47",), (b"\x49",), (b"\x4b",)]
    GROUP_OFF = [(b"\x46",), (b"\x48",), (b"\x4a",), (b"\x4c",)]
    GROUP_X_TO_WHITE = [(b"\xc5",), (b"\xc7",), (b"\xc9",), (b"\xcb",)]
    COMMANDS = {
     "all_on": (b"\x42",),
     "all_off": (b"\x41",),
     "all_white": (b"\xc2",),
     "disco": (b"\x4d",),
     "disco_faster": (b"\x44",),
     "disco_slower": (b"\x43",),
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
        self.ip = ip
        self.port = int(kwargs.get("port", 8899))
        self.last_command_at = 0
        self.repeat_commands = int(kwargs.get("repeat_commands", 3))
        if self.repeat_commands == 0:
            self.repeat_commands = 1
        self.pause_between_commands = float(kwargs.get("pause_between_commands", 0.1))

    def send_command(self, input_command):
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
        if group is None or group == 0:
            self.send_to_group(group, self.COMMANDS["all_on"], False)
            return
        self.send_to_group(group, self.GROUP_ON[group-1], False)

    def off(self, group=None):
        if group is None or group == 0:
            self.send_to_group(group, self.COMMANDS["all_off"], False)
            return
        self.send_to_group(group, self.GROUP_OFF[group-1], False)

    def white(self, group=None):
        if group is None or group == 0:
            self.send_to_group(group, self.COMMANDS["all_white"])
            return
        self.send_to_group(group, self.GROUP_X_TO_WHITE[group-1])

    def set_color(self, color, group=None):
        if color == "white":
            self.white(group)
        else:
            self.send_to_group(group, self.COMMANDS["color_to_"+color])

    def set_brightness(self, percent, group=None):
        if percent < 0:
            percent = 0
        if percent > 100:
            percent = 100
        # Map 0-100 to 2-27
        value = int(2 + ((float(percent) / 100) * 25))
        self.send_to_group(group, (b"\x4e", bytes([value])))

    def disco(self, group=None):
        self.send_to_group(group, self.COMMANDS["disco"], True, 1)

    def disco_faster(self, group=None):
        self.send_to_group(group, self.COMMANDS["disco_faster"], True, 1)

    def disco_slower(self, group=None):
        self.send_to_group(group, self.COMMANDS["disco_slower"], True, 1)


def main():
    led = LedController("192.168.1.6")
    led.set_color("red")
    led.set_brightness(100)

if __name__ == '__main__':
    main()
