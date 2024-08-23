from multiprocessing import Pool

import numpy as np
from tqdm.auto import trange

from .core import TSeries

__all__ = ["EMD", "CEEMDAN", "LMD", "VMD"]
# TODO: Variational Mode Decomposition (Dragomiretskiy & Zosso, 2014)


class EMD(object):
    def __init__(
        self, max_iter=2000, pad_width=2, theta_1=0.05, theta_2=0.50, alpha=0.05
    ):
        """Empirical Mode Decomposition

        Parameters
        ----------
        max_iter: int, optional
            Maximum number of sifting iterations (the default is 2000).
        pad_width: int, optional
            Number of extrema to repeat on either side of the signal while
            interpolating envelopes (the default is 2).
        theta_1: float, optional
            Lower threshold for the evaluation function (the default is 0.05).
        theta_2: float, optional
            Upper threshold for the evaluation function (usually ``10 * theta_1``).
        alpha: float, optional
            Fraction of total duration where the evaluation function is allowed to
            be ``theta_1 < sigma < theta_2`` (the default is 0.05).

        References
        ----------
        .. [#] G. Rilling, P. Flandrin, P. Gonçalves, "On Empirical Mode
        Decomposition and its Algorithms," IEEE-EURASIP Workshop on Nonlinear
        Signal and Image Processing, June 2003.
        """
        self.max_iter = max_iter
        self.pad_width = pad_width
        self.theta_1 = theta_1
        self.theta_2 = theta_2
        self.alpha = alpha

    def sift(self, sig):
        peaks = sig.find_peaks(include_edges=True)
        n_peaks = peaks.size - 2
        dips = sig.find_dips(include_edges=True)
        n_dips = dips.size - 2
        n_ext = n_peaks + n_dips
        ind_zer = sig.find_zero_crossings()
        n_zero = ind_zer.size
        if n_peaks < self.pad_width or n_dips < self.pad_width:
            raise ValueError("Signal doesn't have enough extrema for padding.")
        peaks = peaks.pad(
            self.pad_width, mode="reflect", reflect_type=["odd", None]
        ).drop([self.pad_width, -self.pad_width - 1])
        dips = dips.pad(
            self.pad_width, mode="reflect", reflect_type=["odd", None]
        ).drop([self.pad_width, -self.pad_width - 1])
        if peaks.size < 4 or dips.size < 4:
            raise ValueError(
                "Signal doesn't have enough extrema for envelope interpolation."
            )
        upper = peaks.interp(new_time=sig.time, method="spline").values
        lower = dips.interp(new_time=sig.time, method="spline").values
        mu = (upper + lower) / 2
        amp = (upper - lower) / 2
        sigma = np.abs(mu / amp)
        return mu, sigma, n_ext, n_zero

    def iter(self, sig):
        is_monotonic = False
        mode = sig.copy()
        for it in range(self.max_iter):
            try:
                mu, sigma, n_ext, n_zero = self.sift(mode)
            except ValueError:
                # print(it)
                is_monotonic = True
                break
            # sigma < theta_1 for some prescribed fraction (1-alpha) of the total duration
            is_imf = np.mean(sigma > self.theta_1) < self.alpha
            # sigma < theta_2 for the remaining fraction
            is_imf = is_imf and np.all(sigma < self.theta_2)
            # The number of extrema and zero-crossings must differ at most by 1
            is_imf = is_imf and (np.abs(n_zero - n_ext) <= 1)
            # Checks stopping criteria BEFORE updating the current mode
            if is_imf:
                # print(it)
                break
            mode = mode - mu
        return mode, is_monotonic

    def __call__(self, signal, max_modes=None):
        """
        Parameters
        ----------
        max_modes: int, optional
            If given, stops the decomposition after this number of modes.
        """
        if not isinstance(signal, TSeries):
            signal = TSeries(values=signal)
        if max_modes is None:
            max_modes = np.inf
        imfs = []
        is_monotonic = signal.size < 4
        residue = signal.copy()
        while not is_monotonic and len(imfs) < max_modes:
            mode, is_monotonic = self.iter(residue)
            if not is_monotonic:
                imfs.append(mode)
                residue = residue - mode
        # Defines useful attributes
        self.signal = signal
        self.modes = imfs
        self.residue = residue
        self.n_modes = len(imfs)
        return self.modes


class LMD(object):
    def __init__(self, max_iter=10, pad_width=0, smooth_iter=12, eps=1e-6):
        self.max_iter = max_iter
        self.pad_width = pad_width
        self.smooth_iter = smooth_iter
        self.eps = eps

    def sift(self, sig):
        # define padded extrema
        peaks = sig.find_peaks(include_edges=True)
        dips = sig.find_dips()
        extrema = peaks.join(dips)
        if extrema.size < (2 + self.pad_width):
            raise ValueError("Signal doesn't have enough extrema for padding.")
        if self.pad_width > 0:
            extrema = extrema.pad(
                self.pad_width, mode="reflect", reflect_type="odd"
            ).drop([self.pad_width, -self.pad_width - 1])
        # zero-order hold local mean and envelope
        if extrema.size < 3:
            raise ValueError(
                "Signal doesn't have enough extrema for envelope interpolation."
            )
        mu = 0.5 * (extrema.roll(1) + extrema)
        mu = mu.fill_gaps(dt=sig.dt, method="bfill")
        mu.values[0] = mu.values[1]
        env = 0.5 * abs(extrema.roll(1) - extrema)
        env = env.fill_gaps(dt=sig.dt, method="bfill")
        env.values[0] = env.values[1]
        # smooth local mean and envelope
        window = np.max(np.diff(extrema.time) / sig.dt) // 3
        window = max(3, window + (1 - window % 2))
        for it in range(self.smooth_iter):
            mu = mu.smooth(window, kernel="triangle")
            if np.all(np.diff(mu.values)):
                break
        for it in range(self.smooth_iter):
            env = env.smooth(window, kernel="triangle")
            if np.all(np.diff(env.values)):
                break
        # remove padding
        mu = mu.interp(sig.time)
        env = env.interp(sig.time)
        return mu, env

    def iter(self, sig):
        # Sifts next mode
        is_monotonic = False
        F = sig.copy()
        A = 1.0
        for it in range(self.max_iter):
            try:
                mu, env = self.sift(F)
            except ValueError:
                is_monotonic = True
                break
            F = (F - mu) / env
            A = A * env
            is_pf = np.max(np.abs(F)) - 1.0 < self.eps
            if is_pf:
                break
        F.values[F > 1.0] = 1.0
        F.values[F < -1.0] = -1.0
        return A, F, is_monotonic

    def __call__(self, signal, max_modes=None):
        if not isinstance(signal, TSeries):
            signal = TSeries(values=signal)
        if max_modes is None:
            max_modes = np.inf
        pfs = []
        is_monotonic = signal.size < 4
        residue = signal.copy()
        while not is_monotonic and len(pfs) < max_modes:
            A, F, is_monotonic = self.iter(residue)
            if not is_monotonic:
                pfs.append([A, F])
                residue = residue - A * F
        # Defines useful attributes
        self.signal = signal
        self.modes = pfs
        self.residue = residue
        self.n_modes = len(pfs)
        return self.modes


class VMD(object):
    def __init__(self, alpha, tau, max_modes, DC, init, tol):
        pass

    def __call__(self, signal):
        if len(f) % 2:
            f = f[:-1]
        # Period and sampling frequency of input signal
        fs = 1.0 / len(f)
        ltemp = len(f) // 2
        fMirr = np.append(np.flip(f[:ltemp], axis=0), f)
        fMirr = np.append(fMirr, np.flip(f[-ltemp:], axis=0))
        # Time Domain 0 to T (of mirrored signal)
        T = len(fMirr)
        t = np.arange(1, T + 1) / T
        # Spectral Domain discretization
        freqs = t - 0.5 - (1 / T)
        # Maximum number of iterations (if not converged yet, then it won't anyway)
        Niter = 500
        # For future generalizations: individual alpha for each mode
        Alpha = alpha * np.ones(K)
        # Construct and center f_hat
        f_hat = np.fft.fftshift((np.fft.fft(fMirr)))
        f_hat_plus = np.copy(f_hat)  # copy f_hat
        f_hat_plus[: T // 2] = 0
        # Initialization of omega_k
        omega_plus = np.zeros([Niter, K])
        if init == 1:
            for i in range(K):
                omega_plus[0, i] = (0.5 / K) * (i)
        elif init == 2:
            omega_plus[0, :] = np.sort(
                np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(1, K))
            )
        else:
            omega_plus[0, :] = 0
        # if DC mode imposed, set its omega to 0
        if DC:
            omega_plus[0, 0] = 0
        # start with empty dual variables
        lambda_hat = np.zeros([Niter, len(freqs)], dtype=complex)
        # other inits
        uDiff = tol + np.spacing(1)  # update step
        n = 0  # loop counter
        sum_uk = 0  # accumulator
        # matrix keeping track of every iterant // could be discarded for mem
        u_hat_plus = np.zeros([Niter, len(freqs), K], dtype=complex)
        # *** Main loop for iterative updates***
        while uDiff > tol and n < Niter - 1:  # not converged and below iterations limit
            # update first mode accumulator
            k = 0
            sum_uk = u_hat_plus[n, :, K - 1] + sum_uk - u_hat_plus[n, :, 0]
            # update spectrum of first mode through Wiener filter of residuals
            u_hat_plus[n + 1, :, k] = (f_hat_plus - sum_uk - lambda_hat[n, :] / 2) / (
                1.0 + Alpha[k] * (freqs - omega_plus[n, k]) ** 2
            )
            # update first omega if not held at 0
            if not (DC):
                omega_plus[n + 1, k] = np.dot(
                    freqs[T // 2 : T], (abs(u_hat_plus[n + 1, T // 2 : T, k]) ** 2)
                ) / np.sum(abs(u_hat_plus[n + 1, T // 2 : T, k]) ** 2)
            # update of any other mode
            for k in np.arange(1, K):
                # accumulator
                sum_uk = u_hat_plus[n + 1, :, k - 1] + sum_uk - u_hat_plus[n, :, k]
                # mode spectrum
                u_hat_plus[n + 1, :, k] = (
                    f_hat_plus - sum_uk - lambda_hat[n, :] / 2
                ) / (1 + Alpha[k] * (freqs - omega_plus[n, k]) ** 2)
                # center frequencies
                omega_plus[n + 1, k] = np.dot(
                    freqs[T // 2 : T], (abs(u_hat_plus[n + 1, T // 2 : T, k]) ** 2)
                ) / np.sum(abs(u_hat_plus[n + 1, T // 2 : T, k]) ** 2)
            # Dual ascent
            lambda_hat[n + 1, :] = lambda_hat[n, :] + tau * (
                np.sum(u_hat_plus[n + 1, :, :], axis=1) - f_hat_plus
            )
            # loop counter
            n = n + 1
            # converged yet?
            uDiff = np.spacing(1)
            for i in range(K):
                uDiff = uDiff + (1 / T) * np.dot(
                    (u_hat_plus[n, :, i] - u_hat_plus[n - 1, :, i]),
                    np.conj((u_hat_plus[n, :, i] - u_hat_plus[n - 1, :, i])),
                )
            uDiff = np.abs(uDiff)
        # Postprocessing and cleanup
        # discard empty space if converged early
        Niter = np.min([Niter, n])
        omega = omega_plus[:Niter, :]
        idxs = np.flip(np.arange(1, T // 2 + 1), axis=0)
        # Signal reconstruction
        u_hat = np.zeros([T, K], dtype=complex)
        u_hat[T // 2 : T, :] = u_hat_plus[Niter - 1, T // 2 : T, :]
        u_hat[idxs, :] = np.conj(u_hat_plus[Niter - 1, T // 2 : T, :])
        u_hat[0, :] = np.conj(u_hat[-1, :])
        u = np.zeros([K, len(t)])
        for k in range(K):
            u[k, :] = np.real(np.fft.ifft(np.fft.ifftshift(u_hat[:, k])))
        # remove mirror part
        u = u[:, T // 4 : 3 * T // 4]
        # recompute spectrum
        u_hat = np.zeros([u.shape[1], K], dtype=complex)
        for k in range(K):
            u_hat[:, k] = np.fft.fftshift(np.fft.fft(u[k, :]))
        return u, u_hat, omega


class SSA(object):
    def __init__(self, L):
        self.L = L

    def __call__(self, signal):
        """
        Decomposes the given time series with a singular-spectrum analysis. Assumes the values of the time series are
        recorded at equal intervals.

        Parameters
        ----------
        tseries : The original time series, in the form of a Pandas Series, NumPy array or list.
        L : The window length. Must be an integer 2 <= L <= N/2, where N is the length of the time series.
        save_mem : Conserve memory by not retaining the elementary matrices. Recommended for long time series with
            thousands of values. Defaults to True.

        Note: Even if an NumPy array or list is used for the initial time series, all time series returned will be
        in the form of a Pandas Series or DataFrame object.
        """

        # Tedious type-checking for the initial time series
        if not isinstance(signal, TSeries):
            signal = TSeries(values=signal)

        # Checks to save us from ourselves
        self.N = len(signal)
        if not 2 <= self.L <= self.N / 2:
            raise ValueError("The window length must be in the interval [2, N/2].")

        self.orig_TS = signal.copy()
        self.K = self.N - self.L + 1

        # Embed the time series in a trajectory matrix
        self.X = np.array(
            [self.orig_TS.values[i : self.L + i] for i in range(0, self.K)]
        ).T

        # Decompose the trajectory matrix
        self.U, self.Sigma, VT = np.linalg.svd(self.X)
        self.d = np.linalg.matrix_rank(self.X)

        self.TS_comps = np.zeros((self.N, self.d))

        # Reconstruct the elementary matrices without storing them
        for i in range(self.d):
            X_elem = self.Sigma[i] * np.outer(self.U[:, i], VT[i, :])
            X_rev = X_elem[::-1]
            self.TS_comps[:, i] = [
                X_rev.diagonal(j).mean()
                for j in range(-X_rev.shape[0] + 1, X_rev.shape[1])
            ]

        # Calculate the w-correlation matrix.
        self.calc_wcorr()

    def reconstruct(self, indices):
        """
        Reconstructs the time series from its elementary components, using the given indices. Returns a Pandas Series
        object with the reconstructed time series.

        Parameters
        ----------
        indices: An integer, list of integers or slice(n,m) object, representing the elementary components to sum.
        """
        if isinstance(indices, int):
            indices = [indices]

        ts_vals = self.TS_comps[:, indices].sum(axis=1)
        return TSeries(time=self.orig_TS.time, values=ts_vals)

    def calc_wcorr(self):
        """
        Calculates the w-correlation matrix for the time series.
        """

        # Calculate the weights
        w = np.array(
            list(np.arange(self.L) + 1)
            + [self.L] * (self.K - self.L - 1)
            + list(np.arange(self.L) + 1)[::-1]
        )

        def w_inner(F_i, F_j):
            return w.dot(F_i * F_j)

        # Calculated weighted norms, ||F_i||_w, then invert.
        F_wnorms = np.array(
            [w_inner(self.TS_comps[:, i], self.TS_comps[:, i]) for i in range(self.d)]
        )
        F_wnorms = F_wnorms**-0.5

        # Calculate Wcorr.
        self.Wcorr = np.identity(self.d)
        for i in range(self.d):
            for j in range(i + 1, self.d):
                self.Wcorr[i, j] = abs(
                    w_inner(self.TS_comps[:, i], self.TS_comps[:, j])
                    * F_wnorms[i]
                    * F_wnorms[j]
                )
                self.Wcorr[j, i] = self.Wcorr[i, j]

    # def plot_wcorr(self, min=None, max=None):
    #     """
    #     Plots the w-correlation matrix for the decomposed time series.
    #     """
    #     if min is None:
    #         min = 0
    #     if max is None:
    #         max = self.d

    #     if self.Wcorr is None:
    #         self.calc_wcorr()

    #     ax = plt.imshow(self.Wcorr)
    #     plt.xlabel(r"$\tilde{F}_i$")
    #     plt.ylabel(r"$\tilde{F}_j$")
    #     plt.colorbar(ax.colorbar, fraction=0.045)
    #     ax.colorbar.set_label("$W_{i,j}$")
    #     plt.clim(0, 1)

    #     # For plotting purposes:
    #     if max == self.d:
    #         max_rnge = self.d - 1
    #     else:
    #         max_rnge = max

    #     plt.xlim(min - 0.5, max_rnge + 0.5)
    #     plt.ylim(max_rnge + 0.5, min - 0.5)


class CEEMDAN(object):
    def __init__(
        self,
        epsilon=0.2,
        ensemble_size=50,
        min_energy=0.0,
        random_seed=None,
        cores=None,
        **kwargs,
    ):
        """Complete Ensemble Empirical Mode Decomposition with Adaptive Noise

        Parameters
        ----------
        max_modes: int, optional
            If given, stops the decomposition after this number of modes.
        epsilon: float, optional
            Normalized standard deviation of the added Gaussian noise (the default is 0.2).
        ensemble_size: int, optional
            Number of realizations averaged for each IMF (the default is 50).
        min_energy: float, optional
            Stopping criterium for the energy contribution of the residue.
        random_seed: int, optional
            Seed for generating random numbers, useful for reproducibility of results.

        References
        ----------
        .. [#] M. Colominas, G. Schlotthauer, M. Torres, "Improved complete
        ensemble EMD: A suitable tool for biomedical signal processing,"
        Biomedical Signal Processing and Control, 2014.
        .. [#] M. Torres, M. Colominas, G. Schlotthauer, P. Flandrin, "A Complete
        Ensemble Empirical Mode Decomposition with Adaptive Noise," 36th
        International Conference on Acoustics, Speech and Signal Processing
        ICASSP, 2011.
        """
        self.epsilon = epsilon
        self.ensemble_size = ensemble_size
        self.min_energy = min_energy
        self.cores = cores
        self.emd = EMD(**kwargs)
        self.rng = np.random.default_rng(random_seed)

    def _realization(self, task):
        noise_modes, k, residue = task
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

    def __call__(self, signal, max_modes=None, progress=False):
        if not isinstance(signal, TSeries):
            signal = TSeries(values=signal)
        if max_modes is None:
            max_modes = np.inf
        sigma_x = np.std(signal)

        # Creates the noise realizations
        white_noise_modes = []
        if self.cores is not None:
            with Pool(self.cores) as pool:
                white_noise = [
                    TSeries(signal.time, self.rng.standard_normal(signal.size))
                    for i in range(self.ensemble_size)
                ]
                white_noise_modes = pool.map(self.emd, white_noise)
                if progress:
                    print("White noise: done")
        else:
            if progress:
                ensemble = trange(self.ensemble_size, desc="White noise", leave=True)
            else:
                ensemble = range(self.ensemble_size)
            for i in ensemble:
                white_noise = TSeries(
                    signal.time, self.rng.standard_normal(signal.size)
                )
                white_noise_modes.append(self.emd(white_noise))

        imfs = []
        residue = signal / sigma_x
        while len(imfs) < max_modes:
            k = len(imfs)

            # Averages the ensemble of trials for the next mode
            mu = 0
            if self.cores is not None:
                with Pool(self.cores) as pool:
                    tasks = [
                        (noise_modes, k, residue) for noise_modes in white_noise_modes
                    ]
                    mus = pool.map(self._realization, tasks)
                mu = sum(mus) / self.ensemble_size
                if progress:
                    print(f"Mode #{k+1}: done")
            else:
                if progress:
                    ensemble = trange(
                        self.ensemble_size, desc=f"Mode #{k+1}", leave=True
                    )
                for i in ensemble:
                    noise_modes = white_noise_modes[i]
                    mu = mu + (
                        self._realization((noise_modes, k, residue))
                        / self.ensemble_size
                    )
            imfs.append(residue - mu)
            residue = mu.copy()

            # Checks stopping criteria (if the residue is an IMF or too small)
            if np.var(residue) < self.min_energy:
                break
            residue_imfs = self.emd(residue)
            if len(residue_imfs) <= 1:
                if len(imfs) < max_modes and len(residue_imfs) == 1:
                    imfs.append(residue_imfs[0])
                break

        # Undoes the initial normalization
        for i in range(len(imfs)):
            imfs[i] *= sigma_x
        self.signal = signal
        self.modes = imfs
        self.residue = signal - sum(imfs)
        self.n_modes = len(imfs)
        return self.modes

    def postprocessing(self):
        ck = self.emd(self.modes[0], max_modes=1)[0]
        c_imfs = [ck]
        qk = self.modes[0] - ck
        for k in range(1, self.n_modes):
            Dk = qk + self.modes[k]
            modes = self.emd(Dk, max_modes=1)
            if len(modes) > 0:
                ck = modes[0]
            else:
                c_imfs.append(self.modes[k])
                break
            qk = Dk - ck
            c_imfs.append(ck)
        self.c_residue = sum(self.modes) + self.residue - sum(c_imfs)
        self.c_modes = c_imfs

    @property
    def orthogonality_matrix(self):
        orth = np.zeros((self.n_modes, self.n_modes), float)
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                orth[i, j] = self.imfs[i].corr(self.imfs[j])
        return orth

    @property
    def c_orthogonality_matrix(self):
        orth = np.zeros((len(self.c_modes), len(self.c_modes)), float)
        for i in range(len(self.c_modes)):
            for j in range(len(self.c_modes)):
                orth[i, j] = self.c_modes[i].corr(self.c_modes[j])
        return orth
