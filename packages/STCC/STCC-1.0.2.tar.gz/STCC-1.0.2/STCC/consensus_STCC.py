import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
from cvxopt import matrix, solvers


def convert_labels_to_numeric(df):
    """
    Convert character labels to numeric labels.
    """
    label_mapping = {}
    numeric_df = df.copy()

    for column in df.columns:
        unique_labels = df[column].unique()
        mapping = {label: idx for idx, label in enumerate(unique_labels)}
        label_mapping[column] = mapping
        numeric_df[column] = df[column].map(mapping)

    return numeric_df, label_mapping


def consensus_STCC(df, n_clusters=None, methods='wNMF-based', maxiter_em=100, eps_em=0.001, seed=2024):
    '''
    :param df: a data frame representing the clustering results, the rows represent samples, and the columns represent different situations
    :param methods='Average-based' or methods='Onehot-based' or methods='NMF-based' or methods='wNMF-based'
    :param n_clusters: number of principal components for NMF, if None, will be determined automatically
    :param maxiter_em: the maximum number of iterations, only useful when methods='NMF-based' or 'wNMF-based'
    :param eps_em: threshold, only useful when methods='NMF-based' or 'wNMF-based'
    :param seed: random number seed
    '''
    # Validate data input
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame.")

    if df.isnull().values.any():
        raise ValueError("Input data contains missing values.")

    # Convert character labels to numerical labels
    df, label_mapping = convert_labels_to_numeric(df)

    # Determine the number of clusters (n_clusters)
    if n_clusters is None:
        from sklearn.metrics import silhouette_score
        sil_scores = []
        for k in range(2, min(11, df.shape[0])):
            kmeans = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(df.T)
            sil_scores.append(silhouette_score(df.T, kmeans.labels_))
        n_clusters = sil_scores.index(max(sil_scores)) + 2
        print(f'The automatically determined k is {n_clusters}')

    # Compute the connectivity matrices and calculate their weighted sum (with a weight of 1/T)
    n = len(df)
    matrix_sum = np.zeros(shape=(n, n))
    matrix_list = []
    for i in df.columns:
        labels = df[i].tolist()
        temp = np.zeros(shape=(n, n))
        for i in range(n):
            for j in range(n)[i + 1:]:
                if labels[i] == labels[j]:
                    temp[i, j] = temp[j, i] = 1
        matrix_sum += temp
        matrix_list.append(temp)
    matrix_mean = matrix_sum / df.shape[1]

    if methods == 'Average-based':
        # Perform k-means clustering on the matrix_mean
        kmeans = KMeans(n_clusters, random_state=seed, n_init=10)
        kmeans.fit(matrix_mean)
        labels_consensus = kmeans.labels_
    elif methods == 'Onehot-based':
        # Constructing a hypergraph matrix
        k = n_clusters
        matrix_all = np.zeros(shape=(1, n))
        for i in df.columns:
            temp = np.zeros(shape=(k, n))
            for j in range(n):
                labels = df[i].tolist()
                if labels[j] >= k:
                    labels[j] = k - 1
                temp[labels[j], j] = 1
            matrix_all = np.vstack((matrix_all, temp))
        matrix_all = matrix_all[1:, :]

        # Perform k-means clustering on matrix_all
        kmeans = KMeans(n_clusters, random_state=seed, n_init=10)
        kmeans.fit(matrix_all.T)
        labels_consensus = kmeans.labels_
    elif methods == 'NMF-based':
        try:
            # Apply Non-negative Matrix Factorization (NMF) on matrix_mean
            model = NMF(n_components=n_clusters, init='random', solver='mu', random_state=seed, max_iter=10000)
            W = model.fit_transform(matrix_mean)
            H = model.components_

            H_init = (W + H.T) / 2
            H_hat = np.dot(H_init, (np.dot(H_init.T, H_init)) ** (-1 / 2))
            D = np.diag(np.diagonal(np.dot(H_init.T, H_init)))
            U0 = np.dot(np.dot(H_hat, D), H_hat.T)

            # Solve for H_hat (n*n_clusters) and D through the multiplicative update rules of NMF
            diff = []
            diff.append(np.linalg.norm(matrix_mean - U0))
            for i in range(maxiter_em):
                # print(f"**********This is {i}th iteration**********")
                if len(diff) > 1 and ((abs(diff[-1] - diff[-2]) / abs(diff[-2])) < eps_em):
                    break
                else:
                    H_update = np.multiply(H_hat, np.sqrt(
                        np.dot(np.dot(matrix_mean, H_hat), D) / np.dot(np.dot(np.dot(H_hat, H_hat.T), matrix_mean),
                                                                       np.dot(H_hat, D))))
                    D_update = np.multiply(D, np.sqrt(
                        np.dot(np.dot(H_hat.T, matrix_mean), H_hat) / np.dot(np.dot(np.dot(H_hat.T, H_hat), D),
                                                                             np.dot(H_hat.T, H_hat))))
                    U_update = np.dot(np.dot(H_update, D_update), H_update.T)
                    diff.append(np.linalg.norm(matrix_mean - U_update))
                    H_hat = H_update
                    D = D_update
            # Assign the cluster labels based on the index of the maximum value in each row of H_hat
            labels_nmf = []
            for i in range(len(H_hat)):
                labels_nmf.append(np.argmax(H_hat[i]))
            labels_consensus = labels_nmf

        except Exception as e:
            raise ValueError(f"NMF step failed: {e}")

    elif methods == 'wNMF-based':
        try:
            model = NMF(n_components=n_clusters, init='random', solver='mu', random_state=seed, max_iter=10000)
            W = model.fit_transform(matrix_mean)
            H = model.components_

            H_init = (W + H.T) / 2
            H_hat = np.dot(H_init, (np.dot(H_init.T, H_init)) ** (-1 / 2))
            D = np.diag(np.diagonal(np.dot(H_init.T, H_init)))
            U0 = np.dot(np.dot(H_hat, D), H_hat.T)

            # Step 1: Fix w (w = 1/T) and solve for H_hat
            diff = []
            diff.append(np.linalg.norm(matrix_mean - U0))
            for i in range(maxiter_em):
                # print(f"**********This is {i}th iteration**********")
                if len(diff) > 1 and ((abs(diff[-1] - diff[-2]) / abs(diff[-2])) < eps_em):
                    break
                else:
                    H_update = np.multiply(H_hat, np.sqrt(
                        np.dot(np.dot(matrix_mean, H_hat), D) / np.dot(np.dot(np.dot(H_hat, H_hat.T), matrix_mean),
                                                                       np.dot(H_hat, D))))
                    D_update = D
                    U_update = np.dot(np.dot(H_update, D_update), H_update.T)
                    diff.append(np.linalg.norm(matrix_mean - U_update))
                    H_hat = H_update

            # Initialize result variable
            result = None

            # Step 2: Fix H_hat and solve for w (a quadratic programming optimization problem with T linear constraints)
            p = np.ones((len(matrix_list), len(matrix_list)))
            for i in range(len(matrix_list)):
                for j in range(len(matrix_list)):
                    p[i, j] = p[j, i] = np.multiply(matrix_list[i], matrix_list[j]).sum()
            q = list()
            for i in range(df.shape[1]):
                q.append((-2 * (np.dot(np.dot(H_hat.T, matrix_list[i]), H_hat))).sum())
            G = -np.identity(len(matrix_list))
            h = np.zeros((len(matrix_list), 1))
            A = np.ones((1, len(matrix_list)))
            b = matrix([1.0])
            result = solvers.qp(matrix(p), matrix(q), matrix(G), matrix(h), matrix(A), b)  # result['x']即为权重
        except:
            # If solvers.qp fails, try different random seeds
            seed_list = np.random.randint(0, 10000, 10)
            for seed in seed_list:
                try:
                    model = NMF(n_components=n_clusters, init='random', solver='mu', random_state=seed, max_iter=10000)
                    W = model.fit_transform(matrix_mean)
                    H = model.components_

                    H_init = (W + H.T) / 2
                    H_hat = np.dot(H_init, (np.dot(H_init.T, H_init)) ** (-1 / 2))
                    D = np.diag(np.diagonal(np.dot(H_init.T, H_init)))
                    U0 = np.dot(np.dot(H_hat, D), H_hat.T)

                    # Step 1: Fix w (w = 1/T) and solve for H_hat
                    diff = []
                    diff.append(np.linalg.norm(matrix_mean - U0))
                    for i in range(maxiter_em):
                        # print(f"**********This is {i}th iteration**********")
                        if len(diff) > 1 and ((abs(diff[-1] - diff[-2]) / abs(diff[-2])) < eps_em):
                            break
                        else:
                            H_update = np.multiply(H_hat, np.sqrt(np.dot(np.dot(matrix_mean, H_hat), D) / np.dot(
                                np.dot(np.dot(H_hat, H_hat.T), matrix_mean), np.dot(H_hat, D))))
                            D_update = D
                            U_update = np.dot(np.dot(H_update, D_update), H_update.T)
                            diff.append(np.linalg.norm(matrix_mean - U_update))
                            H_hat = H_update

                    # Initialize result variable
                    result = None

                    # Step 2: Fix H_hat and solve for w (a quadratic programming optimization problem with T linear constraints)
                    p = np.ones((len(matrix_list), len(matrix_list)))
                    for i in range(len(matrix_list)):
                        for j in range(len(matrix_list)):
                            p[i, j] = p[j, i] = np.multiply(matrix_list[i], matrix_list[j]).sum()
                    q = list()
                    for i in range(df.shape[1]):
                        q.append((-2 * (np.dot(np.dot(H_hat.T, matrix_list[i]), H_hat))).sum())
                    G = -np.identity(len(matrix_list))
                    h = np.zeros((len(matrix_list), 1))
                    A = np.ones((1, len(matrix_list)))
                    b = matrix([1.0])
                    result = solvers.qp(matrix(p), matrix(q), matrix(G), matrix(h), matrix(A), b)  # result['x']即为权重
                    break
                except Exception as e:
                    print(f"Retry with seed {seed} failed: {e}")
                    continue

        # Check if result is properly defined
        if result is None:
            print("Quadratic programming problem could not be solved. Using uniform weights as fallback.")
            weights = np.full(len(matrix_list), 1.0 / len(matrix_list))
        else:
            weights = np.array(result['x']).flatten()

        # Use the obtained weights to compute the weighted sum of the T connectivity matrices,
        # resulting in the final matrix (matrix_weight)
        matrix_weigh = np.zeros(shape=(n, n))
        for i in range(len(matrix_list)):
            matrix_weigh += weights[i] * matrix_list[i]

        # Perform k-means clustering on matrix_weight to obtain the final labels
        kmeans = KMeans(n_clusters, random_state=seed, n_init=10)
        kmeans.fit(matrix_weigh.T)
        labels_consensus = kmeans.labels_

        # Calculate the contribution of each clustering algorithm
        contributions = weights / weights.sum()
    else:
        raise ValueError("Invalid method. Choose from 'Average-based', 'Onehot-based', 'NMF-based', 'wNMF-based'")

    if methods == 'wNMF-based':
        return labels_consensus, contributions
    else:
        return labels_consensus