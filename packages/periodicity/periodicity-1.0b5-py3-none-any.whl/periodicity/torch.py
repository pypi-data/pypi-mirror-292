import torch


def torch_peaks(y, method):
    y1 = y[..., 1:-1] - y[..., :-2]
    y1 = torch.where(y1 < 0, y1 * 0 - 1, torch.where(y1 > 0, y1 * 0 + 1, y1))
    y2 = y[..., 1:-1] - y[..., 2:]
    y2 = torch.where(y2 < 0, y2 * 0 - 1, torch.where(y2 > 0, y2 * 0 + 1, y2))
    if method == "bfill":
        y2 = torch.where(y2 == 0, -y1, y2)
        first_nonzero = (y2.abs() * torch.arange(y2.shape[-1], 0, -1)).argmax(
            -1, keepdim=True
        )
        last_nonzero = (y2.abs() * torch.arange(y2.shape[-1])).argmax(-1, keepdim=True)
        y2_without_first_nonzero = y2.scatter(-1, first_nonzero, 0)
        y2_without_last_nonzero = y2.scatter(-1, last_nonzero, 0)
        ind = torch.where(y2_without_last_nonzero != 0)
        indp1 = torch.where(y2_without_first_nonzero != 0)
        y1[indp1] = -y2[ind]
    elif method == "ffill":
        y1 = torch.where(y1 == 0, -y2, y1)
        first_nonzero = (y1.abs() * torch.arange(y1.shape[-1], 0, -1)).argmax(
            -1, keepdim=True
        )
        last_nonzero = (y1.abs() * torch.arange(y1.shape[-1])).argmax(-1, keepdim=True)
        y1_without_first_nonzero = y1.scatter(-1, first_nonzero, 0)
        y1_without_last_nonzero = y1.scatter(-1, last_nonzero, 0)
        ind = torch.where(y1_without_last_nonzero != 0)
        indp1 = torch.where(y1_without_first_nonzero != 0)
        y2[ind] = -y1[indp1]
    else:
        raise ValueError("method must be either 'bfill' or 'ffill'!")
    out1 = torch.where(y1 > 0, y1 * 0 + 1, y1 * 0)
    out2 = torch.where(y2 > 0, out1, y2 * 0)
    peaks = torch.nonzero(out2)
    batch, cols = peaks[..., :-1], peaks[..., -1]
    cols.add_(1)
    return batch, cols


def torch_cubic(x, y, xs):
    nf = y.size(-1)
    if nf == 0:
        return torch.zeros_like(xs, dtype=y.dtype, device=y.device)
    if nf == 1:
        return torch.ones_like(xs, dtype=y.dtype, device=y.device) * y[..., [0]]
    if nf == 2:
        a = y[..., :1]
        b = (y[..., 1:] - y[..., :1]) / (x[..., 1:] - x[..., :1])
        c = torch.zeros(*y.shape[:-1], 1, dtype=y.dtype, device=y.device)
        d = torch.zeros(*y.shape[:-1], 1, dtype=y.dtype, device=y.device)
    else:
        dx = x[1:] - x[:-1]
        inv_dx = dx.reciprocal()
        inv_dx2 = inv_dx**2
        dy = y[..., 1:] - y[..., :-1]
        dy_scaled = 3 * dy * inv_dx2
        D = torch.empty(nf, dtype=y.dtype, device=y.device)
        D[:-1] = inv_dx
        D[-1] = 0
        D[1:] += inv_dx
        D *= 2
        f = torch.empty_like(y)
        f[..., :-1] = dy_scaled
        f[..., -1] = 0
        f[..., 1:] += dy_scaled
        U = inv_dx.clone().detach()
        L = inv_dx.clone().detach()
        for i in range(1, nf):
            w = L[i - 1] / D[i - 1]
            D[i] = D[i] - w * U[i - 1]
            f[i] = f[i] - w * f[i - 1]
        out = f / D
        for i in range(nf - 2, -1, -1):
            out[i] = (f[i] - U[i] * out[i + 1]) / D[i]
        a = y[..., :-1]
        b = out[..., :-1]
        c = (3 * dy * inv_dx - 2 * out[..., :-1] - out[..., 1:]) * inv_dx
        d = (-2 * dy * inv_dx + out[..., :-1] + out[..., 1:]) * inv_dx2
    maxlen = b.size(-1) - 1
    index = torch.bucketize(xs.detach(), x) - 1
    index = index.clamp(0, maxlen)
    t = xs - x[index]
    inner = c[..., index] + d[..., index] * t
    inner = b[..., index] + inner * t
    return a[..., index] + inner * t


def torch_hermite(x, y, xs):
    nf = y.size(-1)
    if nf == 0:
        return torch.zeros_like(xs, dtype=y.dtype, device=y.device)
    if nf == 1:
        return torch.ones_like(xs, dtype=y.dtype, device=y.device) * y[..., [0]]
    else:
        delta = x[..., 1:] - x[..., :-1]
        last_nonzero = (-delta).signbit().cumsum(-1)[..., [-1]].clamp(min=1)
        m = (y[..., 1:] - y[..., :-1]) / delta
        replacement = torch.take_along_dim(m, last_nonzero - 1, dim=-1)
        m = torch.where(torch.isnan(m), replacement, m)
        m = torch.cat(
            [m[..., [0]], (m[..., 1:] + m[..., :-1]) / 2, m[..., [-1]]], axis=1
        )
        idxs = torch.searchsorted(x, xs) - 1
        idxs.clamp_(min=0, max=nf - 2)
        xi = torch.take_along_dim(x, idxs, dim=-1)
        dx = torch.take_along_dim(x, idxs + 1, dim=-1) - xi
        t = (xs - xi) / dx
        tt = t[..., None, :] ** torch.arange(4, device=t.device)[:, None]
        A = torch.tensor(
            [[1, 0, -3, 2], [0, 1, -2, 1], [0, 0, 3, -2], [0, 0, -1, 1]],
            dtype=t.dtype,
            device=t.device,
        )
        hh = A @ tt
        yi = torch.take_along_dim(y, idxs, dim=-1)
        mi = torch.take_along_dim(m, idxs, dim=-1)
        yi1 = torch.take_along_dim(y, idxs + 1, dim=-1)
        mi1 = torch.take_along_dim(m, idxs + 1, dim=-1)
        return (
            hh[..., 0, :] * yi
            + hh[..., 1, :] * mi * dx
            + hh[..., 2, :] * yi1
            + hh[..., 3, :] * mi1 * dx
        )


def torch_akima(x, y, xs):
    nf = y.size(-1)
    if nf == 0:
        return torch.zeros_like(xs, dtype=y.dtype, device=y.device)
    if nf == 1:
        return torch.ones_like(xs, dtype=y.dtype, device=y.device) * y[..., [0]]
    if nf == 3:
        return torch_hermite(x, y, xs)
    delta = x[..., 1:] - x[..., :-1]
    last_nonzero = (-delta).signbit().cumsum(-1)[..., [-1]].clamp(min=1)
    m = (y[..., 1:] - y[..., :-1]) / delta
    replacement = torch.take_along_dim(m, last_nonzero - 1, dim=-1)
    m = torch.where(torch.isnan(m), replacement, m)
    if nf == 2:
        return m * (xs - x[..., [0]]) + y[..., [0]]
    else:
        mm = 2.0 * m[..., [0]] - m[..., [1]]
        mmm = 2.0 * mm - m[..., [0]]
        mp = 2.0 * m[..., [-2]] - m[..., [-3]]
        mpp = 2.0 * mp - m[..., [-2]]
        m = torch.cat([mmm, mm, m, mp, mpp], axis=-1)
        dm = torch.abs(m[..., 1:] - m[..., :-1])
        f1 = dm[..., 2:]
        f2 = dm[..., :-2]
        f12 = f1 + f2
        ind = torch.nonzero(f12 > 1e-9 * f12.max(), as_tuple=True)
        batch_ind, x_ind = ind[:-1], ind[-1]
        b = m[..., 1:-1].clone().detach()
        b[ind] = (
            f1[ind] * m[batch_ind + (x_ind + 1,)]
            + f2[ind] * m[batch_ind + (x_ind + 2,)]
        ) / f12[ind]
        c = (3.0 * m[..., 2:-2] - 2.0 * b[..., :-2] - b[..., 1:-1]) / delta
        d = (b[..., :-2] + b[..., 1:-1] - 2.0 * m[..., 2:-2]) / delta**2
        idxs = torch.searchsorted(x, xs) - 1
        idxs.clamp_(min=0, max=nf - 2)
        xi = torch.take_along_dim(x, idxs, dim=-1)
        yi = torch.take_along_dim(y, idxs, dim=-1)
        di = torch.take_along_dim(d, idxs, dim=-1)
        ci = torch.take_along_dim(c, idxs, dim=-1)
        bi = torch.take_along_dim(b, idxs, dim=-1)
        t = xs - xi
        return ((t * di + ci) * t + bi) * t + yi


class TorchEMD(object):
    def __init__(
        self,
        max_iter=2000,
        theta_1=0.05,
        theta_2=0.50,
        alpha=0.05,
        spline=torch_akima,
    ):
        self.max_iter = max_iter
        self.theta_1 = theta_1
        self.theta_2 = theta_2
        self.alpha = alpha
        self.spline = spline

    def get_envelope(self, batch, cols, y, yy):
        # remove peaks on the edges of the original signals
        mask = cols % (self.size - 1) > 0
        batch = batch[mask]
        cols = cols[mask]
        # use linear indices to calculate n_peaks
        ravel = (batch * self.coefs).sum(dim=-1)
        n_ext = torch.bincount(ravel, minlength=self.n_signals).reshape(
            self.batch_shape
        )
        # fancy indexing by repeating the last elements of the batches with fewer peaks
        index = torch.zeros(n_ext.shape + (n_ext.max() + 1,), dtype=int)
        index.scatter_(-1, n_ext.view(*self.shape), 1)
        index = index[..., 1:].flip(dims=(-1,)).cumsum(-1).flip(dims=(-1,))
        index = index.view(-1).cumsum(0).view(n_ext.shape + (n_ext.max(),))
        # the original signal is repeated 3 times, determine actual number of peaks
        n_ext.div_(3, rounding_mode="floor")
        # use the fancy indexing to get peaks for each batch
        t_ext = self.tt[cols[index - 1]]
        y_ext = torch.take_along_dim(yy, cols[index - 1], dim=-1)
        env = self.spline(t_ext, y_ext, self.t_interp)
        # replace interpolation of monotonic residues with the original signal
        env = torch.where(torch.isnan(env), y, env)
        return n_ext, env

    def sift(self, y):
        """
        Parameters
        ----------
        y: Tensor (..., size)

        Returns
        -------
        mu: Tensor (..., size)
        is_imf: Tensor (...,)
        is_monotonic: Tensor (...,)
        """
        yy = torch.cat(
            [y[..., 1:].flip(-1), y, y[..., :-1].flip(-1)],
            axis=-1,
        )
        peak_batch, peak_cols_f = torch_peaks(yy, "ffill")
        peak_batch, peak_cols_b = torch_peaks(yy, "bfill")
        peak_cols = (peak_cols_b + peak_cols_f).div(2, rounding_mode="floor")
        n_peaks, upper = self.get_envelope(peak_batch, peak_cols, y, yy)
        dip_batch, dip_cols_f = torch_peaks(-yy, "ffill")
        dip_batch, dip_cols_b = torch_peaks(-yy, "bfill")
        dip_cols = (dip_cols_b + dip_cols_f).div(2, rounding_mode="floor")
        n_dips, lower = self.get_envelope(dip_batch, dip_cols, y, yy)
        # find zero crossings
        n_zero = torch.count_nonzero(torch.diff(torch.signbit(yy)), axis=-1)
        n_zero.div_(3, rounding_mode="floor")
        is_monotonic = (n_peaks < 2) | (n_dips < 2)
        mu = (upper + lower) / 2
        amp = (upper - lower) / 2
        sigma = torch.abs(mu / amp)

        print(
            torch.vstack(
                [
                    n_peaks,
                    n_dips,
                    n_zero,
                    torch.abs(n_peaks + n_dips - n_zero),
                    (sigma > self.theta_1).sum(-1),
                    (sigma > self.theta_2).sum(-1),
                ]
            )
        )

        # stoppig criteria
        is_imf = (sigma > self.theta_1).sum(axis=-1) < (self.alpha * self.size)
        is_imf &= (sigma < self.theta_2).all(axis=-1)
        is_imf &= torch.abs(n_peaks + n_dips - n_zero) <= 1
        return mu, is_imf, is_monotonic

    def iter(self, y):
        """
        Parameters
        ----------
        y: Tensor (..., size)

        Returns
        -------
        mode: Tensor (..., size)
        is_monotonic: Tensor (...,)
        """
        mode = y.clone().detach()
        for it in range(self.max_iter):
            if it == 0:
                mu, is_imf, is_monotonic = self.sift(mode)
            else:
                mu, is_imf, _ = self.sift(mode)
            if (is_monotonic | is_imf).all():
                break
            mode[~is_imf] = mode[~is_imf] - mu[~is_imf]
            # mode[is_monotonic] = 0.0
        return mode, is_monotonic

    def fit(self, t, X):
        size = X.shape[-1]
        if t.ndim != 1:
            raise ValueError("'t' should be 1D.")
        if size != t.shape[0]:
            raise ValueError(
                f"'t' should have the same size as the last dim of 'X' "
                f"(got {t.shape[0]} and {size})."
            )
        self.time = t
        self.size = size
        self.tt = torch.cat(
            [
                2 * self.time[0] - self.time[1:].flip(-1),
                self.time,
                2 * self.time[-1] - self.time[:-1].flip(-1),
            ]
        )
        self.device = X.device

    def transform(self, X, max_modes=None):
        if X.shape[-1] != self.size:
            raise ValueError(
                f"the last dim of 'X' should have the same size as 'time' "
                f"(got {X.shape[-1]} and {self.size})."
            )
        *self.batch_shape, self.size = X.shape
        self.shape = torch.tensor(self.batch_shape + [1], dtype=int, device=self.device)
        self.n_signals = self.shape.prod()
        self.coefs = self.shape[1:].flipud().cumprod(dim=0).flipud()
        # t_interp must have same batches as t_peaks for the searchsorted step
        self.t_interp = self.time.expand(X.shape)
        if max_modes is None:
            max_modes = torch.inf
        imfs = []
        is_monotonic = torch.zeros(self.batch_shape, dtype=bool)
        residue = X.clone().detach()
        while not is_monotonic.all() and len(imfs) < max_modes:
            mode, is_monotonic = self.iter(residue)
            if is_monotonic.all():
                break
            imfs.append(mode)
            residue = residue - mode
        # Defines useful attributes
        self.modes = imfs
        self.residue = residue
        self.n_modes = len(imfs)
        return self.modes

    def __call__(self, t, X, max_modes=None):
        self.fit(t, X)
        return self.transform(X, max_modes)


class TorchCEEMDAN(object):
    def __init__(
        self,
        epsilon=0.2,
        ensemble_size=50,
        min_energy=0.0,
        random_seed=None,
        **emd_kwargs,
    ):
        self.epsilon = epsilon
        self.ensemble_size = ensemble_size
        self.min_energy = min_energy
        if random_seed is not None:
            torch.manual_seed(random_seed)
        self.emd = TorchEMD(**emd_kwargs)

    def _realization(self, noise_modes, k, residue):
        noisy_residue = residue.copy()
        if len(noise_modes) > k:
            beta = self.epsilon * np.std(residue)
            if k == 0:
                beta /= np.std(noise_modes[k])
            noisy_residue = noisy_residue + beta * noise_modes[k]
        try:
            mode = self.emd(noisy_residue, max_modes=1)[0]
        except IndexError:
            # in case noisy_residue happens to be monotonic even though residue was not
            mode = noisy_residue.copy()
        return noisy_residue - mode

    def __call__(self, t, X, max_modes=None):
        size = X.shape[-1]
        if t.ndim != 1:
            raise ValueError("'t' should be 1D.")
        if size != t.shape[0]:
            raise ValueError(
                f"'t' should have the same size as the last dim of 'X' "
                f"(got {t.shape[0]} and {size})."
            )
        self.time = t
        self.size = size
        self.device = X.device
        if max_modes is None:
            max_modes = torch.inf
        sigma_x = X.std(-1)
        white_noise = torch.randn((self.ensemble_size, self.size), dtype=X.dtype)
        white_noise_modes = self.emd(white_noise)

        imfs = []
        residue = X / sigma_x
        while len(imfs) < max_modes:
            k = len(imfs)

            # Averages the ensemble of trials for the next mode
            mu = 0
            tasks = [(noise_modes, k, residue) for noise_modes in white_noise_modes]
            mus = pool.map(self._realization, tasks)
            mu = sum(mus) / self.ensemble_size
            imfs.append(residue - mu)
            residue = mu.copy()

            # Checks stopping criteria (if the residue is an IMF or too small)
            if np.var(residue) < self.min_energy:
                break
            residue_imfs = self.emd(residue)
            if len(residue_imfs) <= 1:
                if len(imfs) < max_modes and len(residue_imfs) == 1:
                    imfs.append(residue)
                break

        # Undoes the initial normalization
        for i in range(len(imfs)):
            imfs[i] *= sigma_x
        self.signal = signal
        self.modes = imfs
        self.residue = signal - sum(imfs)
        self.n_modes = len(imfs)
        return self.modes


class TorchSSA(object):
    def __init__(self, L):
        self.L = L

    def __call__(self, t, x, max_components=None, min_sigma=0):
        N = t.size(0)
        K = N - self.L + 1
        if max_components is None:
            max_components = self.L
        rangeL = torch.arange(self.L, device=x.device)
        ids = torch.arange(K, device=x.device).expand(self.L, K)
        ids = ids + rangeL.view(-1, 1)
        X = x[ids]
        U, S, VT = torch.linalg.svd(X)
        self.sigma = S
        d = torch.linalg.matrix_rank(X).item()
        self.rank = d
        d = min(d, max_components)
        d = min(d, torch.where(S / S[0] > min_sigma)[0][-1] + 1)
        X_elem = torch.full((self.L, N), torch.nan, device=x.device)
        x_ids = torch.repeat_interleave(rangeL, K)
        y_ids = ids.flipud().flatten()
        results = torch.empty((d, N), device=x.device)
        for i in range(d):
            X_elem[x_ids, y_ids] = (S[i] * U[:, i].outer(VT[i, :])).flipud().flatten()
            results[i] = torch.nanmean(X_elem, 0)
        return results


"""

%matplotlib tk
import numpy as np
import matplotlib.pyplot as plt
from periodicity.core import TSeries
from periodicity.torch import TorchEMD
from periodicity.decomposition import EMD
from astropy.io import fits
import torch

i = 2
y = fits.open(f'simu_8192/signals/{i:06d}.fits')[0].data.astype('float32')
y = y[::10]
t = np.arange(0, 1024, 1/8, dtype='float32')
sig_list = [TSeries(t, y[i]) for i in range(10)]

cpu_emd = TorchEMD(device="cpu", max_iter=20)
gpu_emd = TorchEMD(device="cuda", max_iter=20)
emd = EMD(max_iter=20)


"""
