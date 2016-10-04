#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import edward as ed
import numpy as np
import tensorflow as tf

from edward.models import Normal
from scipy.stats import norm


def build_toy_dataset(N, noise_std=0.1):
  X = np.concatenate([np.linspace(0, 2, num=N / 2),
                      np.linspace(6, 8, num=N / 2)])
  y = 5.0 * X + norm.rvs(0, noise_std, size=N)
  X = X.reshape((N, 1))
  return X.astype(np.float32), y.astype(np.float32)


ed.set_seed(42)

N = 40  # num data points
D = 1  # num features

# DATA
X_train, y_train = build_toy_dataset(N)
X_test, y_test = build_toy_dataset(N)

# MODEL
X = ed.placeholder(tf.float32, [N, D], name='X')
beta = Normal(mu=tf.zeros(D), sigma=tf.ones(D), name='beta')
y = Normal(mu=ed.dot(X, beta), sigma=tf.ones(N), name='y')

# INFERENCE
qmu_mu = tf.Variable(tf.random_normal([D]))
qmu_sigma = tf.nn.softplus(tf.Variable(tf.random_normal([D])))
qbeta = Normal(mu=qmu_mu, sigma=qmu_sigma, name='qbeta')

data = {X: X_train, y: y_train}
inference = ed.MFVI({beta: qbeta}, data)
inference.run(n_iter=500, logdir='train')

# CRITICISM
y_post = ed.copy(y, {beta: qbeta.mean()})
# This is equivalent to
# y_post = Normal(mu=ed.dot(X, qbeta.mean()), sigma=tf.ones(N))

print("Mean squared error on test data:")
print(ed.evaluate('mean_squared_error', data={X: X_test, y_post: y_test}))
