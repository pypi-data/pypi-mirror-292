"""Constrained K-means clustering."""

import warnings
from abc import ABC
from numbers import Integral, Real

import numpy as np
import ot
import scipy.sparse as sp
from sklearn.base import (
    BaseEstimator,
    ClassNamePrefixFeaturesOutMixin,
    ClusterMixin,
    TransformerMixin,
    _fit_context,
)
from sklearn.cluster._k_means_common import (
    CHUNK_SIZE,
    _inertia_dense,
    _inertia_sparse,
    _is_same_clustering
)
from sklearn.cluster._kmeans import kmeans_plusplus
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.utils import check_array, check_random_state
from sklearn.utils._openmp_helpers import _openmp_effective_n_threads
from sklearn.utils._param_validation import Hidden, Interval, StrOptions, validate_params
from sklearn.utils.extmath import row_norms
from sklearn.utils.fixes import threadpool_info, threadpool_limits
from sklearn.utils.sparsefuncs import mean_variance_axis
from sklearn.utils.validation import (
    _is_arraylike_not_scalar,
    check_is_fitted, )

from .cbase import CBase


###############################################################################
# K-means batch estimation by EM (expectation maximization)


def _tolerance(X, tol):
    """Return a tolerance which is dependent on the dataset."""
    if tol == 0:
        return 0
    if sp.issparse(X):
        variances = mean_variance_axis(X, axis=0)[1]
    else:
        variances = np.var(X, axis=0)
    return np.mean(variances) * tol


@validate_params(
    {
        "X": ["array-like", "sparse matrix"],
        "cluster_sizes": ["array-like", None],
        "return_n_iter": [bool],
    },
    prefer_skip_nested_validation=False,
)
def constrained_k_means(X, n_clusters, cluster_sizes, *,
                        init="k-means++", n_init=10, max_iter=300, verbose=False,
                        tol=1e-4, random_state=None, copy_x=True, return_n_iter=False):
    """Perform K-means clustering algorithm with cluster size constraints.


    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The observations to cluster. It must be noted that the data
        will be converted to C ordering, which will cause a memory copy
        if the given data is not C-contiguous.

    n_clusters : int
        The number of clusters to form as well as the number of
        centroids to generate.

    cluster_sizes : array-like of shape (n_constraints,), default=None
        The constraints for the cluster sizes. If `None`, we retrieve
        the classical Lloyd algorithm. The constraints can either be
        exhaustive (n_constraints == n_clusters) or partial
        (n_constraints < n_clusters).

    init : {'k-means++', 'random'}, callable or array-like of shape \
            (n_clusters, n_features), default='k-means++'
        Method for initialization:

        - `'k-means++'` : selects initial cluster centers for k-mean
          clustering in a smart way to speed up convergence.
        - `'random'`: choose `n_clusters` observations (rows) at random from data
          for the initial centroids.
        - If an array is passed, it should be of shape `(n_clusters, n_features)`
          and gives the initial centers.
        - If a callable is passed, it should take arguments `X`, `n_clusters` and a
          random state and return an initialization.

    n_init : int, default=10
        Number of time the k-means algorithm will be run with different
        centroid seeds. The final results will be the best output of
        n_init consecutive runs in terms of inertia.


    max_iter : int, default=300
        Maximum number of iterations of the k-means algorithm to run.

    verbose : bool, default=False
        Verbosity mode.

    tol : float, default=1e-4
        Relative tolerance with regards to Frobenius norm of the difference
        in the cluster centers of two consecutive iterations to declare
        convergence.

    random_state : int, RandomState instance or None, default=None
        Determines random number generation for centroid initialization. Use
        an int to make the randomness deterministic.

    copy_x : bool, default=True
        When pre-computing distances it is more numerically accurate to center
        the data first. If `copy_x` is True (default), then the original data is
        not modified. If False, the original data is modified, and put back
        before the function returns, but small numerical differences may be
        introduced by subtracting and then adding the data mean. Note that if
        the original data is not C-contiguous, a copy will be made even if
        `copy_x` is False. If the original data is sparse, but not in CSR format,
        a copy will be made even if `copy_x` is False.

    return_n_iter : bool, default=False
        Whether or not to return the number of iterations.

    Returns
    -------
    centroid : ndarray of shape (n_clusters, n_features)
        Centroids found at the last iteration of k-means.

    label : ndarray of shape (n_samples,)
        The `label[i]` is the code or index of the centroid the
        i'th observation is closest to.

    inertia : float
        The final value of the inertia criterion (sum of squared distances to
        the closest centroid for all observations in the training set).

    best_n_iter : int
        Number of iterations corresponding to the best results.
        Returned only if `return_n_iter` is set to True.
    """
    est = ConstrainedKMeans(
        n_clusters=n_clusters,
        cluster_sizes=cluster_sizes,
        init=init,
        n_init=n_init,
        max_iter=max_iter,
        verbose=verbose,
        tol=tol,
        random_state=random_state,
        copy_x=copy_x,
    ).fit(X)
    if return_n_iter:
        return est.cluster_centers_, est.labels_, est.inertia_, est.n_iter_
    else:
        return est.cluster_centers_, est.labels_, est.inertia_


def _relocate_empty_clusters_dense(X, idx_unconstrained, centers_new, weight_in_clusters, labels):
    empty_clusters = np.where(np.equal(weight_in_clusters, 0))[0].astype(np.int32)
    n_empty = empty_clusters.shape[0]
    if n_empty == 0:
        return

    for empty_cluster_id in empty_clusters:
        for old_cluster_id in range(idx_unconstrained, centers_new.shape[0]):
            if weight_in_clusters[old_cluster_id] <= 1:
                continue

            far_idx = np.where(labels == old_cluster_id)[0][0]

            centers_new[old_cluster_id] = weight_in_clusters[old_cluster_id] * centers_new[old_cluster_id] - X[far_idx]
            centers_new[old_cluster_id] = centers_new[old_cluster_id] / (weight_in_clusters[old_cluster_id]-1)
            if sp.issparse(X):
                centers_new[empty_cluster_id] = X[far_idx].A
            else:
                centers_new[empty_cluster_id] = X[far_idx]

            labels[far_idx] = empty_cluster_id

            weight_in_clusters[empty_cluster_id] = 1
            weight_in_clusters[old_cluster_id] -= 1

            break


def constrained_iter(
        X,
        cluster_sizes,
        centers,
        centers_new,
        weight_in_clusters,
        labels,
        center_shift,
        n_threads,
        update_centers=True
):
    cost = (centers ** 2).sum(1) - 2 * X @ centers.T

    if cluster_sizes is None or cluster_sizes.shape[0] == 0:
        # no constraints (regular k-means)
        new_labels = cost.argmin(1)
    elif cluster_sizes.shape[0] == centers.shape[0]:
        # complete constraints
        plan = ot.emd(
            np.ones(X.shape[0]),
            cluster_sizes,
            cost[:, :cluster_sizes.shape[0]],
            numThreads=n_threads)
        new_labels = np.argmax(plan, 1)
    else:
        # partial constraints
        plan = ot.partial.partial_wasserstein(
            np.ones(X.shape[0]),
            cluster_sizes,
            cost[:, :cluster_sizes.shape[0]],
            m=np.sum(cluster_sizes),
            numThreads=n_threads
        )
        new_labels = np.argmax(plan, 1)
        unassigned_mask = (plan.sum(1) == 0)
        unassigned_labels = cluster_sizes.shape[0] + cost[unassigned_mask, cluster_sizes.shape[0]:].argmin(1)
        new_labels[unassigned_mask] = unassigned_labels

    np.copyto(labels, new_labels)

    if update_centers:
        for l in range(centers.shape[0]):
            mask = labels == l
            weights = np.sum(mask)
            if weights != 0:
                centers_new[l] = np.sum(X[mask], 0) / weights
            weight_in_clusters[l] = weights

        _relocate_empty_clusters_dense(
            X, cluster_sizes.shape[0], centers_new, weight_in_clusters, labels
        )
        np.copyto(center_shift, ((centers_new - centers) ** 2).sum(1) ** .5)


def _kmeans_single_constrained(
        X,
        cluster_sizes,
        centers_init,
        max_iter=300,
        verbose=False,
        tol=1e-4,
        n_threads=1,
):
    n_clusters = centers_init.shape[0]

    # Buffers to avoid new allocations at each iteration.
    centers = centers_init
    centers_new = np.zeros_like(centers)
    labels = np.full(X.shape[0], -1, dtype=np.int32)
    labels_old = labels.copy()
    weight_in_clusters = np.zeros(n_clusters, dtype=X.dtype)
    center_shift = np.zeros(n_clusters, dtype=X.dtype)

    if sp.issparse(X):
        _inertia = _inertia_sparse
    else:
        _inertia = _inertia_dense


    for i in range(max_iter):
        constrained_iter(
            X,
            cluster_sizes,
            centers,
            centers_new,
            weight_in_clusters,
            labels,
            center_shift,
            n_threads,
        )

        if verbose:
            inertia = _inertia(X, np.ones(X.shape[0]), centers, labels, n_threads)
            print(f"Iteration {i}, inertia {inertia}.")

        centers, centers_new = centers_new, centers

        if np.array_equal(labels, labels_old):
            # First check the labels for strict convergence.
            if verbose:
                print(f"Converged at iteration {i}: strict convergence.")
            break
        else:
            # No strict convergence, check for tol based convergence.
            center_shift_tot = (center_shift ** 2).sum()
            if center_shift_tot <= tol:
                if verbose:
                    print(
                        f"Converged at iteration {i}: center shift "
                        f"{center_shift_tot} within tolerance {tol}."
                    )
                break

        labels_old[:] = labels

    inertia = _inertia(X, np.ones(X.shape[0]), centers, labels, n_threads)

    return labels, inertia, centers, i + 1


def _labels_inertia(X, cluster_sizes, centers, n_threads=1, return_inertia=True):
    n_samples = X.shape[0]
    n_clusters = centers.shape[0]

    labels = np.full(n_samples, -1, dtype=np.int32)
    center_shift = np.zeros(n_clusters, dtype=centers.dtype)

    if sp.issparse(X):
        _labels = constrained_iter
        _inertia = _inertia_sparse
    else:
        _labels = constrained_iter
        _inertia = _inertia_dense

    _labels(
        X,
        cluster_sizes,
        centers,
        centers_new=None,
        weight_in_clusters=None,
        labels=labels,
        center_shift=center_shift,
        n_threads=n_threads,
        update_centers=False,
    )

    if return_inertia:
        inertia = _inertia(X, np.ones(X.shape[0]), centers, labels, n_threads)
        return labels, inertia

    return labels


def _labels_inertia_threadpool_limit(
        X, cluster_sizes, centers, n_threads=1, return_inertia=True
):
    with threadpool_limits(limits=1, user_api="blas"):
        result = _labels_inertia(X, cluster_sizes, centers, n_threads, return_inertia)

    return result


class ConstrainedKMeans(
    ClassNamePrefixFeaturesOutMixin, TransformerMixin, ClusterMixin, BaseEstimator, ABC, CBase
):
    """Perform K-means clustering algorithm with cluster size constraints.

    Parameters
    ----------

    n_clusters : int, default=8
        The number of clusters to form as well as the number of
        centroids to generate.

    cluster_sizes : array-like of shape (n_constraints,), default=None
        The constraints for the cluster sizes. If `None`, we retrieve
        the classical Lloyd algorithm. The constraints can either be
        exhaustive (n_constraints == n_clusters) or partial
        (n_constraints < n_clusters).

    init : {'k-means++', 'random'}, callable or array-like of shape \
            (n_clusters, n_features), default='k-means++'
        Method for initialization:

        * 'k-means++' : selects initial cluster centroids using sampling \
            based on an empirical probability distribution of the points' \
            contribution to the overall inertia. This technique speeds up \
            convergence. The algorithm implemented is "greedy k-means++". It \
            differs from the vanilla k-means++ by making several trials at \
            each sampling step and choosing the best centroid among them.

        * 'random': choose `n_clusters` observations (rows) at random from \
        data for the initial centroids.

        * If an array is passed, it should be of shape (n_clusters, n_features)\
        and gives the initial centers.

        * If a callable is passed, it should take arguments X, n_clusters and a\
        random state and return an initialization.

    n_init : int, default=10
        Number of times the k-means algorithm is run with different centroid
        seeds. The final results will be the best output of `n_init` consecutive runs
        in terms of inertia.

    max_iter : int, default=300
        Maximum number of iterations of the k-means algorithm for a
        single run.

    tol : float, default=1e-4
        Relative tolerance with regards to Frobenius norm of the difference
        in the cluster centers of two consecutive iterations to declare
        convergence.

    verbose : int, default=0
        Verbosity mode.

    random_state : int, RandomState instance or None, default=None
        Determines random number generation for centroid initialization. Use
        an int to make the randomness deterministic.

    copy_x : bool, default=True
        When pre-computing distances it is more numerically accurate to center
        the data first. If copy_x is True (default), then the original data is
        not modified. If False, the original data is modified, and put back
        before the function returns, but small numerical differences may be
        introduced by subtracting and then adding the data mean. Note that if
        the original data is not C-contiguous, a copy will be made even if
        copy_x is False. If the original data is sparse, but not in CSR format,
        a copy will be made even if copy_x is False.

    Attributes
    ----------
    cluster_centers_ : ndarray of shape (n_clusters, n_features)
        Coordinates of cluster centers. If the algorithm stops before fully
        converging (see ``tol`` and ``max_iter``), these will not be
        consistent with ``labels_``.

    labels_ : ndarray of shape (n_samples,)
        Labels of each point

    inertia_ : float
        Sum of squared distances of samples to their closest cluster center,
        weighted by the sample weights if provided.

    n_iter_ : int
        Number of iterations run.

    Examples
    --------

    >>> from ccluster.size import ConstrainedKMeans
    >>> import numpy as np
    >>> X = np.array([[1, 2], [1, 4], [1, 0],
    >>>                [10, 2], [10, 4], [10, 0]])
    >>> kmeans = ConstrainedKMeans(n_clusters=2, cluster_sizes=[2, 4], random_state=0, n_init=10).fit(X)
    >>> kmeans.labels_
    array([1, 1, 1, 0, 0, 1])
    >>> kmeans.predict([[0, 0], [12, 3]], [1, 1])
    array([1, 0], dtype=int32)
    >>>  kmeans.cluster_centers_
    array([[10.  ,  3.  ],
           [ 3.25,  1.5 ]])
    """

    _parameter_constraints: dict = {
        "n_clusters": [Interval(Integral, 1, None, closed="left")],
        "cluster_sizes": ["array-like", None],
        "init": [StrOptions({"k-means++", "random"}), callable, "array-like"],
        "n_init": [
            StrOptions({"auto"}),
            Hidden(StrOptions({"warn"})),
            Interval(Integral, 1, None, closed="left"),
        ],
        "max_iter": [Interval(Integral, 1, None, closed="left")],
        "tol": [Interval(Real, 0, None, closed="left")],
        "verbose": ["verbose"],
        "random_state": ["random_state"],
        "copy_x": ["boolean"],
    }

    def __init__(
            self,
            n_clusters,
            cluster_sizes,
            *,
            init="k-means++",
            n_init=10,
            max_iter=300,
            tol=1e-4,
            verbose=0,
            random_state=None,
            copy_x=True,
    ):
        self.n_clusters = n_clusters
        self.init = init
        self.max_iter = max_iter
        self.tol = tol
        self.n_init = n_init
        self.verbose = verbose
        self.random_state = random_state
        self.copy_x = copy_x
        # n_clusters and cluster_sizes
        self.cluster_sizes = self._check_cluster_size(cluster_sizes)

    def _validate_center_shape(self, X, centers):
        """Check if centers is compatible with X and n_clusters."""
        if centers.shape[0] != self.n_clusters:
            raise ValueError(
                f"The shape of the initial centers {centers.shape} does not "
                f"match the number of clusters {self.n_clusters}."
            )
        if centers.shape[1] != X.shape[1]:
            raise ValueError(
                f"The shape of the initial centers {centers.shape} does not "
                f"match the number of features of the data {X.shape[1]}."
            )

    def _check_params_vs_input(self, X):
        # n_clusters
        if X.shape[0] < self.n_clusters:
            raise ValueError(
                f"n_samples={X.shape[0]} should be >= n_clusters={self.n_clusters}."
            )
        self._check_cluster_size_vs_input(X)

        # tol
        self._tol = _tolerance(X, self.tol)

        # n-init
        self._n_init = self.n_init

        if _is_arraylike_not_scalar(self.init) and self._n_init != 1:
            warnings.warn(
                (
                    "Explicit initial center position passed: performing only"
                    f" one init in {self.__class__.__name__} instead of "
                    f"n_init={self._n_init}."
                ),
                RuntimeWarning,
                stacklevel=2,
            )
            self._n_init = 1



    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y=None):
        """Compute k-means clustering.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Training instances to cluster. It must be noted that the data
            will be converted to C ordering, which will cause a memory
            copy if the given data is not C-contiguous.
            If a sparse matrix is passed, a copy will be made if it's not in
            CSR format.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        self : object
            Fitted estimator.
        """
        X = self._validate_data(
            X,
            accept_sparse="csr",
            dtype=[np.float64, np.float32],
            order="C",
            copy=self.copy_x,
            accept_large_sparse=False,
        )

        self._check_params_vs_input(X)

        random_state = check_random_state(self.random_state)
        self._n_threads = _openmp_effective_n_threads()

        # Validate init array
        init = self.init
        init_is_array_like = _is_arraylike_not_scalar(init)
        if init_is_array_like:
            init = check_array(init, dtype=X.dtype, copy=True, order="C")
            self._validate_center_shape(X, init)

        # subtract of mean of x for more accurate distance computations
        if not sp.issparse(X):
            X_mean = X.mean(axis=0)
            # The copy was already done above
            X -= X_mean

            if init_is_array_like:
                init -= X_mean

        # precompute squared norms of data points
        x_squared_norms = row_norms(X, squared=True)

        kmeans_single = _kmeans_single_constrained
        self._check_mkl_vcomp(X, X.shape[0])

        best_inertia, best_labels = None, None

        for i in range(self._n_init):
            # Initialize centers
            centers_init = self._init_centroids(
                X,
                x_squared_norms=x_squared_norms,
                init=init,
                random_state=random_state,
            )
            if self.verbose:
                print("Initialization complete")

            # run a k-means once
            labels, inertia, centers, n_iter_ = kmeans_single(
                X,
                self.cluster_sizes,
                centers_init,
                max_iter=self.max_iter,
                verbose=self.verbose,
                tol=self._tol,
                n_threads=self._n_threads,
            )

            # determine if these results are the best so far
            # we chose a new run if it has a better inertia and the clustering is
            # different from the best so far (it's possible that the inertia is
            # slightly better even if the clustering is the same with potentially
            # permuted labels, due to rounding errors)
            if best_inertia is None or (
                    inertia < best_inertia
                    and not _is_same_clustering(labels, best_labels, self.n_clusters)
            ):
                best_labels = labels
                best_centers = centers
                best_inertia = inertia
                best_n_iter = n_iter_

        if not sp.issparse(X):
            if not self.copy_x:
                X += X_mean
            best_centers += X_mean

        distinct_clusters = len(set(best_labels))
        if distinct_clusters < self.n_clusters:
            warnings.warn(
                "Number of distinct clusters ({}) found smaller than "
                "n_clusters ({}). Consider specifying a full cluster "
                "size distribution.".format(distinct_clusters, self.n_clusters),
                ConvergenceWarning,
                stacklevel=2,
            )

        self.cluster_centers_ = best_centers
        self._n_features_out = self.cluster_centers_.shape[0]
        self.labels_ = best_labels
        self.inertia_ = best_inertia
        self.n_iter_ = best_n_iter
        return self

    def _init_centroids(
            self,
            X,
            x_squared_norms,
            init,
            random_state,
            init_size=None,
            n_centroids=None,
    ):
        n_samples = X.shape[0]
        n_clusters = self.n_clusters if n_centroids is None else n_centroids

        if init_size is not None and init_size < n_samples:
            init_indices = random_state.randint(0, n_samples, init_size)
            X = X[init_indices]
            x_squared_norms = x_squared_norms[init_indices]
            n_samples = X.shape[0]

        if isinstance(init, str) and init == "k-means++":
            centers, _ = kmeans_plusplus(
                X,
                n_clusters,
                random_state=random_state,
                x_squared_norms=x_squared_norms,
            )
        elif isinstance(init, str) and init == "random":
            seeds = random_state.choice(
                n_samples,
                size=n_clusters,
                replace=False,
            )
            centers = X[seeds]
        elif _is_arraylike_not_scalar(self.init):
            centers = init
        elif callable(init):
            centers = init(X, n_clusters, random_state=random_state)
            centers = check_array(centers, dtype=X.dtype, copy=False, order="C")
            self._validate_center_shape(X, centers)

        if sp.issparse(centers):
            centers = centers.toarray()

        return centers

    def _check_test_data(self, X):
        X = self._validate_data(
            X,
            accept_sparse="csr",
            reset=False,
            dtype=[np.float64, np.float32],
            order="C",
            accept_large_sparse=False,
        )
        return X

    def fit_predict(self, X, y=None):
        """Compute cluster centers and predict cluster index for each sample.

        Convenience method; equivalent to calling fit(X) followed by
        predict(X).

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            New data to transform.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            Index of the cluster each sample belongs to.
        """
        return self.fit(X).labels_

    def predict(self, X, cluster_sizes=None):
        """Predict the closest cluster each sample in X belongs to.

        In the vector quantization literature, `cluster_centers_` is called
        the code book and each value returned by `predict` is the index of
        the closest code in the code book.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            New data to predict.
        cluster_sizes: ndarray of shape (n_constraints,)
            The number of points to assign to each constrained cluster.
        Returns
        -------
        labels : ndarray of shape (n_samples,)
            Index of the cluster each sample belongs to.
        """
        check_is_fitted(self)

        old_cluster_size = self.cluster_sizes
        self.cluster_sizes = cluster_sizes

        X = self._check_test_data(X)
        self.cluster_sizes = self._check_cluster_size(self.cluster_sizes)

        self._check_cluster_size_vs_input(X)

        labels = _labels_inertia_threadpool_limit(
            X,
            self.cluster_sizes,
            self.cluster_centers_,
            n_threads=self._n_threads,
            return_inertia=False,
        )

        self.cluster_sizes = old_cluster_size
        return labels

    def fit_transform(self, X, y=None):
        """Compute clustering and transform X to cluster-distance space.

        Equivalent to fit(X).transform(X), but more efficiently implemented.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            New data to transform.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        X_new : ndarray of shape (n_samples, n_clusters)
            X transformed in the new space.
        """
        return self.fit(X)._transform(X)

    def transform(self, X):
        """Transform X to a cluster-distance space.

        In the new space, each dimension is the distance to the cluster
        centers. Note that even if X is sparse, the array returned by
        `transform` will typically be dense.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            New data to transform.

        Returns
        -------
        X_new : ndarray of shape (n_samples, n_clusters)
            X transformed in the new space.
        """
        check_is_fitted(self)

        X = self._check_test_data(X)
        return self._transform(X)

    def _transform(self, X):
        return euclidean_distances(X, self.cluster_centers_)

    def score(self, X, y=None):
        """Opposite of the value of X on the K-means objective.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            New data.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        score : float
            Opposite of the value of X on the K-means objective.
        """
        check_is_fitted(self)

        X = self._check_test_data(X)
        _, scores = _labels_inertia_threadpool_limit(
            X, self.cluster_centers_, self._n_threads
        )
        return -scores

    def _check_cluster_size_vs_input(self, X):
        # cluster-size
        n_free_clusters = self.n_clusters - self.cluster_sizes.shape[0]
        if np.sum(self.cluster_sizes) + n_free_clusters > X.shape[0]:
            raise ValueError(
                f"n_samples should be >= than the sum of cluster_sizes and n_unconstrained. "
                f"n_unconstrained is the number of unspecified cluster sizes."
            )
        if self.cluster_sizes.shape[0] == self.n_clusters:
            if np.sum(self.cluster_sizes) != X.shape[0]:
                raise ValueError(
                    f"Length of cluster_sizes should be equal to n_clusters when the sum of cluster_sizes is "
                    f"different from n_samples."
                )

    def _warn_mkl_vcomp(self, n_active_threads):
        """Warn when vcomp and mkl are both present"""
        warnings.warn(
            "KMeans is known to have a memory leak on Windows "
            "with MKL, when there are less chunks than available "
            "threads. You can avoid it by setting the environment"
            f" variable OMP_NUM_THREADS={n_active_threads}."
        )

    def _check_mkl_vcomp(self, X, n_samples):
        """Check when vcomp and mkl are both present"""
        # The BLAS call inside a prange in constrained_iter_chunked_dense is known to
        # cause a small memory leak when there are less chunks than the number
        # of available threads. It only happens when the OpenMP library is
        # vcomp (microsoft OpenMP) and the BLAS library is MKL. see #18653
        if sp.issparse(X):
            return

        n_active_threads = int(np.ceil(n_samples / CHUNK_SIZE))
        if n_active_threads < self._n_threads:
            modules = threadpool_info()
            has_vcomp = "vcomp" in [module["prefix"] for module in modules]
            has_mkl = ("mkl", "intel") in [
                (module["internal_api"], module.get("threading_layer", None))
                for module in modules
            ]
            if has_vcomp and has_mkl:
                self._warn_mkl_vcomp(n_active_threads)
