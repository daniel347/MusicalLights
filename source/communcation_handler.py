import json

class ComHandler():

    def __init__(self, socket_client):
        self.client = socket_client
        self.end_code = 0x00  # A null

    def set_leds_active(self, active):
        message = {"method" : "setLedsActive",
                   "value" : active}
        self.send_message(message)

    def set_mode(self, mode):
        message = {"method" : "setMode",
                   "value" : mode}
        self.send_message(message)

    def send_message(self, message):
        data = json.dumps(message)
        self.client.send(data)
        self.client.send(self.end_code)