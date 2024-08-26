import os
import unittest

import numpy as np

from maspim.project.file_helpers import get_d_folder
from maspim import hdf5Handler, Spectra
from maspim.res.compound_masses import mC37_3, mC37_2

path_folder = r'C:\Users\Yannick Zander\Promotion\Test data'
# path_folder = r'C:\Users\Yannick Zander\Promotion\Cariaco MSI 2024\490-495cm\2018_08_27 Cariaco 490-495 alkenones.i'
path_d_folder = os.path.join(path_folder, get_d_folder(path_folder))

reader = hdf5Handler(path_d_folder)


def test_spectra():
    spec = Spectra(path_d_folder=path_d_folder, reader=reader)

    # __init__
    assert spec.delta_mz == 1e-4
    assert np.allclose(spec.limits, (544., 564.))
    idcs = np.arange(1, 72 + 1)
    assert np.allclose(
        np.arange(spec.limits[0], spec.limits[1] + spec.delta_mz * 2, spec.delta_mz),
        spec.mzs
    )
    assert spec.indices.shape == idcs.shape
    assert np.allclose(spec.indices, idcs)
    assert os.path.samefile(spec.path_d_folder, path_d_folder)

    # other stuff
    i = np.ones_like(spec.mzs)
    spec.add_spectrum(i)
    assert np.allclose(spec.intensities, i)
    spec.reset_intensities()
    assert np.allclose(spec.intensities, np.zeros_like(spec.mzs))

    spec.add_all_spectra(reader=reader)
    assert np.allclose(np.load('summed_intensities.npy'), spec.intensities)

    spec.set_noise_level()
    assert np.allclose(np.load('noise_level.npy'), spec.noise_level)

    spec.subtract_baseline()
    tc = unittest.TestCase()
    with tc.assertRaises(AssertionError):
        spec.subtract_baseline()

    shift = spec.get_mass_shift(reader.get_spectrum(5))
    assert abs(shift - -0.0003) < 1e-12

    spec.set_peaks()
    assert np.allclose(np.load('test_peaks.npy'), spec._peaks)

    spec.set_targets([mC37_2, mC37_3], method='area', reader=reader)
    spec.set_targets([mC37_2, mC37_3], method='height', reader=reader)
    spec.set_targets([mC37_2, mC37_3], method='max', reader=reader)


if __name__ == '__main__':
    pass
    
    # reader.get_spectrum(70).plot()

    spec = Spectra(path_d_folder=path_d_folder, reader=reader)
    spec.add_calibrated_spectra(reader=reader)
    # spec.set_targets([mC37_2, mC37_3], method='height', reader=reader, plts=True)

    spec.set_peaks()
    spec.set_kernels()
    spec.bin_spectra(reader=reader)
    spec.filter_line_spectra(binned_snr_threshold=2)
    spec.set_reconstruction_losses(reader=reader)

    spec.plot_losses()


