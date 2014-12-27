# Documentation: http://www.limitlessled.com/dev/
import socket
import time

wifi_bridge_ip = "192.168.1.111"
wifi_bridge_port = 8899

class LedController(object):
    GROUP_ON =  ["\x45", "\x47", "\x49", "\x4b"]
    GROUP_OFF = ["\x46", "\x48", "\x4a", "\x4c"]
    GROUP_X_TO_WHITE = ["\xc5", "\xc7", "\xc9", "\xcb"]
    COMMANDS = {
     "all_on": "\x42",
     "all_off": "\x41",
     "all_white": "\xc2",
     "disco": "\x4d",
     "disco_faster": "\x44",
     "disco_slower": "\x43",
     "color_to_violet": ("\x40", "\x00"),
     "color_to_royal_blue": ("\x40", "\x10"),
     "color_to_baby_blue": ("\x40", "\x20"),
     "color_to_aqua": ("\x40", "\x30"),
     "color_to_royal_mint": ("\x40", "\x40"),
     "color_to_seafoam_green": ("\x40", "\x50"),
     "color_to_green": ("\x40", "\x60"),
     "color_to_lime_green": ("\x40", "\x70"),
     "color_to_yellow": ("\x40", "\x80"),
     "color_to_yellow_orange": ("\x40", "\x90"),
     "color_to_orange": ("\x40", "\xa0"),
     "color_to_red": ("\x40", "\xb0"),
     "color_to_pink": ("\x40", "\xc0"),
     "color_to_fusia": ("\x40", "\xd0"),
     "color_to_lilac": ("\x40", "\xe0"),
     "color_to_lavendar": ("\x40", "\xf0"),
    }

    def __init__(self, ip, port=8899, repeat_commands=3):
        self.ip = ip
        self.port = port
        self.last_command_at = 0
        self.repeat_commands = repeat_commands

    def send_command(self, input_command):
        time_since_last_command = time.time() - self.last_command_at
        if time_since_last_command < 0.100:
            # Lights require 100ms pause between commands to function at least almost reliably.
            time.sleep(0.1 - time_since_last_command)
        self.last_command_at = time.time()
        command = ""
        for item in input_command:
            command = command + item
        if len(command) == 1:
            command = command + b"\x00"
        if len(command) == 2:
            command = command + b"\x55"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command, (self.ip, self.port))

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
        self.send_to_group(group, ("\x4e", chr(value)))

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
