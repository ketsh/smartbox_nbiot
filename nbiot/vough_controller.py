from machine import UART, Pin

class VoungController:
    def __init__(self):
        self.uart0 = UART(1, 9600,rx=3,tx=1,timeout=10)

    def calculate_checksum(self, message):
        checksum = 0
        for byte in message:
            checksum ^= byte
        return checksum

    def open_lock(self, board_id, door_id, byt = True):
        start_character = [0x57, 0x4B, 0x4C, 0x59]
        instruction_word = [0x82]
        data_field = [door_id]
        frame_length = len(start_character) + 1 + 1 + len(instruction_word) + len(data_field) + 1  # +1 for checksum

        message = start_character + [frame_length, board_id] + instruction_word + data_field
        message.append(self.calculate_checksum(message))
        if byt:
            self.uart0.write(bytearray(message))
        else:
            self.uart0.write(bytes(message))
