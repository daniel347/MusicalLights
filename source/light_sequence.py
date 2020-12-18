import numpy as np

class LightSequence:

    def __init__(self, led_array=None, change_times=None, sequence_list_time=None):
        self.led_array = None
        self.change_times = None

        if led_array is not None and change_times is not None:
            self.construct_from_arrays(led_array, change_times)
        elif sequence_list_time is not None:
            self.construct_from_time_sequences(sequence_list_time)

    def construct_from_arrays(self, led_array, change_times):
        assert led_array.shape[0] == change_times.shape[0]

        self.led_array = led_array
        self.change_times = change_times

    def construct_from_time_sequences(self, sequence_list):
        """concatenates a number of time sequences, e.g. produced for different sections of the song"""
        assert all(seq.led_array.shape[0] == seq.change_times.shape[0] for seq in sequence_list)

        self.change_times = np.concatenate([seq.change_times for seq in sequence_list])
        assert np.all(np.diff(self.change_times) > 0)  # check all the times are increasing

        self.led_array = np.concatenate([seq.led_array for seq in sequence_list], axis=0)

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