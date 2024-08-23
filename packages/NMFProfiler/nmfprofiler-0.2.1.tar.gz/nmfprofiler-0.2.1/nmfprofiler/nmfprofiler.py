"""NMFProfiler: A multi-omics integration method for samples stratified in
groups
"""

# Authors: Aurelie Mercadie
#          Eleonore Gravier
#          Gwendal Josse
#          Nathalie Vialaneix https://nathalievialaneix.eu
#          Celine Brouard https://miat.inrae.fr/brouard/
# License: GPL-3

from copy import deepcopy

import warnings
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
from numpy import divide, multiply, newaxis
from numpy.linalg import norm, multi_dot
import pandas as pd

from sklearn.decomposition._nmf import _initialize_nmf
from sklearn.utils.extmath import safe_sparse_dot
from sklearn.preprocessing import OneHotEncoder
from sklearn.exceptions import ConvergenceWarning

import statsmodels.api as sm

from time import process_time  # closest to elapsed time from system.time() (R)

from .utils.validate_inputs import _check_inputs_NMFProfiler


def _prox_l1_pos(v, lambd):
    """Proximal operator of l1 norm (lasso) + positivity constraint."""
    return np.maximum(v - lambd, 0)


def _update_W(W, omic1, omic2, H1, H2, mu):
    """Update the matrix containing contributions of individuals to latent
    components.

    Parameters
    ----------
    :W: ndarray of shape (n_samples x K), contributions of individuals
        to latent components.
    :omic1: ndarray of shape (n_samples x n_features_omic1), values of
        features from (omic1) measured on (n_samples).
    :omic2: ndarray of shape (n_samples x n_features_omic2), values of
        features from (omic2) measured on the same (n_samples) samples as
        (omic1).
    :H1: ndarray of shape (K x n_features_omic1), latent components
        built on (omic1).
    :H2: ndarray of shape (K x n_features_omic2), latent components built on
        (omic2).
    :mu: float, value for parameter `mu` from objective function.


    Returns
    -------
    Newly updated W.
    """
    B = (
        safe_sparse_dot(H1, H1.T)
        + safe_sparse_dot(H2, H2.T)
        + (mu * np.identity(W.shape[1]))
    )
    C = safe_sparse_dot(omic1, H1.T) + safe_sparse_dot(omic2, H2.T)

    return multiply(W, divide(C, safe_sparse_dot(W, B)))


def _update_H(
    H,
    W,
    omic,
    Beta,
    Y,
    gamma,
    eta,
    lambdA,
    as_sklearn,
    grad=False,
    H_grad=None
):
    """Update the matrix containing latent components built on omic j.
       (j referring to the omic dataset number, either 1 or 2)

    Parameters
    ----------
    :H: ndarray of shape (K x n_features_omicj), latent components built on
        omic j.
    :W: ndarray of shape (n_samples x K), contributions of individuals to
        latent components.
    :omic: ndarray of shape (n_samples x n_features_omicj), values of
        features from omic j measured on (n_samples).
    :Beta: ndarray of shape (K x 1), regression coefficients for projection
        of individuals from omic j onto latent components from H^(j).
    :Y: ndarray of shape (n_samples x U), one-hot encoding of (y) indicating
        to which group each sample belongs.
    :gamma: float, nonnegative value for parameter `gamma` from objective
        function.
    :eta: float, nonnegative value for parameter `eta` from prox.
    :lambdA: float, nonnegative value for parameter `lambda` from objective
        function.
    :as_sklearn: boolean, whether or not a modified version of the MU updates
        from scikit-learn is used.
    :grad: boolean, compute gradient or not. By default, grad = False.
    :H_grad: list, gradient values of H^(j) matrix. By default, H_grad = None.


    Returns
    -------
    Newly updated H^(j).


    Note
    ----
    A part of this function is strongly based on Multiplicative Updates
    implemented in sklearn.decomposition.NMF.
    """
    R = safe_sparse_dot(W.T, omic) + (
        gamma * multi_dot([np.diag(Beta), Y.T, omic])
    )  # R (Prox) or numerator (MU)
    D = multi_dot([W.T, W, H]) + (
        gamma * multi_dot([np.diag(Beta**2), H, omic.T, omic])
    )  # D (Prox) or denominator (MU)

    # Compute gradient before updates
    if grad:
        H_grad.append(D - R)

    if as_sklearn:
        EPSILON = np.finfo(np.float32).eps

        # Add L1 regularization
        if lambdA > 0:
            D += lambdA

        # Introduce small value to avoid definition problems
        D[D == 0] = EPSILON

        delta_H = R
        delta_H /= D
        H *= delta_H

    else:
        H_tilde = H + (1 / eta) * (R - D)
        H = _prox_l1_pos(H_tilde, lambdA / eta)

    return [H, H_grad] if grad else H


def _update_Beta(omic, h_k, y_k, gamma, Beta):
    """Update the regression coefficients linked to omic j and component k.
    (j referring to the omic dataset number, either 1 or 2)

    Parameters
    ----------
    :omic: ndarray of shape (n_samples x n_features_omicj), values of
        features from omic j measured on (n_samples).
    :h_k: ndarray of length (n_features_omicj), contains latent component k
        built on omic j (row k of H^(j)).
    :y_k: ndarray of length (n_samples), contains binary labels regarding
        group k (column k of Y).
    :gamma: float, value for parameter `gamma` from objective function.
    :Beta: float, regression coefficient for projection of individuals from
        omic j onto latent components from H^(j).


    Returns
    -------
    Newly updated scalar Beta_k^(j).
    """
    if gamma > 0:

        h_k = h_k[newaxis]  # 1 component x p_j features
        y_k = np.transpose(y_k[newaxis])  # n samples x 1 group

        u_numerator = np.squeeze(
            multi_dot([h_k, omic.T, y_k])
        )  # np.squeeze to reduce to a 0d array
        u_denominator = np.squeeze(
            multi_dot([h_k, omic.T, omic, np.transpose(h_k)])
        )  # np.squeeze to reduce to a 0d array

        Beta = divide(u_numerator, u_denominator)

    return Beta


def _computeF(
    omic1,
    omic2,
    Y,
    W,
    H1,
    H2,
    Beta1,
    Beta2,
    mu,
    lambdA,
    gamma,
    K_gp,
    details=False
):
    """Compute the value of F given omic1, omic2, Y, W, H1, H2, Beta1, Beta2
    and some hyperparameters (i.e. gamma, lambda and mu).

    Calculate the objective function value, as well as each error term,
    in order to monitor progress of algorithm convergence.

    Parameters
    ----------
    :omic1: ndarray of shape (n_samples x n_features_omic1), values of
        features from (omic1) measured on (n_samples).
    :omic2: ndarray of shape (n_samples x n_features_omic2), values of
        features from (omic2) measured on the same (n_samples) samples
        as (omic1).
    :Y: ndarray of shape (n_samples x U), one-hot encoding of (y) indicating
        to which group each sample belongs.
    :W: ndarray of shape (n_samples x K), contributions of individuals to
        latent components.
    :H1: ndarray of shape (K x n_features_omic1), latent components built on
        (omic1).
    :H2: ndarray of shape (K x n_features_omic2), latent components built on
        (omic2).
    :Beta1: ndarray of shape (K x 1), regression coefficients for projection
        of individuals from (omic1) onto latent components from H^(1).
    :Beta2: ndarray of shape (K x 1), regression coefficients for projection
        of individuals from (omic2) onto latent components from H^(2).
    :mu: float, value for parameter `mu` from objective function.
    :lambdA: float, value for parameter `lambda` from objective function.
    :gamma: float, value for parameter `gamma` from objective function.
    :K_gp: int, number of components dedicated to groups profiling.
    :details: boolean, whether or not all specific error terms are displayed
        to the user. By default, details = False.


    Returns
    -------
    Either the value of the objective function (i.e. the global loss) alone,
    or accompagned by each specific term to obtain it.
    """
    distort1 = 0.5 * (norm(omic1 - safe_sparse_dot(W, H1)) ** 2)
    distort2 = 0.5 * (norm(omic2 - safe_sparse_dot(W, H2)) ** 2)
    regul = (mu / 2) * np.trace(safe_sparse_dot(W.T, W))
    sparse1 = lambdA * norm(H1, 1)
    sparse2 = lambdA * norm(H2, 1)
    pred1 = (gamma / 2) * (
        norm(Y - multi_dot([omic1, H1.T[:, 0:K_gp],
                            np.diag(Beta1[0:K_gp])])) ** 2
    )
    pred2 = (gamma / 2) * (
        norm(Y - multi_dot([omic2, H2.T[:, 0:K_gp],
                            np.diag(Beta2[0:K_gp])])) ** 2
    )

    loss = distort1 + distort2 + regul + sparse1 + sparse2 + pred1 + pred2

    if details:
        res = [loss, distort1, distort2, sparse1, sparse2, regul, pred1, pred2]

    return loss if details is False else res


def _computeMargH(omic, Y, W, H, Beta, gamma, lambdA, K_gp):
    """Compute the marginal loss of H^(j).

    Calculate the marginal of the objective function in H^(j) to perform
    Backtrack LineSearch and optimize the value of the gradient descent step
    size eta^(j).

    Parameters
    ----------
    :omic: ndarray of shape (n_samples x n_features_omicj), values of
        features from omic j measured on (n_samples).
    :Y: ndarray of shape (n_samples x U), one-hot encoding of (y) indicating
        to which group each sample belongs.
    :W: ndarray of shape (n_samples x K), contributions of individuals to
        latent components.
    :H: ndarray of shape (K x n_features_omicj), latent components built on
        omic j.
    :Beta: ndarray of shape (K x 1), regression coefficients for projection
        of individuals from omic j onto latent components from H^(j).
    :gamma: float, value for parameters `gamma` from objective function.
    :lambdA: float, value for parameter `lambda` from objective function.
    :K_gp: int, number of components dedicated to groups profiling.


    Returns
    -------
    Value of the marginal loss for H^(j).
    """
    part1 = 0.5 * np.trace(multi_dot([H.T, W.T, W, H]))
    part2 = np.trace(multi_dot([H.T, W.T, omic]))
    part3 = (gamma / 2) * np.trace(
        multi_dot(
            [np.diag(Beta[0:K_gp] ** 2), H[0:K_gp, :],
             omic.T, omic, H.T[:, 0:K_gp]]
        )
    )
    part4 = gamma * np.trace(
        multi_dot([np.diag(Beta[0:K_gp]), H[0:K_gp, :], omic.T, Y])
    )
    part5 = lambdA * norm(H, 1)

    res = part1 - part2 + part3 - part4 + part5

    return res


def _linesearch(
    H_old,
    H,
    W,
    omic,
    Beta,
    Y,
    gamma,
    lambdA,
    current_eta,
    H_loss,
    alpha,
    sigma,
    m_back,
    max_iter_back,
    K_gp,
    verbose,
):
    """Find the most suited value for eta^(j).

    Calculate the optimal gradient descent step size eta^(j) to update H^(j)
    (j = 1,2).
    Instead of reuse each time the initial eta_0^(j), use the last one found,
    eta_(t-1)^(j).

    Parameters
    ----------
    :H_old: ndarray of shape (K x n_features_omicj), latent components built
        on omic j at t-1 (or t).
    :H: ndarray of shape (K x n_features_omicj), latent components built
        on omic j at t (or t+1).
    :W: ndarray of shape (n_samples x K), contributions of individuals to
        latent components.
    :omic: ndarray of shape (n_samples x n_features_omicj), values of
        features from omic j measured on (n_samples).
    :Beta: ndarray of shape (K x 1), regression coefficients for projection
        of individuals from omic j onto latent components from H^(j).
    :Y: ndarray of shape (n_samples x U), one-hot encoding of (y) indicating
        to which group each sample belongs.
    :gamma: float, value for parameters `gamma` from objective function.
    :lambdA: float, value for parameter `lambda` from objective function.
    :current_eta: float, last optimal value for parameter `eta` from proximal.
    :H_loss: list, values of the marginal loss in H.
    :alpha: float, factor by which multiplying eta^(j).
    :sigma: float, parameter needed in thr_back computation.
    :m_back: int, marginal loss historic looked at when optimizing eta^(j).
    :max_iter_back: int, maximum number of iterations for the backtrack.
    :K_gp: int, number of components dedicated to groups profiling.
    :verbose: boolean, whether or not to print algorithm progress.


    Returns
    -------
    :H: ndarray of shape (K x n_features_omicj), newly updated H^(j).
    :H_loss: list, updated with last marginal loss for H^(j).
    :current_eta: float, optimal value for eta^(j) chosen during linesearch.
    """

    # Initialize iteration
    it = 0

    # Compute the threshold under which the update of eta will stop
    thr_back = np.max(
        [
            H_loss[-2 - k] - (sigma / 2 * current_eta * norm(H - H_old) ** 2)
            for k in range(min(m_back, len(H_loss) - 1))
        ]
    )

    # Backtrack LineSearch
    while H_loss[-1] > thr_back and it < max_iter_back:
        current_eta *= alpha
        H = _update_H(
            H_old,
            W,
            omic,
            Beta,
            Y,
            gamma,
            current_eta,
            lambdA,
            as_sklearn=False
        )
        H_loss[-1] = _computeMargH(omic, Y, W, H, Beta, gamma, lambdA, K_gp)
        thr_back = np.max(
            [
                H_loss[-2 - k] - (
                    sigma / 2 * current_eta * norm(H - H_old) ** 2
                )
                for k in range(min(m_back, len(H_loss) - 1))
            ]
        )
        it += 1

    if it == max_iter_back and verbose:
        print("Warning: backtrack failed")

    return H, H_loss, current_eta


def _analytic_solver(
    omic1,
    omic2,
    Y,
    W,
    H1,
    H2,
    Beta1,
    Beta2,
    params,
    as_sklearn,
    backtrack,
    max_iter_back,
    H1_loss,
    H2_loss,
    H1_grad,
    H2_grad,
    K,
    K_gp,
    verbose,
):
    """Solver for NMFProfiler.

    This solver is based on analytic forms of gradients computed by hand.
    It has been adapted from both solvers in sklearn.decomposition.NMF and
    the one proposed by Fernsel and Maass (2018).


    Parameters
    ----------
    :omic1: ndarray of shape (n_samples x n_features_omic1), values of
        features from (omic1) measured on (n_samples).
    :omic2: ndarray of shape (n_samples x n_features_omic2), values of
        features from (omic2) measured on the same (n_samples) samples as
        (omic1).
    :Y: ndarray of shape (n_samples x U), one-hot encoding of (y) indicating
        to which group each sample belongs.
    :W: ndarray of shape (n_samples x K), contributions of individuals to
        latent components, initialized or at (t).
    :H1: ndarray of shape (K x n_features_omic1), latent components built on
        (omic1), initialized or at (t).
    :H2: ndarray of shape (K x n_features_omic2), latent components built on
        (omic2), initialized or at (t).
    :Beta1: ndarray of shape (K x 1), regression coefficients for projection
        of individuals from (omic1) onto (H1), initialized or at (t).
    :Beta2: ndarray of shape (K x 1), regression coefficients for projection
        of individuals from (omic2) onto (H2), initialized or at (t).
    :params: dict of length 8 (optional), values for parameters `gamma`,
        `lambda`, `mu` from objective function, `eta1`, `eta2` for prox, and
        `alpha`, `sigma`, `m_back` for linesearch().
        By default, gamma = 0.005, lambda = 1e-3, mu = 1e-3, eta1 = eta2 = 1,
        alpha = 2, sigma = 1e-9 and m_back = 1.
    :as_sklearn: boolean, whether or not a modified version of the MU updates
        from scikit-learn is used.
    :backtrack: boolean, if Backtrack LineSearch is performed or not.
    :max_iter_back: int, maximum number of iterations for the backtrack.
    :H1_loss: list, values of the marginal loss for H^(1).
    :H2_loss: list, values of the marginal loss for H^(2).
    :H1_grad: list, values of gradient in H^(1) (before update).
    :H2_grad: list, values of gradient in H^(2) (before update).
    :K: int (optional), number of latent components to build.
        By default, K = 2.
    :K_gp: int, number of components dedicated to groups profiling.
    :verbose: boolean, whether or not to print algorithm progress.


    Returns
    -------
    :W_new: ndarray of shape (n_samples x K), updated, or (t+1), W matrix.
    :H1_new: ndarray of shape (K x n_features_omic1), updated, or (t+1),
        H1 matrix.
    :H2_new: ndarray of shape (K x n_features_omic2), updated, or (t+1),
        H2 matrix.
    :Beta1_new: vector of length (K), updated, or (t+1), Beta1 vector.
    :Beta2_new: vector of length (K), updated, or (t+1), Beta2 vector.
    :params[`eta1`]: float, updated value of parameter `eta1`.
    :params[`eta2`]: float, updated value of parameter `eta2`.
    :H1_loss: list, augmented list of marginal losses for H^(1).
    :H2_loss: list, augmented list of marginal losses for H^(2).
    :H1_grad: list, augmented list of gradient values in H^(1)
        (before update).
    :H2_grad: list, augmented list of gradient values in H^(2)
        (before update).


    Note
    ----
    See (Fevotte, 2011) and sklearn.decomposition.NMF source code for
    choice of parameters.
    """

    # W update with new values of Hs
    W_new = _update_W(W, omic1, omic2, H1, H2, params["mu"])

    # Hs updates (either MU or Proximal)
    H1_new, H1_grad = _update_H(
        H1,
        W_new,
        omic1,
        Beta1,
        Y,
        params["gamma"],
        params["eta1"],
        params["lambda"],
        as_sklearn=as_sklearn,
        grad=True,
        H_grad=H1_grad,
    )
    H2_new, H2_grad = _update_H(
        H2,
        W_new,
        omic2,
        Beta2,
        Y,
        params["gamma"],
        params["eta2"],
        params["lambda"],
        as_sklearn=as_sklearn,
        grad=True,
        H_grad=H2_grad,
    )

    if backtrack and not as_sklearn:
        # LineSearch for H1
        H1_loss.append(
            _computeMargH(
                omic1,
                Y,
                W_new,
                H1_new,
                Beta1,
                params["gamma"],
                params["lambda"],
                K_gp
            )
        )
        H1_new, H1_loss, params["eta1"] = _linesearch(
            H_old=H1,
            H=H1_new,
            W=W_new,
            omic=omic1,
            Beta=Beta1,
            Y=Y,
            gamma=params["gamma"],
            lambdA=params["lambda"],
            current_eta=params["eta1"],
            H_loss=H1_loss,
            alpha=params["alpha"],
            sigma=params["sigma"],
            m_back=params["m_back"],
            max_iter_back=max_iter_back,
            K_gp=K_gp,
            verbose=verbose,
        )
        # LineSearch for H2
        H2_loss.append(
            _computeMargH(
                omic2,
                Y,
                W_new,
                H2_new,
                Beta2,
                params["gamma"],
                params["lambda"],
                K_gp
            )
        )
        H2_new, H2_loss, params["eta2"] = _linesearch(
            H_old=H2,
            H=H2_new,
            W=W_new,
            omic=omic2,
            Beta=Beta2,
            Y=Y,
            gamma=params["gamma"],
            lambdA=params["lambda"],
            current_eta=params["eta2"],
            H_loss=H2_loss,
            alpha=params["alpha"],
            sigma=params["sigma"],
            m_back=params["m_back"],
            max_iter_back=max_iter_back,
            K_gp=K_gp,
            verbose=verbose,
        )

    # Betas updates with new values of Hs
    # Compute each regression coef. of each component separately
    # and gather them in a unique vector
    Beta1_new = np.array(
        [
            _update_Beta(
                omic1, H1_new[0, :], Y[:, 0], params["gamma"], Beta1[0]
            ),
            _update_Beta(
                omic1, H1_new[1, :], Y[:, 1], params["gamma"], Beta1[1]
            ),
        ]
    )

    Beta2_new = np.array(
        [
            _update_Beta(
                omic2, H2_new[0, :], Y[:, 0], params["gamma"], Beta2[0]
            ),
            _update_Beta(
                omic2, H2_new[1, :], Y[:, 1], params["gamma"], Beta2[1]
            ),
        ]
    )

    # Put to zero all coefficients linked to components k when k > K_gp
    if K_gp < K:
        Beta1_new[K_gp:] = 0
        Beta2_new[K_gp:] = 0

    return (
        W_new,
        H1_new,
        H2_new,
        Beta1_new,
        Beta2_new,
        params["eta1"],
        params["eta2"],
        H1_loss,
        H2_loss,
        H1_grad,
        H2_grad,
    )


def _autograd_solver():
    """Another version of NMFProfiler solver.

    This solver is based on gradients automatically computed thanks to
    `autograd` python library.

    Note this feature has not been implemented so far.
    """
    raise Exception(
        "Feature not implemented yet. Please use 'analytical' solver."
    )


class NMFProfiler:
    r"""A multi-omics integration method for samples stratified in groups

    The goal of the method is to find relationships between OMICS
    corresponding to typical profiles of distinct groups of individuals. The
    objective is to find two decompositions, one for each omic, with a common
    contribution of individuals, in which latent factor matrices are sparse.

    The objective function
    :math:`\mathcal{F}
    (\mathbf{W},\mathbf{H}^{(1)},\mathbf{H}^{(2)},\beta^{(1)},\beta^{(2)})`
    is as follows:

    .. math::

        & \dfrac{1}{2}\left( \sum_{j=1}^2\| \mathbf{X}^{(j)} -
        \mathbf{WH}^{(j)} \|_F^2 \right)

        &+ \dfrac{\gamma}{2}\left( \sum_{j=1}^2\| \mathbf{Y} -
        \mathbf{X}^{(j)} \mathbf{H}^{(j)\top} \text{Diag}(\beta^{(j)})
        \|_F^2 \right)

        &+ \sum_{j=1}^{2} \lambda\|\mathbf{H}^{(j)}\|_1 +
        \dfrac{\mu}{2}\|\mathbf{W \|_F^2}

    Parameters
    ----------
    :omic1: array-like of shape (n_samples x n_features_omic1).
        First omics dataset. (n_samples) is the number of samples and
        (n_features_omic1) the number of features.

    :omic2: array-like of shape (n_samples x n_features_omic2).
        Second omics dataset. (n_samples) is the number of samples and
        (n_features_omic2) is the number of features.
        WARNING: (omic2) must contain the exact same samples in the same order
        as (omic1).

    :y: vector of length (n_samples).
        Group to which each sample belongs (same order than the rows of omic1
        and omic2).

    :params: dict of length 8, optional.
        Contains, in this order, values for hyperparameters `gamma`, `lambda`,
        `mu` (from the objective function), for `eta1`, `eta2` (when proximal
        optimization is used), and for `alpha`, `sigma`, `m_back` (for
        `linesearch()`).
        By default, gamma = 1e-2, lambda = 1e-3, mu = 1e-3, eta1 = eta2 = 1,
        alpha = 2, sigma = 1e-9, and m_back = 1. In the objective function,
        `lambda` and `gamma` are additionally multiplied by (n_samples).

    :init_method: str, optional.
        Initialization method. One of {`'random2'`, `'random3'`, `'nndsvd2'`,
        `'nndsvd3s'`, `'nndsvd'`, `'nndsvda'`, `'nndsvdar'`}. Initializations
        are base on the `_initialize_nmf` function of the
        `sklearn.decomposition.NMF` module.
        In addition, for `'random2'` and `'random3'`, values are drawn
        from a standard Normal distribution (with 0 mean and standard deviation
        equal to 1).
        By default, `init_method = 'random2'`.
        See `_initialize_nmf()` for further information.

    :solver: str, optional.
        Solver type for the optimization problem. One of `'analytical'`
        (analytical differentiation) or `'autograd'` (automatic
        differentiation). Note the latter solver is not implemented in
        the current version, but should be released in future versions.
        By default, `solver = 'analytical'`.

    :as_sklearn: boolean, optional.
        If `True`, the solver uses MU updates. If `False`, it uses a proximal
        optimization strategy.
        By default, `as_sklearn = True`.

    :backtrack: boolean, optional.
        When `as_sklearn = False`, whether or not to perform Backtrack
        LineSearch.
        By default, `backtrack = False`.

    :max_iter_back: int, optional.
        When `max_iter_back = True`, maximum number of iterations for the
        Backtrack LineSearch.
        By default, `max_iter_back = 100`.

    :tol: float, optional.
        Tolerance for the stopping condition.
        By default, `tol = 1e-4`.

    :max_iter: int, optional.
        Maximum number of allowed iterations.
        By default, `max_iter = 1000`.

    :seed: int, optional.
        Random seed to ensure reproducibility of results.
        By default, seed = None.

    :verbose: boolean, optional.
        Verbose optimization process.
        By default, `verbose = False`.


    Attributes
    ----------
    :W: ndarray of shape (n_samples x 2).
        Contributions of individuals in each latent component.

    :W_init: ndarray of shape (n_samples x 2).
        Initial version of (W).

    :H1: ndarray of shape (2 x n_features_omic1).
        Latent components for (omic1).

    :H1_init: ndarray of shape (2 x n_features_omic1).
        Initial version of (H1).

    :H2: ndarray of shape (2 x n_features_omic2).
        Latent components for (omic2).

    :H2_init: ndarray of shape (2 x n_features_omic2).
        Initial version of (H2).

    :Beta1: ndarray of shape (2 x 1).
        Regression coefficients for the projection of individuals from (omic1)
        onto (H1).

    :Beta1_init: ndarray of shape (2 x 1).
        Initial version of (Beta1).

    :Beta2: ndarray of shape (K x 1).
        Regression coefficients for the projection of individuals from (omic2)
        onto (H2).

    :Beta2_init: ndarray of shape (K x 1).
        Initial version of (Beta2).

    :n_iter: int.
        Final number of iterations (up to convergence or maximum number of
        iterations is reached).

    :df_etas: `pd.dataFrame` of shape (n_iter+1, 2).
        Optimal values for parameters `eta1` and `eta2` at each iteration.

    :df_errors: `pd.dataFrame` of shape (n_iter+1, 9).
        All error terms for each iteration and omic j.

    :df_ldaperf: `pd.DataFrame` of shape (n_iter+1, 13).
        All metrics linked to LDA at each iteration and omic j.

    :df_grads: `pd.DataFrame` of shape (n_iter+1, 2)
        Values of H^(1) and H^(2) gradients before being updated, at each
        iteration.

    :runningtime: float.
        Running time of the method measured through `process_time()`.

    ... : all inputs passed to `NMFProfiler()`.


    References
    ----------
    C. Boutsidis and E. Gallopoulos. SVD based initialization: A head
    start for nonnegative matrix factorization. Pattern Recognition.
    Volume 41, Issue 4. 2008. Pages 1350-1362.
    https://doi.org/10.1016/j.patcog.2007.09.010.

    J. Leuschner, M. Schmidt, P. Fernsel, D. Lachmund, T. Boskamp, and
    P. Maass. Supervised non-negative matrix factorization methods for
    MALDI imaging applications. Bioinformatics.
    Volume 35. 2019. Pages 1940-1947
    https://doi.org/10.1093/bioinformatics/bty909.

    S. Zhang, C.-C. Liu, W. Li, H. Shen, P. W. Laird, and X. J. Zhou.
    Discovery of multi-dimensional modules by integrative analysis of
    cancer genomic data. Nucleic acids research.
    Volume 40, Issue 19. 2012. Pages 9379-9391.
    https://doi.org/10.1093/nar/gks725.

    A. Mercadie, E. Gravier, G. Josse, N. Vialaneix, and C. Brouard.
    NMFProfiler: A multi-omics integration method for samples stratified in
    groups. Preprint submitted for publication.

    Examples
    --------

    >>> import numpy as np
    >>> X1 = np.array([[1, 1.8, 1],
    >>>                [2, 3.2, 1],
    >>>                [1.5, 2.8, 1],
    >>>                [4.1, 0.7, 0.1],
    >>>                [5.01, 0.8, 0.1],
    >>>                [6.2, 0.9, 0.1]])
    >>> X2 = np.array([[2, 2.8, 2],
    >>>                [3, 4.2, 2],
    >>>                [2.5, 3.8, 2],
    >>>                [5.1, 1.7, 1.1],
    >>>                [6.01, 1.8, 1.1],
    >>>                [7.2, 1.9, 1.1]])
    >>> y = np.array([1, 1, 1, 0, 0, 0])
    >>> seed = 240805
    >>> from nmfprofiler import NMFProfiler
    >>> model = NMFProfiler(omic1=X1, omic2=X2, y=y, seed=seed)
    >>> res = model.fit()
    >>> print(res)
    >>> res.heatmap(obj_to_viz="W", height=10, width=10, path="")
    >>> model.barplot_error(height=6, width=15, path="")
    """

    def __init__(
        self,
        omic1,
        omic2,
        y,
        params={
            "gamma": 1e-2,
            "lambda": 1e-3,
            "mu": 1e-3,
            "eta1": 1.00,
            "eta2": 1.00,
            "alpha": 2,
            "sigma": 1e-9,
            "m_back": 1,
        },
        init_method="random2",
        solver="analytical",
        as_sklearn=True,
        backtrack=False,
        max_iter_back=100,
        tol=1e-4,
        max_iter=1000,
        seed=None,
        verbose=False,
    ):

        self.omic1 = omic1
        self.omic2 = omic2
        self.y = y
        self.params = params
        self.init_method = init_method
        self.solver = solver
        self.as_sklearn = as_sklearn
        self.backtrack = backtrack
        self.max_iter_back = max_iter_back
        self.tol = tol
        self.max_iter = max_iter
        self.seed = seed
        self.verbose = verbose

    def __str__(self):
        """Briefly describe inputs and outputs of NMFProfiler."""
        print_statement = (
            "NMFProfiler\n-----------\n\nAnalysis run on dataset 1 containing "
            f"{self.omic1.shape[1]} features measured on {self.omic1.shape[0]}"
            f" samples,\ndataset 2 containing {self.omic2.shape[1]} features "
            f"measured on the same {self.omic2.shape[0]} samples.\nSamples "
            f"are splitted into {len(np.unique(self.y))} distinct groups.\n\n"
            f"NMFProfiler (as_sklearn = {self.as_sklearn}) extracted "
            f"{len(np.unique(self.y))} profiles in {self.runningtime} "
            "seconds.\n\nFor more information, please refer to help(), "
            "GitLab page or contact aurelie.mercadie@inrae.fr."
        )
        return print_statement

    def _update_params(self):
        """Adapt hyperparameters to the datasets analyzed.

        Hyperparameters lambda and gamma, used in the objective function,
        depend on (n_samples), the number of samples.
        This function will update them accordingly.
        """
        # Multiply lambda parameter by n_samples to get its final value
        self.params["lambda"] *= self.y.shape[0]

        # Multiply gamma parameter by n_samples to get its final value
        self.params["gamma"] *= self.y.shape[0]

    def _preprocess_data(self):
        """Pre-process datasets.

        Apply a min-max normalization and divide by the square root
        of the number of features.
        """
        # First dataset
        for i in range(self.omic1.shape[1]):
            self.omic1[:, i] = (
                self.omic1[:, i] - np.min(self.omic1[:, i])
            ) / (
                np.max(self.omic1[:, i]) - np.min(self.omic1[:, i])
            )
        self.omic1 = self.omic1 * (1 / np.sqrt(self.omic1.shape[1]))

        # Second dataset
        for i in range(self.omic2.shape[1]):
            self.omic2[:, i] = (
                self.omic2[:, i] - np.min(self.omic2[:, i])
            ) / (
                np.max(self.omic2[:, i]) - np.min(self.omic2[:, i])
            )
        self.omic2 = self.omic2 * (1 / np.sqrt(self.omic2.shape[1]))

    def _initialize_w_h_beta(self):
        """Initialize matrices W, H^j and Beta^j.

        Several ways to intialize W, H1, H2.
        Beta1 and Beta2 are initialized with 1s vectors.

        Note
        ----
        Based on _initialize_nmf of sklearn.decomposition.NMF.
        """

        # Extract K, the number of latent components, as equal to
        # the number of distinct groups in y
        K = len(np.unique(self.y))
        # For now, initialize K_gp, the number of latent components
        # dedicated to groups, identically to K
        K_gp = len(np.unique(self.y))

        # For W, H1 and H2:
        # 1.1. Concatenate omics data sets
        omics = np.concatenate((self.omic1, self.omic2), axis=1)
        # 1.2. Initialize using sklearn function
        if self.init_method == "random2":
            # 1.2a. Initialize W with both omics and Hj
            # with specific omic (random)
            W0, *_ = _initialize_nmf(
                X=omics,
                n_components=K,
                init="random",
                random_state=self.seed
            )
            *_, H1_0 = _initialize_nmf(
                X=self.omic1,
                n_components=K,
                init="random",
                random_state=self.seed
            )
            *_, H2_0 = _initialize_nmf(
                X=self.omic2,
                n_components=K,
                init="random",
                random_state=self.seed
            )
            del _
        elif self.init_method == "random3":
            # 1.2b. FOR IDENTICAL OMICS DATA SETS - Initialize W
            # with both omics, H1 with omic1 and H2 as H1 (random)
            W0, H1_0 = _initialize_nmf(
                X=self.omic1,
                n_components=K,
                init="random",
                random_state=self.seed
            )
            H2_0 = H1_0.copy()
        elif self.init_method == "nndsvd2":
            # 1.2c. Initialize W with both omics and Hj
            # with specific omic (nndsvd)
            W0, *_ = _initialize_nmf(
                X=omics,
                n_components=K,
                init="nndsvd",
                random_state=self.seed
            )
            *_, H1_0 = _initialize_nmf(
                X=self.omic1,
                n_components=K,
                init="nndsvd",
                random_state=self.seed
            )
            *_, H2_0 = _initialize_nmf(
                X=self.omic2,
                n_components=K,
                init="nndsvd",
                random_state=self.seed
            )
            del _
        elif self.init_method == "nndsvd3":
            # 1.2d. Initialize W with each omic then take the mean and
            # initialize Hj with specific omic (nndsvd)
            W_a, H1_0 = _initialize_nmf(
                X=self.omic1,
                n_components=K,
                init="nndsvd",
                random_state=self.seed
            )
            W_b, H2_0 = _initialize_nmf(
                X=self.omic2,
                n_components=K,
                init="nndsvd",
                random_state=self.seed
            )
            W0 = (1 / 2) * (W_a + W_b)
            del W_a, W_b
        else:
            # 1.2e. Initialize both with all omics, using whatever method
            # available in _initialize_nmf(). See help.
            W0, H0 = _initialize_nmf(
                X=omics,
                n_components=K,
                init=self.init_method,
                random_state=self.seed
            )
            # 1.2e. Split H matrix
            H1_0, H2_0 = np.split(
                ary=H0, indices_or_sections=[self.omic1.shape[1]], axis=1
            )
            del H0

        # For Beta1 and Beta2:
        Beta1_0 = np.repeat(1, K)
        Beta2_0 = np.repeat(1, K)
        # Put to zero all coefficients linked to component k when k > K_gp
        if K_gp < K:
            Beta1_0[K_gp:] = 0
            Beta2_0[K_gp:] = 0

        return W0, H1_0, H2_0, Beta1_0, Beta2_0

    def fit(self):
        """Run NMFProfiler."""
        # Check hyperparameters and inputs
        _check_inputs_NMFProfiler(self)

        # Extract K, the number of latent components, as equal
        # to the number of distinct groups in y
        K = len(np.unique(self.y))
        # For now, initialize K_gp, the number of latent components
        # dedicated to groups, identically to K
        K_gp = len(np.unique(self.y))

        # Automatically convert a vector encoding U groups into
        # a one-hot encoded matrix
        encoder = OneHotEncoder(handle_unknown="ignore")
        Y = encoder.fit_transform(self.y.reshape(-1, 1)).toarray()

        # Pre-process datasets (with min-max and number of features)
        self._preprocess_data()

        # Initialize matrices
        W0, H1_0, H2_0, Beta1_0, Beta2_0 = self._initialize_w_h_beta()
        self.W_init = W0
        self.H1_init = H1_0
        self.H2_init = H2_0
        self.Beta1_init = Beta1_0
        self.Beta2_init = Beta2_0

        # Update lambda and gamma given sample size
        self._update_params()

        # Solve the minimization problem
        # ------------------------------

        # Create matrices and vectors to update using initialization
        # (and keep intact initialized matrices and vectors)
        W, H1, H2, Beta1, Beta2 = (
            deepcopy(W0),
            deepcopy(H1_0),
            deepcopy(H2_0),
            deepcopy(Beta1_0),
            deepcopy(Beta2_0),
        )

        # Create lists of error terms to enrich iteratively
        (
            error,
            margH1,
            margH2,
            gradH1,
            gradH2,
            distort1,
            distort2,
            sparsity1,
            sparsity2,
            regul,
            pred1,
            pred2,
            nb_iters,
        ) = ([] for i in range(13))
        # Create lists of LDA performance indicators to enrich iteratively
        (
            R2adj_1,
            R2adj_2,
            BIC_1,
            BIC_2,
            AIC_1,
            AIC_2,
            F_pval_1,
            F_pval_2,
            bet1_1,
            bet1_2,
            bet2_1,
            bet2_2,
        ) = ([] for i in range(12))

        loss_init = _computeF(
            self.omic1,
            self.omic2,
            Y,
            W0,
            H1_0,
            H2_0,
            Beta1_0,
            Beta2_0,
            self.params["mu"],
            self.params["lambda"],
            self.params["gamma"],
            K_gp,
            details=True,
        )
        error.append(loss_init[0])
        nb_iters.append(0)
        distort1.append(loss_init[1])
        distort2.append(loss_init[2])
        sparsity1.append(loss_init[3])
        sparsity2.append(loss_init[4])
        regul.append(loss_init[5])
        pred1.append(loss_init[6])
        pred2.append(loss_init[7])

        # Keep track of marginal objective functions in Hj with
        # initial matrices (necessary for linesearch first execution)
        margH1.append(
            _computeMargH(
                self.omic1,
                Y,
                W0,
                H1_0,
                Beta1_0,
                self.params["gamma"],
                self.params["lambda"],
                K_gp,
            )
        )
        margH2.append(
            _computeMargH(
                self.omic2,
                Y,
                W0,
                H2_0,
                Beta2_0,
                self.params["gamma"],
                self.params["lambda"],
                K_gp,
            )
        )

        # LDAs with initial matrices
        reg1_init = sm.OLS(
            self.y, sm.add_constant(safe_sparse_dot(self.omic1, H1_0.T))
        ).fit()
        reg2_init = sm.OLS(
            self.y, sm.add_constant(safe_sparse_dot(self.omic2, H2_0.T))
        ).fit()

        bet1_1.append(reg1_init.params[1])
        bet2_1.append(reg1_init.params[2])
        bet1_2.append(reg2_init.params[1])
        bet2_2.append(reg2_init.params[2])
        R2adj_1.append(reg1_init.rsquared_adj)
        R2adj_2.append(reg2_init.rsquared_adj)
        BIC_1.append(reg1_init.bic)
        BIC_2.append(reg2_init.bic)
        AIC_1.append(reg1_init.aic)
        AIC_2.append(reg2_init.aic)
        F_pval_1.append(reg1_init.f_pvalue)
        F_pval_2.append(reg2_init.f_pvalue)

        # Show the initial global loss value
        if self.verbose:
            print("Error after initialization step: %f" % (error[0]))

        # To keep track of the choice of etas
        eta1, eta2 = ([] for i in range(2))
        eta1.append(self.params["eta1"])
        eta2.append(self.params["eta2"])

        # Begin the optimization,k
        start_time = process_time()
        for n_iter in range(1, self.max_iter + 1):

            # Solver

            # Analytical solver...
            if self.solver == "analytical":
                (
                    W,
                    H1,
                    H2,
                    Beta1,
                    Beta2,
                    self.params["eta1"],
                    self.params["eta2"],
                    margH1,
                    margH2,
                    gradH1,
                    gradH2,
                ) = _analytic_solver(
                    self.omic1,
                    self.omic2,
                    Y,
                    W,
                    H1,
                    H2,
                    Beta1,
                    Beta2,
                    self.params,
                    as_sklearn=self.as_sklearn,
                    backtrack=self.backtrack,
                    max_iter_back=self.max_iter_back,
                    H1_loss=margH1,
                    H2_loss=margH2,
                    H1_grad=gradH1,
                    H2_grad=gradH2,
                    K=K,
                    K_gp=K_gp,
                    verbose=self.verbose,
                )

            # ... or Autograd solver
            else:
                W, H1, H2, Beta1, Beta2 = _autograd_solver()

            # Keep track of optimal etas
            eta1.append(self.params["eta1"])
            eta2.append(self.params["eta2"])

            # Compute the new loss as well as specific terms
            loss_ = _computeF(
                self.omic1,
                self.omic2,
                Y,
                W,
                H1,
                H2,
                Beta1,
                Beta2,
                self.params["mu"],
                self.params["lambda"],
                self.params["gamma"],
                K_gp,
                details=True,
            )
            error.append(loss_[0])
            nb_iters.append(n_iter)
            distort1.append(loss_[1])
            distort2.append(loss_[2])
            sparsity1.append(loss_[3])
            sparsity2.append(loss_[4])
            regul.append(loss_[5])
            pred1.append(loss_[6])
            pred2.append(loss_[7])

            # Monitor the LDA part
            reg1 = sm.OLS(
                self.y, sm.add_constant(safe_sparse_dot(self.omic1, H1.T))
            ).fit()
            reg2 = sm.OLS(
                self.y, sm.add_constant(safe_sparse_dot(self.omic2, H2.T))
            ).fit()
            bet1_1.append(reg1.params[1])
            bet2_1.append(reg1.params[2])
            bet1_2.append(reg2.params[1])
            bet2_2.append(reg2.params[2])
            R2adj_1.append(reg1.rsquared_adj)
            R2adj_2.append(reg2.rsquared_adj)
            BIC_1.append(reg1.bic)
            BIC_2.append(reg2.bic)
            AIC_1.append(reg1.aic)
            AIC_2.append(reg2.aic)
            F_pval_1.append(reg1.f_pvalue)
            F_pval_2.append(reg2.f_pvalue)

            # Every 10 iterations, if tol is still strictly positive and
            # verbose == True, compute the loss value
            if self.tol > 0 and n_iter % 10 == 0 and self.verbose:

                iter_time = process_time()
                print(
                    "Epoch %02d reached after %.3f seconds, error: %f"
                    % (n_iter, iter_time - start_time, error[-1])
                )

            # If the difference between losses at t and t-1
            # (divided by error_at_init) is smaller than threshold, stop algo.
            # Note the initial convergence criterion of scikit-learn was
            # (error[-2] - error[-1]) / error[0] < tol
            if (error[-2] - error[-1]) / error[-2] < self.tol:
                break

        end_time = process_time()
        self.runningtime = end_time - start_time

        # When converged, print global loss (IF not already shown prev.)
        # --------------------------------------------------------------
        if self.verbose and (self.tol == 0 or n_iter % 10 != 0):
            print(
                "Algorithm converged in %02d steps \
                 after %.3f seconds, error: %f"
                % (n_iter, end_time - start_time, error[-1])
            )

        # Warning if not converged (i.e. value of F not below tol)
        # but reached max_iter
        # --------------------------------------------------------
        if n_iter == self.max_iter and self.tol > 0:
            warnings.warn(
                "Maximum number of iterations %d reached. Increase "
                "it to improve convergence." % self.max_iter,
                ConvergenceWarning
            )

        # Store optimal values of matrices
        # --------------------------------
        self.n_iter = n_iter
        self.W = W
        self.H1 = H1
        self.H2 = H2
        self.Beta1 = Beta1
        self.Beta2 = Beta2

        # Keep track of final Hj gradients and build the Hj gradients matrix
        # (following up their evolution during optimization)
        # ------------------------------------------------------------------
        gradH1.append(
            multi_dot([W.T, W, H1])
            + (
                self.params["gamma"]
                * multi_dot(
                    [
                        np.transpose(Beta1[newaxis]),
                        Beta1[newaxis],
                        H1,
                        self.omic1.T,
                        self.omic1,
                    ]
                )
            )
            - (
                safe_sparse_dot(W.T, self.omic1)
                + (
                    self.params["gamma"]
                    * multi_dot(
                        [
                            np.transpose(Beta1[newaxis]),
                            self.y[newaxis],
                            self.omic1
                        ]
                    )
                )
            )
        )
        gradH2.append(
            multi_dot([W.T, W, H2])
            + (
                self.params["gamma"]
                * multi_dot(
                    [
                        np.transpose(Beta2[newaxis]),
                        Beta2[newaxis],
                        H2,
                        self.omic2.T,
                        self.omic2,
                    ]
                )
            )
            - (
                safe_sparse_dot(W.T, self.omic2)
                + (
                    self.params["gamma"]
                    * multi_dot(
                        [np.transpose(Beta2[newaxis]),
                         self.y[newaxis], self.omic2]
                    )
                )
            )
        )

        grads = np.hstack(
            (
                np.vstack([norm(i) ** 2 for i in gradH1]),
                np.vstack([norm(i) ** 2 for i in gradH2]),
            )
        )
        self.df_grads = pd.DataFrame(grads, columns=["grad_H1", "grad_H2"])

        # Build the error terms matrix
        # ----------------------------
        error_terms = np.hstack(
            (
                np.vstack(nb_iters),
                np.vstack(distort1),
                np.vstack(distort2),
                np.vstack(sparsity1),
                np.vstack(sparsity2),
                np.vstack(regul),
                np.vstack(pred1),
                np.vstack(pred2),
                np.vstack(error),
            )
        )
        self.df_errors = pd.DataFrame(
            error_terms,
            columns=[
                "iter",
                "distort1",
                "distort2",
                "sparsity1",
                "sparsity2",
                "regul",
                "pred1",
                "pred2",
                "loss",
            ],
        )

        # Build the LDA performance matrix
        # --------------------------------
        LDA_perf = np.hstack(
            (
                np.vstack(nb_iters),
                np.vstack(bet1_1),
                np.vstack(bet1_2),
                np.vstack(R2adj_1),
                np.vstack(BIC_1),
                np.vstack(AIC_1),
                np.vstack(F_pval_1),
                np.vstack(bet1_2),
                np.vstack(bet2_2),
                np.vstack(R2adj_2),
                np.vstack(BIC_2),
                np.vstack(AIC_2),
                np.vstack(F_pval_2),
            )
        )
        self.df_ldaperf = pd.DataFrame(
            LDA_perf,
            columns=[
                "iter",
                "Comp.1 coef (omic1)",
                "Comp.2 coef (omic1)",
                "R2 Adjusted (omic1)",
                "BIC (omic1)",
                "AIC (omic1)",
                "F-statistic p-value (omic1)",
                "Comp.1 coef (omic2)",
                "Comp.2 coef (omic2)",
                "R2 Adjusted (omic2)",
                "BIC (omic2)",
                "AIC (omic2)",
                "F-statistic p-value (omic2)",
            ],
        )

        # Build the etas matrix
        # (following up etas evolution during optimization)
        # -------------------------------------------------
        etas = np.hstack((np.vstack(eta1), np.vstack(eta2)))
        self.df_etas = pd.DataFrame(etas, columns=["eta_omic1", "eta_omic2"])

        return self

    def predict(self, new_ind, verbose=False):
        """Predict the group of a new sample, based on its projection onto
        signatures matrices.

        Params
        ------
        :new_ind: list. List of arrays containing values of
            features from omic1 and omic2 for a new sample.

        Values
        ------
        :group: list. Predicted group (one of 0 or 1) for the new sample
            in each omic.
        :proj1: array. Projection onto H1
        :proj2: array. Projection onto H2
        """
        # Convert to right format
        new_ind_X1 = new_ind[0][newaxis]
        new_ind_X2 = new_ind[1][newaxis]

        # Compute projections of the new samples onto dictionary matrices
        proj1 = safe_sparse_dot(new_ind_X1, self.H1.T)
        proj2 = safe_sparse_dot(new_ind_X2, self.H2.T)

        # For each omic, find which component gave the highest score
        group = [proj1.argmax(), proj2.argmax()]

        # Compute global group value
        group_value = int(np.average(group))
        if verbose:
            print(
                f"Profile of this new sample resembles \
                  profile of group {group_value}."
            )

        res = {"group": group, "proj1": proj1, "proj2": proj2}

        return res

    def barplot_error(self, width, height, path):
        """Visualize of the final error terms.

        Params
        ------
        :width: int. Width of the figure (in `units` by default).
        :height: int. Height of the figure (in `units` by default).
        :path: str. Location to save the figure.

        Values
        ------
        Return a barplot of the different error terms.
        """
        data_barplot = [
            ["reconstruction omic1", self.df_errors.iloc[-1, 1]],
            ["reconstruction omic2", self.df_errors.iloc[-1, 2]],
            ["l2 penalty on W", self.df_errors.iloc[-1, 5]],
            ["l1 penalty on H1", self.df_errors.iloc[-1, 3]],
            ["l1 penalty on H2", self.df_errors.iloc[-1, 4]],
            ["supervised part omic1", self.df_errors.iloc[-1, 6]],
            ["supervised part omic2", self.df_errors.iloc[-1, 7]],
        ]
        df_bar = pd.DataFrame(data_barplot, columns=["part", "value"])

        plt.figure(figsize=(width, height))
        sns.barplot(data=df_bar, x="part", y="value")
        plt.savefig(str(path + "BarplotErrors.png"))
        plt.show()

    def evolplot(self, obj_to_check, width, height):
        """Visualize the evolution of either etas values or gradients along
        the optimization process.

        Params
        ------
        :obj_to_check: str. One of {`'etas'`, `'gradients'`}.
        :width: int, width of the figure (in `units` by default).
        :height: int, height of the figure (in `units` by default).

        Values
        ------
        Return a lineplot.
        """
        if obj_to_check == "etas":
            plt.figure(figsize=(width, height))
            sns.lineplot(data=self.df_etas, palette=["blue", "orange"])
            plt.show()

        elif obj_to_check == "gradients":
            plt.figure(figsize=(width, height))
            sns.lineplot(data=self.df_grads, palette=["blue", "orange"])
            plt.show()

        else:
            raise Exception(
                "Cannot plot this object, please change 'obj_to_check' input."
                " Only 'df_etas' and 'df_gradients' outputs "
                "from NMFProfiler can be plotted with this method."
            )

    def heatmap(self, obj_to_viz, width, height, path):
        """Visualize any matrix of X^j, W, H^j with a heatmap.

        Params
        ------
        :obj_to_viz: str. One of {`'omic1'`, `'omic2'`,
            `'W'`, `'H1'`, `'H2'`}.
        :width: int. Width of the figure (in units by default).
        :height: int. Height of the figure (in units by default).
        :path: str. Location to save the figure.

        Values
        ------
        Returns a heatmap.
        """
        plt.figure(figsize=(width, height))

        if obj_to_viz == "omic1":
            sns.heatmap(pd.DataFrame(self.omic1), cmap="viridis")
        elif obj_to_viz == "omic2":
            sns.heatmap(pd.DataFrame(self.omic2), cmap="viridis")
        elif obj_to_viz == "W":
            sns.heatmap(pd.DataFrame(self.W), cmap="viridis")
        elif obj_to_viz == "H1":
            sns.heatmap(pd.DataFrame(self.H1), cmap="viridis")
        elif obj_to_viz == "H2":
            sns.heatmap(pd.DataFrame(self.H2), cmap="viridis")
        else:
            raise Exception(
                "Cannot plot this object, please change 'obj_to_viz' input."
                " Only 'omic1', 'omic2', 'W', 'H1' and 'H2' outputs "
                "from NMFProfiler can be plotted with this method."
            )

        plt.savefig(str(path + obj_to_viz + "_Heatmap.png"))
        plt.show()
