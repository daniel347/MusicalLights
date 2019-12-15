import numpy as np
import matplotlib.pyplot as plt

import dsp

if __name__ == "__main__":
    t = np.linspace(0, 2 * np.pi, 100)
    x = np.sin(t) + np.sin(4*t)

    plt.plot(t, x)
    plt.show()

    fourier, frequencies = dsp.fourier(x, 100)

    plt.plot(frequencies, fourier)
    # plt.xlim(0,5)
    plt.show()



