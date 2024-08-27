"""A module to manage libraries of spectrophotometric standard stars
"""


import numpy as np
import pandas
from bbf.bspline import BSpline, Projector


__all__ = ['StellarLib']


class StellarLib:
    """A generic stellar library

    The library data is stored in a DataFrame. One line per spectrum. Two
    mandatory columns: wave and flux.

    """
    def __init__(self, data, basis=None, project=True):
        """Constructor. Build an internal basis and project the dataset on it

        Parameters
        ----------
        data: (pandas.DataFrame)
          the dataset that holds the spectra. Two required fields: ``wave`` and `flux`
        basis: BSpline (1D) or np.ndarray
          the internal basis. If of type `ndarray` then instantiate a `BSpline` from that
        project: (bool), default=True
          whether to project the dataset on the basis or raise NotImplementedError

        The dataset coefficients are stored in `self.coeffs`, a 2D array.
        """
        self.data = data
        assert 'wave' in data.columns and 'flux' in data.columns
        self.basis = None
        if isinstance(basis, BSpline):
            self.basis = basis
        elif isinstance(basis, np.ndarray):
            self.basis = BSpline(basis)
        elif basis is None:
            self.basis = self._default_basis()
        else:
            raise ValueError(f'unable to build a basis from {basis}')

        # if basis is not None:
        #     self.basis = basis
        # elif grid is not None:
        #     self.basis = BSpline(grid)
        if project:
            self.coeffs = self.project()
        else:
            self.coeffs = None

    def __len__(self):
        """number of spectra in the library"""
        return len(self.data)

    def _same_wave_grid(self):
        """test whether the binning is the same for all spectra in the library
        """
        d = self.data
        return np.all(d.wave.apply(lambda x: np.array_equal(x, d.iloc[0].wave)))

    def _default_basis(self):
        return BSpline(np.arange(3000., 11010., 10.))

    def project(self):
        """project the spectra on the class internal basis

        if all the spectra are defined on the same grid, we use a projector
        (theoretically faster than doing individual fits for all spectra).
        Otherwise, we fit all the spectra individually.

        Returns
        -------
        a 2D ndarray, of dimensions n_spec x n_splines
        """
        # if all the spectra share the same grid, we use a projector
        if self._same_wave_grid():
            proj = Projector(self.basis)
            ret = proj(np.vstack(self.data.flux), x=self.data.iloc[0].wave)
        # otherwise, we fit the spectra one by one
        else:
            t = []
            for i in range(len(self.data)):
                sp = self.data.iloc[i]
                t.append(self.basis.linear_fit(sp.wave, sp.flux, beta=1.E-6))
            ret = np.vstack(t).T
        return ret

    def to_hdf5(self, fn):
        """
        """
        # import h5py
        # with h5py.File(fn, 'w') as f:
        #     spectra = f.create_group('spectra')
        #     self.data.to_hdf5
        #     f.create_dataset('spectra', data=self.data)
        #     f.create_dataset('basis', data=self.basis.grid)
        self.data.to_hdf(fn, key='spectra', mode='w')
        basis = pandas.DataFrame({'grid': self.basis.grid})
        basis.to_hdf(fn, key='grid', mode='a')

    @classmethod
    def from_hdf5(cls, fn, basis=None):
        """
        """
        # import h5py
        # with h5py.File(fn, 'r') as f:
        #     spectra = f['spectra']
        #     if basis is None:
        #         grid = f['grid']
        #         basis = BSpline(grid)
        data = pandas.read_hdf(fn, 'spectra')
        if basis is None:
            grid = pandas.read_hdf(fn, 'grid').to_numpy().squeeze()
            basis = BSpline(grid)
        return cls(data, basis=basis)

    def to_parquet(self, prefix):
        """
        """
        prefix = str(prefix)
        prefix = prefix.replace('.parquet', '')
        self.data.to_parquet(prefix + '_data.parquet')
        basis = pandas.DataFrame({'grid': self.basis.grid})
        basis.to_parquet(prefix + '_grid.parquet')

    @classmethod
    def from_parquet(cls, prefix, basis=None):
        """
        """
        prefix = str(prefix)
        prefix = prefix.replace('.parquet', '')
        data = pandas.read_parquet(prefix + '_data.parquet')
        if basis is None:
            grid = pandas.read_parquet(prefix + '_grid.parquet')
            basis = BSpline(grid['grid'].to_numpy())
        return cls(data, basis=basis)
