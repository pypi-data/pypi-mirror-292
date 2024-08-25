import numpy as np
from sklearn.utils.validation import check_non_negative, check_array


class CBase:

    def _check_cluster_size(self, cluster_size_original):
        if cluster_size_original is None:
            cluster_size_original = []

        cluster_size = check_array(
            cluster_size_original,
            force_all_finite=True,
            ensure_2d=False,
            dtype=np.int32,
            input_name='cluster_size',
            ensure_min_samples=0
        )
        if cluster_size.shape[0] != 0:
            check_non_negative(cluster_size, 'cluster_size')

            if not np.array_equal(cluster_size, cluster_size_original):
                raise ValueError(
                    f"cluster_size should not contain non-integer values."
                )
            if np.any(cluster_size == 0):
                raise ValueError(
                    f"cluster_size should not contain zeros."
                )
            if self.n_clusters < cluster_size.shape[0]:
                raise ValueError(
                    f"length of cluster_size={cluster_size.shape[0]} should be <= "
                    f" n_clusters={self.n_clusters}."
                )

        return cluster_size