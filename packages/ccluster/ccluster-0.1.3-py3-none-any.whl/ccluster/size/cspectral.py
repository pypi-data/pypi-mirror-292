"""Constrained spectral clustering"""

# Author: Gael Varoquaux <gael.varoquaux@normalesup.org>
#         Brian Cheung
#         Wei LI <kuantkid@gmail.com>
#         Andrew Knyazev <Andrew.Knyazev@ucdenver.edu>
# License: BSD 3 clause

import warnings
from numbers import Integral, Real

import numpy as np
from .ckmeans import constrained_k_means

from sklearn.base import (
    BaseEstimator,
    ClusterMixin,
    _fit_context,
)

from sklearn.manifold import spectral_embedding
from sklearn.metrics.pairwise import KERNEL_PARAMS, pairwise_kernels
from sklearn.neighbors import NearestNeighbors, kneighbors_graph
from sklearn.utils import check_random_state
from sklearn.utils._param_validation import Interval, StrOptions, validate_params

from .cbase import CBase


@validate_params(
    {"affinity": ["array-like", "sparse matrix"]},
    prefer_skip_nested_validation=False,
)
def constrained_spectral_clustering(
    affinity,
    *,
    cluster_sizes,
    n_clusters=8,
    n_components=None,
    eigen_solver=None,
    random_state=None,
    n_init=10,
    eigen_tol="auto",
    verbose=False,
):
    """Apply clustering to a projection of the normalized Laplacian with cluster size constraints.

    Parameters
    ----------
    affinity : {array-like, sparse matrix} of shape (n_samples, n_samples)
        The affinity matrix describing the relationship of the samples to
        embed. **Must be symmetric**.

        Possible examples:
          - adjacency matrix of a graph,
          - heat kernel of the pairwise distance matrix of the samples,
          - symmetric k-nearest neighbours connectivity matrix of the samples.

    n_clusters : int, default=None
        Number of clusters to extract.

    cluster_sizes : array-like of shape (n_constraints,), default=None
        The constraints for the cluster sizes. If `None`, we retrieve
        the classical spectral clustering algorithm. The constraints can
        either be exhaustive (n_constraints == n_clusters) or partial
        (n_constraints < n_clusters).

    n_components : int, default=n_clusters
        Number of eigenvectors to use for the spectral embedding.

    eigen_solver : {None, 'arpack', 'lobpcg', or 'amg'}
        The eigenvalue decomposition method. If None then ``'arpack'`` is used.
        See [4]_ for more details regarding ``'lobpcg'``.
        Eigensolver ``'amg'`` runs ``'lobpcg'`` with optional
        Algebraic MultiGrid preconditioning and requires pyamg to be installed.
        It can be faster on very large sparse problems [6]_ and [7]_.

    random_state : int, RandomState instance, default=None
        A pseudo random number generator used for the initialization
        of the lobpcg eigenvectors decomposition when `eigen_solver ==
        'amg'`, and for the K-Means initialization. Use an int to make
        the results deterministic across calls.

    n_init : int, default=10
        Number of time the k-means algorithm will be run with different
        centroid seeds. The final results will be the best output of n_init
        consecutive runs in terms of inertia.

    eigen_tol : float, default="auto"
        Stopping criterion for eigendecomposition of the Laplacian matrix.
        If `eigen_tol="auto"` then the passed tolerance will depend on the
        `eigen_solver`:

        - If `eigen_solver="arpack"`, then `eigen_tol=0.0`;
        - If `eigen_solver="lobpcg"` or `eigen_solver="amg"`, then
          `eigen_tol=None` which configures the underlying `lobpcg` solver to
          automatically resolve the value according to their heuristics. See,
          :func:`scipy.sparse.linalg.lobpcg` for details.

        Note that when using `eigen_solver="lobpcg"` or `eigen_solver="amg"`
        values of `tol<1e-5` may lead to convergence issues and should be
        avoided.

    verbose : bool, default=False
        Verbosity mode.

    Returns
    -------
    labels : array of integers, shape: n_samples
        The labels of the clusters.

    Notes
    -----
    The graph should contain only one connected component, elsewhere
    the results make little sense.

    References
    ----------

    .. [1] :doi:`Normalized cuts and image segmentation, 2000
           Jianbo Shi, Jitendra Malik
           <10.1109/34.868688>`

    .. [2] :doi:`A Tutorial on Spectral Clustering, 2007
           Ulrike von Luxburg
           <10.1007/s11222-007-9033-z>`

    .. [3] `Multiclass spectral clustering, 2003
           Stella X. Yu, Jianbo Shi
           <https://people.eecs.berkeley.edu/~jordan/courses/281B-spring04/readings/yu-shi.pdf>`_

    .. [4] :doi:`Toward the Optimal Preconditioned Eigensolver:
           Locally Optimal Block Preconditioned Conjugate Gradient Method, 2001
           A. V. Knyazev
           SIAM Journal on Scientific Computing 23, no. 2, pp. 517-541.
           <10.1137/S1064827500366124>`

    .. [5] :doi:`Simple, direct, and efficient multi-way spectral clustering, 2019
           Anil Damle, Victor Minden, Lexing Ying
           <10.1093/imaiai/iay008>`

    .. [6] :doi:`Multiscale Spectral Image Segmentation Multiscale preconditioning
           for computing eigenvalues of graph Laplacians in image segmentation, 2006
           Andrew Knyazev
           <10.13140/RG.2.2.35280.02565>`

    .. [7] :doi:`Preconditioned spectral clustering for stochastic block partition
           streaming graph challenge (Preliminary version at arXiv.)
           David Zhuzhunashvili, Andrew Knyazev
           <10.1109/HPEC.2017.8091045>`

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.metrics.pairwise import pairwise_kernels
    >>> from ccluster.size import constrained_spectral_clustering
    >>> X = np.array([[1, 1], [2, 1], [1, 0],
    ...               [4, 7], [3, 5], [3, 6]])
    >>> affinity = pairwise_kernels(X, metric='rbf')
    >>> constrained_spectral_clustering(
    ...     affinity=affinity, cluster_sizes=[4, 2], n_clusters=2, random_state=0
    ... )
    array([0, 0, 0, 1, 0, 1])
    """

    clusterer = ConstrainedSpectralClustering(
        n_clusters=n_clusters,
        cluster_sizes=cluster_sizes,
        n_components=n_components,
        eigen_solver=eigen_solver,
        random_state=random_state,
        n_init=n_init,
        affinity="precomputed",
        eigen_tol=eigen_tol,
        verbose=verbose,
    ).fit(affinity)

    return clusterer.labels_


class ConstrainedSpectralClustering(ClusterMixin, BaseEstimator, CBase):
    """Apply clustering to a projection of the normalized Laplacian with cluster size constraints.

    When calling ``fit``, an affinity matrix is constructed using either
    a kernel function such the Gaussian (aka RBF) kernel with Euclidean
    distance ``d(X, X)``::

            np.exp(-gamma * d(X,X) ** 2)

    or a k-nearest neighbors connectivity matrix.

    Alternatively, a user-provided affinity matrix can be specified by
    setting ``affinity='precomputed'``.


    Parameters
    ----------
    n_clusters : int, default=8
        The dimension of the projection subspace.

    cluster_sizes : array-like of shape (n_constraints,), default=None
        The constraints for the cluster sizes. If `None`, we retrieve
        the classical spectral clustering algorithm. The constraints can
        either be exhaustive (n_constraints == n_clusters) or partial
        (n_constraints < n_clusters).

    eigen_solver : {'arpack', 'lobpcg', 'amg'}, default=None
        The eigenvalue decomposition strategy to use. AMG requires pyamg
        to be installed. It can be faster on very large, sparse problems,
        but may also lead to instabilities. If None, then ``'arpack'`` is
        used.

    n_components : int, default=None
        Number of eigenvectors to use for the spectral embedding. If None,
        defaults to `n_clusters`.

    random_state : int, RandomState instance, default=None
        A pseudo random number generator used for the initialization
        of the lobpcg eigenvectors decomposition when `eigen_solver ==
        'amg'`, and for the K-Means initialization. Use an int to make
        the results deterministic across calls.

        .. note::
            When using `eigen_solver == 'amg'`,
            it is necessary to also fix the global numpy seed with
            `np.random.seed(int)` to get deterministic results. See
            https://github.com/pyamg/pyamg/issues/139 for further
            information.

    n_init : int, default=10
        Number of time the k-means algorithm will be run with different
        centroid seeds. The final results will be the best output of n_init
        consecutive runs in terms of inertia.

    gamma : float, default=1.0
        Kernel coefficient for rbf, poly, sigmoid, laplacian and chi2 kernels.
        Ignored for ``affinity='nearest_neighbors'``.

    affinity : str or callable, default='rbf'
        How to construct the affinity matrix.
         - 'nearest_neighbors': construct the affinity matrix by computing a
           graph of nearest neighbors.
         - 'rbf': construct the affinity matrix using a radial basis function
           (RBF) kernel.
         - 'precomputed': interpret ``X`` as a precomputed affinity matrix,
           where larger values indicate greater similarity between instances.
         - 'precomputed_nearest_neighbors': interpret ``X`` as a sparse graph
           of precomputed distances, and construct a binary affinity matrix
           from the ``n_neighbors`` nearest neighbors of each instance.
         - one of the kernels supported by
           :func:`~sklearn.metrics.pairwise.pairwise_kernels`.

        Only kernels that produce similarity scores (non-negative values that
        increase with similarity) should be used. This property is not checked
        by the clustering algorithm.

    n_neighbors : int, default=10
        Number of neighbors to use when constructing the affinity matrix using
        the nearest neighbors method. Ignored for ``affinity='rbf'``.

    eigen_tol : float, default="auto"
        Stopping criterion for eigen decomposition of the Laplacian matrix.
        If `eigen_tol="auto"` then the passed tolerance will depend on the
        `eigen_solver`:

        - If `eigen_solver="arpack"`, then `eigen_tol=0.0`;
        - If `eigen_solver="lobpcg"` or `eigen_solver="amg"`, then
          `eigen_tol=None` which configures the underlying `lobpcg` solver to
          automatically resolve the value according to their heuristics. See,
          :func:`scipy.sparse.linalg.lobpcg` for details.

        Note that when using `eigen_solver="lobpcg"` or `eigen_solver="amg"`
        values of `tol<1e-5` may lead to convergence issues and should be
        avoided.

    degree : float, default=3
        Degree of the polynomial kernel. Ignored by other kernels.

    coef0 : float, default=1
        Zero coefficient for polynomial and sigmoid kernels.
        Ignored by other kernels.

    kernel_params : dict of str to any, default=None
        Parameters (keyword arguments) and values for kernel passed as
        callable object. Ignored by other kernels.

    n_jobs : int, default=None
        The number of parallel jobs to run when `affinity='nearest_neighbors'`
        or `affinity='precomputed_nearest_neighbors'`. The neighbors search
        will be done in parallel.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors.

    verbose : bool, default=False
        Verbosity mode.

    Attributes
    ----------
    affinity_matrix_ : array-like of shape (n_samples, n_samples)
        Affinity matrix used for clustering. Available only after calling
        ``fit``.

    labels_ : ndarray of shape (n_samples,)
        Labels of each point

    n_features_in_ : int
        Number of features seen during :term:`fit`.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.


    Notes
    -----
    A distance matrix for which 0 indicates identical elements and high values
    indicate very dissimilar elements can be transformed into an affinity /
    similarity matrix that is well-suited for the algorithm by
    applying the Gaussian (aka RBF, heat) kernel::

        np.exp(- dist_matrix ** 2 / (2. * delta ** 2))

    where ``delta`` is a free parameter representing the width of the Gaussian
    kernel.

    An alternative is to take a symmetric version of the k-nearest neighbors
    connectivity matrix of the points.

    If the pyamg package is installed, it is used: this greatly
    speeds up computation.

    Examples
    --------
    >>> from ccluster.size import ConstrainedSpectralClustering
    >>> import numpy as np
    >>> X = np.array([[1, 1], [2, 1], [1, 0],
    ...               [4, 7], [3, 5], [3, 6]])
    >>> clustering = ConstrainedSpectralClustering(n_clusters=2, cluster_sizes=[4, 2],
    ...         random_state=0).fit(X)
    >>> clustering.labels_
    array([0, 0, 0, 1, 0, 1])
    >>> clustering
    ConstrainedSpectralClustering(cluster_sizes=array([4, 2]), n_clusters=2,
        random_state=0)
    """

    _parameter_constraints: dict = {
        "n_clusters": [Interval(Integral, 1, None, closed="left")],
        "eigen_solver": [StrOptions({"arpack", "lobpcg", "amg"}), None],
        "n_components": [Interval(Integral, 1, None, closed="left"), None],
        "random_state": ["random_state"],
        "n_init": [Interval(Integral, 1, None, closed="left")],
        "gamma": [Interval(Real, 0, None, closed="left")],
        "affinity": [
            callable,
            StrOptions(
                set(KERNEL_PARAMS)
                | {"nearest_neighbors", "precomputed", "precomputed_nearest_neighbors"}
            ),
        ],
        "n_neighbors": [Interval(Integral, 1, None, closed="left")],
        "eigen_tol": [
            Interval(Real, 0.0, None, closed="left"),
            StrOptions({"auto"}),
        ],
        "degree": [Interval(Real, 0, None, closed="left")],
        "coef0": [Interval(Real, None, None, closed="neither")],
        "kernel_params": [dict, None],
        "n_jobs": [Integral, None],
        "verbose": ["verbose"],
    }

    def __init__(
        self,
        n_clusters=8,
        *,
        cluster_sizes=None,
        eigen_solver=None,
        n_components=None,
        random_state=None,
        n_init=10,
        gamma=1.0,
        affinity="rbf",
        n_neighbors=10,
        eigen_tol="auto",
        degree=3,
        coef0=1,
        kernel_params=None,
        n_jobs=None,
        verbose=False,
    ):
        self.n_clusters = n_clusters
        self.eigen_solver = eigen_solver
        self.n_components = n_components
        self.random_state = random_state
        self.n_init = n_init
        self.gamma = gamma
        self.affinity = affinity
        self.n_neighbors = n_neighbors
        self.eigen_tol = eigen_tol
        self.degree = degree
        self.coef0 = coef0
        self.kernel_params = kernel_params
        self.n_jobs = n_jobs
        self.verbose = verbose
        self.cluster_sizes = self._check_cluster_size(cluster_sizes)


    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y=None):
        """Perform spectral clustering from features, or affinity matrix.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features) or \
                (n_samples, n_samples)
            Training instances to cluster, similarities / affinities between
            instances if ``affinity='precomputed'``, or distances between
            instances if ``affinity='precomputed_nearest_neighbors``. If a
            sparse matrix is provided in a format other than ``csr_matrix``,
            ``csc_matrix``, or ``coo_matrix``, it will be converted into a
            sparse ``csr_matrix``.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        self : object
            A fitted instance of the estimator.
        """
        X = self._validate_data(
            X,
            accept_sparse=["csr", "csc", "coo"],
            dtype=np.float64,
            ensure_min_samples=2,
        )
        allow_squared = self.affinity in [
            "precomputed",
            "precomputed_nearest_neighbors",
        ]
        if X.shape[0] == X.shape[1] and not allow_squared:
            warnings.warn(
                "The spectral clustering API has changed. ``fit``"
                "now constructs an affinity matrix from data. To use"
                " a custom affinity matrix, "
                "set ``affinity=precomputed``."
            )

        if self.affinity == "nearest_neighbors":
            connectivity = kneighbors_graph(
                X, n_neighbors=self.n_neighbors, include_self=True, n_jobs=self.n_jobs
            )
            self.affinity_matrix_ = 0.5 * (connectivity + connectivity.T)
        elif self.affinity == "precomputed_nearest_neighbors":
            estimator = NearestNeighbors(
                n_neighbors=self.n_neighbors, n_jobs=self.n_jobs, metric="precomputed"
            ).fit(X)
            connectivity = estimator.kneighbors_graph(X=X, mode="connectivity")
            self.affinity_matrix_ = 0.5 * (connectivity + connectivity.T)
        elif self.affinity == "precomputed":
            self.affinity_matrix_ = X
        else:
            params = self.kernel_params
            if params is None:
                params = {}
            if not callable(self.affinity):
                params["gamma"] = self.gamma
                params["degree"] = self.degree
                params["coef0"] = self.coef0
            self.affinity_matrix_ = pairwise_kernels(
                X, metric=self.affinity, filter_params=True, **params
            )

        random_state = check_random_state(self.random_state)
        n_components = (
            self.n_clusters if self.n_components is None else self.n_components
        )
        # We now obtain the real valued solution matrix to the
        # relaxed Ncut problem, solving the eigenvalue problem
        # L_sym x = lambda x  and recovering u = D^-1/2 x.
        # The first eigenvector is constant only for fully connected graphs
        # and should be kept for spectral clustering (drop_first = False)
        # See spectral_embedding documentation.
        maps = spectral_embedding(
            self.affinity_matrix_,
            n_components=n_components,
            eigen_solver=self.eigen_solver,
            random_state=random_state,
            eigen_tol=self.eigen_tol,
            drop_first=False,
        )

        # We then discretize the result using the constrained kmeans
        _, self.labels_, _ = constrained_k_means(
            maps,
            self.n_clusters,
            cluster_sizes=self.cluster_sizes,
            random_state=random_state,
            n_init=self.n_init,
            verbose=self.verbose,
        )

        return self


    def fit_predict(self, X, y=None):
        """Perform constrained spectral clustering on `X` and return cluster labels.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features) or \
                (n_samples, n_samples)
            Training instances to cluster, similarities / affinities between
            instances if ``affinity='precomputed'``, or distances between
            instances if ``affinity='precomputed_nearest_neighbors``. If a
            sparse matrix is provided in a format other than ``csr_matrix``,
            ``csc_matrix``, or ``coo_matrix``, it will be converted into a
            sparse ``csr_matrix``.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            Cluster labels.
        """
        return super().fit_predict(X, y)

    def _more_tags(self):
        return {
            "pairwise": self.affinity in [
                "precomputed",
                "precomputed_nearest_neighbors",
            ]
        }