from loguru import logger
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from joblib import dump



def train_model():
    '''train LR model using generated data'''
    X, y = make_blobs(n_samples=100, centers=2, n_features=2, random_state=0)
    logger.debug('data.shape: {}'.format(X.shape))


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30)

    clf = LogisticRegression(solver='lbfgs')

    clf.fit(X_train, y_train)

    logger.debug('Accuracy: {}'.format(clf.score(X_test, y_test)))

    dump(clf, 'lr_model.joblib')


if __name__ == '__main__':
    logger.debug("Training LR model")
    train_model()

