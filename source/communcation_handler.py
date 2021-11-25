import json

class ComHandler():

    def __init__(self, socket_client):
        self.client = socket_client
        self.end_code = bytes([0x00])  # A End of Transmission symbol

    def set_leds_active(self, active):
        message = {"method" : "setLedsActive",
                   "value" : active}
        self.send_message(message)

    def set_mode(self, mode):
        message = {"method" : "setMode",
                   "value" : mode}
        self.send_message(message)

    def set_static_colour(self, colour):
        message = {"method" : "setStaticColour",
                   "value" : {"r" : colour[0],
                              "g" : colour[1],
                              "b" : colour[2]}
                   }
        self.send_message(message)

    def send_message(self, message):
        data = json.dumps(message)
        self.client.send(bytes(data, 'ascii'))
        self.client.send(self.end_code)