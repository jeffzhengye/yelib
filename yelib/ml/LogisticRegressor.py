import numpy as np
from numpy import loadtxt, where, zeros, e, array, log, ones, append, linspace
from scipy.optimize import fmin_bfgs, check_grad

import sys
# sys.path.insert(0, '/data/Dropbox/python/scikit-learn')
import logging
from sklearn.linear_model import LinearRegression
from sklearn.base import RegressorMixin
from sklearn.feature_selection.selector_mixin import SelectorMixin
from sklearn.utils import as_float_array, atleast2d_or_csr, safe_asarray
from sklearn.utils.extmath import safe_sparse_dot
from numpy.linalg import norm
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error


logging.basicConfig(level=logging.INFO)

def sigmoid(X_):
    '''Compute the sigmoid function '''
    return 1.0 / (1.0 + np.exp(-X_))

def compute_cost(theta, X, y, C=0.,  normf=norm):
    '''
    Comput cost for logistic regression
        X : numpy array or sparse matrix of shape [n_samples,n_features]
            Training data
        y : numpy array of shape [n_samples, n_targets] n_targets =1
            Target values
        theta: [n_featrues, 1]

    '''
    try:
        theta = theta.reshape(len(theta), 1)
        m = y.size
        # print 'cost shape:', X.shape, theta.shape
        h = sigmoid(X.dot(theta))
        # h = h.reshape(len(h), 1)
        J = (.5 / m) * (h - y)**2
        # print 'cost:', J.sum()
        # print 'theta:', theta
        cost = J.sum() + 0.5 * C * normf(theta)
        logging.debug('cost:%f' % cost)
        return cost
    except Exception, e:
        print e

 
def compute_grad(theta, X, y, C=0.):
    #print theta.shape
    m = y.size
    theta = theta.reshape(len(theta), 1)
    grad = zeros(len(theta))

    h = sigmoid(X.dot(theta))
    h = h.reshape(len(h), 1)
    # print 'grad shape:', X.shape, theta.shape, (np.dot(X,theta)).shape, h.shape, y.shape
    delta = (h - y).ravel()
    
    grad = zeros(len(theta))
    for i in range(m):
        x_i = X[i,:].ravel()
        theta_by_xi = np.dot(theta.ravel(), x_i)
        # print theta_by_xi
        grad += delta[i]/((1 + np.exp(-theta_by_xi))**2) * (-x_i)
        # print sumdelta
    grad = (1.0 / m) * grad + C * theta.ravel()
    # print 'grad', grad.ravel()
    return  grad.ravel()

def test_grad():
    from sklearn.datasets import load_svmlight_file
    from sklearn.preprocessing import StandardScaler
    path = "./train.sample"
    X_train, y_train = load_svmlight_file(path)
    x_train = X_train.toarray()
    y_train = 1/(y_train + 1)
    y_train = y_train.reshape(len(y_train), 1)
    scaler = StandardScaler()
    xs_train = scaler.fit_transform(x_train)
    cost = lambda theta: compute_cost(theta, xs_train, y_train, C=0., normf=norm)
    grad = lambda theta: compute_grad(theta, xs_train, y_train, C=0.)
    for i in range(10):
        value = check_grad(cost, grad, np.random.randn(xs_train.shape[1]))
        print 'check%d: %f' %(i, value)

class LogisticRegressor(LinearRegression, SelectorMixin):
    """
    it is for regression, rather than for classfication (LogisticRegression is for classfication)
    """

    def __init__(self, penalty='l2', dual=True, tol=1e-4, C=1.0,
            fit_intercept=True, intercept_scaling=1, class_weight=None,
            random_state=None):
        self.C_ = C
        if penalty == 'l2':
            self.norm_ = norm
            print 'using l2'
        elif penalty == 'l1':
            self.norm_ = lambda X: norm(X, ord=1)
            print 'using l1'
        else:
            self.norm_ = norm
        super(LogisticRegressor, self).__init__()
    
    def fit(self, X, y):
        """
        Fit LogisticRegressor model.

        Parameters
        ----------
        X : numpy array or sparse matrix of shape [n_samples,n_features]
            Training data
        y : numpy array of shape [n_samples, n_targets]
            Target values
        n_jobs : The number of jobs to use for the computation.
            If -1 all CPUs are used. This will only provide speedup for
            n_targets > 1 and sufficient large problems

        Returns
        -------
        self : returns an instance of self.
        """
        self.X = safe_asarray(X)
        self.y = np.asarray(y)
        initial_theta = zeros(self.X.shape[1])
        cost = lambda theta: compute_cost(initial_theta, self.X, self.y, C=self.C_, normf=self.norm_)
        grad = lambda theta: compute_grad(self.coef_, self.X, self.y, C=self.C_)

        self.coef_ = fmin_bfgs(self.decorated_cost, initial_theta, fprime=self.decorated_grad)
        print 'check1:', check_grad(cost, grad, initial_theta)
        print 'check2:', check_grad(cost, grad, self.coef_)
        
        # self.coef_ = fmin_bfgs(self.decorated_cost, initial_theta)
        return self


    def predict(self, X):
        """Predict using the linear model

        Parameters
        ----------
        X : numpy array of shape [n_samples, n_features]

        Returns
        -------
        C : array, shape = [n_samples]
            Returns predicted values.
        """
        return self.sigmoid(X.dot(self.coef_.T))


    def sigmoid(self, X):
        '''Compute the sigmoid function '''
        return 1.0 / (1.0 + np.exp(-X))


def test_oned():
    x = np.arange(1,10, 0.3)
    y = sigmoid(x) - np.random.ranf()/10.
    xp = x.reshape(len(x),1)
    y = y.reshape(len(y), 1)
    #Initialize theta parameters
    initial_theta = zeros(xp.shape[1])
    print 'theta_initial:', initial_theta
    print 'xp, y theta shape :', xp.shape, y.shape, initial_theta.shape
    # decorated_cost(initial_theta)
    print compute_cost(initial_theta, xp, y)
    print compute_grad(initial_theta, xp, y)
    # reg = LogisticRegressor(penalty='l1', C=0.001)
    # reg.fit(xp, y)

    # reg1 = LogisticRegressor(penalty='l2', C=0.3)
    # reg1.fit(xp, y)
    # print res[1]
    # print 'optimal theta:', reg.coef_

    # import pylab as pl
    # pl.figure(1, figsize=(4, 3))
    # pl.clf()
    # pl.scatter(xp, y, color='black', zorder=20)
    # # print xp, predict(theta, xp)
    # pl.scatter(xp, reg.predict(xp), color='red', zorder=20)
    # pl.scatter(xp, reg1.predict(xp), color='green', zorder=20)
    # pl.show()

def test_muld():
    from sklearn.datasets import load_svmlight_file
    from sklearn.preprocessing import StandardScaler
    path = "./train.sample"
    X_train, y_train = load_svmlight_file(path)
    x_train = X_train.toarray()
    y_train = 1/(y_train + 1)
    y_train = y_train.reshape(len(y_train), 1)
    print 'y_train shape' , y_train.shape
    scaler = StandardScaler()
    xs_train = scaler.fit_transform(x_train)
    reg = LogisticRegressor(penalty='l2', C=0.5)
    reg.fit(xs_train, y_train)
    y_pred = reg.predict(xs_train)
    print mean_squared_error(y_pred, y_train)
    print y_train.ravel()
    print reg.score(xs_train, y_train)
    print reg.coef_


if __name__ == "__main__":
    test_grad()