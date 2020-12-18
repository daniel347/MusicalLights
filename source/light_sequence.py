class LightSequence:

    def __init__(self, led_array, change_times):
        assert led_array.shape[0] == change_times.shape[0]

        self.led_array = led_array
        self.change_times = change_times

    def __iter__(self):
        return LightSequenceIterator(self)


class LightSequenceIterator:

    def __init__(self, light_sequence):
        self.light_sequence = light_sequence
        self.sequence_length = light_sequence.change_times.shape[0]
        self._index = 0

    def __next__(self):
        if self._index >= self.sequence_length:
            raise StopIteration

        self._index += 1
        return (self.light_sequence.change_times[self._index - 1],
                self.light_sequence.led_array[self._index - 1])