"""Problem Set 6: PCA, Boosting, Haar Features, Viola-Jones."""
import numpy as np
import cv2
import os
import math

from helper_classes import WeakClassifier, VJ_Classifier


# assignment code
def load_images(folder, size=(32, 32)):
    """Load images to workspace.

    Args:
        folder (String): path to folder with images.
        size   (tuple): new image sizes

    Returns:
        tuple: two-element tuple containing:
            X (numpy.array): data matrix of flatten images
                             (row:observations, col:features) (float).
            y (numpy.array): 1D array of labels (int).
    """

    images_files = [f for f in os.listdir(folder) if f.endswith(".png")]
    img_number = len(images_files)
    X,y = [],[]
    for frame in images_files:
    	img = cv2.imread(os.path.join(folder, frame))
    	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    	# cv2.imshow('temp',img)
    	# cv2.waitKey(0)
    	# print(size)
    	size = tuple(size)
    	img_small = cv2.resize(img_gray, size)
    	# print(img_small.shape)
    	img_flat = img_small.flatten()
    	# print(img_flat.shape)
    	X.append(img_flat)
    	# print(np.shape(X))
    	label_temp = frame.split('.')[0][-2:]
    	# print(int(label_temp))
    	y.append(int(label_temp))
    X = np.asarray(X)
    y = np.asarray(y)
    return (X,y)
    # raise NotImplementedError


def split_dataset(X, y, p):
    """Split dataset into training and test sets.

    Let M be the number of images in X, select N random images that will
    compose the training data (see np.random.permutation). The images that
    were not selected (M - N) will be part of the test data. Record the labels
    accordingly.

    Args:
        X (numpy.array): 2D dataset.
        y (numpy.array): 1D array of labels (int).
        p (float): Decimal value that determines the percentage of the data
                   that will be the training data.

    Returns:
        tuple: Four-element tuple containing:
            Xtrain (numpy.array): Training data 2D array.
            ytrain (numpy.array): Training data labels.
            Xtest (numpy.array): Test data test 2D array.
            ytest (numpy.array): Test data labels.
    """

    # raise NotImplementedError
    M = len(X)
    N = int(M * p)
    permuted = np.random.permutation(M)
    Xtrain = X[:N]
    ytrain = y[:N]
    Xtest = X[N:]
    ytest = y[N:]
    return (Xtrain,ytrain,Xtest,ytest)


def get_mean_face(x):
    """Return the mean face.

    Calculate the mean for each column.

    Args:
        x (numpy.array): array of flattened images.

    Returns:
        numpy.array: Mean face.
    """

    # raise NotImplementedError
    mean_face = np.mean(x,axis=0)
    return mean_face



def pca(X, k):
    """PCA Reduction method.

    Return the top k eigenvectors and eigenvalues using the covariance array
    obtained from X.


    Args:
        X (numpy.array): 2D data array of flatten images (row:observations,
                         col:features) (float).
        k (int): new dimension space

    Returns:
        tuple: two-element tuple containing
            eigenvectors (numpy.array): 2D array with the top k eigenvectors.
            eigenvalues (numpy.array): array with the top k eigenvalues.
    """

    # raise NotImplementedError
    M = get_mean_face(X)
    C = X - M
    V = np.cov(C.transpose(), bias=True)
    V = V * X.shape[0]
    values,vectors = np.linalg.eigh(V)
    idx = values.argsort()[::-1] 
    evalues = values[idx]
    evectors = vectors[:,idx]
    # print(np.shape(evectors))
    # eigenvectors = np.dot(C,evectors)
    eigenvalues = evalues[:k]
    eigenvectors = evectors[:,:k]
    # norms = np.linalg.norm(eigenvectors,axis=0)
    # eigenvectors = eigenvectors / norms
    return (eigenvectors,eigenvalues)


class Boosting:
    """Boosting classifier.

    Args:
        X (numpy.array): Data array of flattened images
                         (row:observations, col:features) (float).
        y (numpy.array): Labels array of shape (observations, ).
        num_iterations (int): number of iterations
                              (ie number of weak classifiers).

    Attributes:
        Xtrain (numpy.array): Array of flattened images (float32).
        ytrain (numpy.array): Labels array (float32).
        num_iterations (int): Number of iterations for the boosting loop.
        weakClassifiers (list): List of weak classifiers appended in each
                               iteration.
        alphas (list): List of alpha values, one for each classifier.
        num_obs (int): Number of observations.
        weights (numpy.array): Array of normalized weights, one for each
                               observation.
        eps (float): Error threshold value to indicate whether to update
                     the current weights or stop training.
    """

    def __init__(self, X, y, num_iterations):
        self.Xtrain = np.float32(X)
        self.ytrain = np.float32(y)
        self.num_iterations = num_iterations
        self.weakClassifiers = []
        self.alphas = []
        self.num_obs,_ = np.shape(X)
        self.weights = np.array([1.0 / self.num_obs] * self.num_obs)  # uniform weights
        self.eps = 0.0001
        
    def train(self):
        """Implement the for loop shown in the problem set instructions."""
        # raise NotImplementedError
        for j in range(self.num_iterations):
        	sum_temp = np.sum(self.weights)
        	self.weights = self.weights / sum_temp
        	eps_temp = 0
        	wkc = WeakClassifier(self.Xtrain, self.ytrain, self.weights, self.eps)
        	wkc.train()
        	# self.weakClassifiers = (self.wkc.predict(self.Xtrain))
        	# print(np.shape(self.Xtrain))
        	predict_temp = []
        	for i in range(self.num_obs):
	        	predict_temp.append(wkc.predict(self.Xtrain[i]))
	        	index = self.ytrain[i] != predict_temp[i]
	        	eps_temp += index * self.weights[i]
	        self.weakClassifiers.append(wkc)
	        # print(np.shape(self.weakClassifiers))
	        self.alphas.append(0.5 * math.log((1.-eps_temp)/eps_temp))
	        # print(np.shape(self.weakClassifiers))
	        if eps_temp >= self.eps:
	        	for i in range(self.num_obs):
	        		self.weights[i] = self.weights[i] * math.exp((-1) * self.ytrain[i]*self.alphas[j]*wkc.predict(self.Xtrain[i]))
	        else:
	        	break



    def evaluate(self):
        """Return the number of correct and incorrect predictions.

        Use the training data (self.Xtrain) to obtain predictions. Compare
        them with the training labels (self.ytrain) and return how many
        where correct and incorrect.

        Returns:
            tuple: two-element tuple containing:
                correct (int): Number of correct predictions.
                incorrect (int): Number of incorrect predictions.
        """
        # raise NotImplementedError
        corr = 0
        inco = 0
        # self.train()
        # print(np.shape(self.weakClassifiers),np.shape(self.Xtrain))
        temp_y = self.predict(self.Xtrain)
        for i in range(self.num_obs):
        	if temp_y[i] == self.ytrain[i]: corr += 1
        	else: inco += 1 
        return (corr,inco)


    def predict(self, X):
        """Return predictions for a given array of observations.

        Use the alpha values stored in self.aphas and the weak classifiers
        stored in self.weakClassifiers.

        Args:
            X (numpy.array): Array of flattened images (observations).

        Returns:
            numpy.array: Predictions, one for each row in X.
        """
        # raise NotImplementedError
        values = []
        for j in range(len(self.alphas)):
        	predict_temp = []
        	for i in range(X.shape[0]):
        		x_temp = X[i,:]
        		predict_temp.append(self.weakClassifiers[j].predict(x_temp))
        	predict_temp = np.asarray(predict_temp)
        	# print(np.shape(predict_temp))
        	values.append(self.alphas[j]*predict_temp)
        out = np.sign(np.sum(values, axis=0))
        out = np.asarray(out.copy())
        return out


class HaarFeature:
    """Haar-like features.

    Args:
        feat_type (tuple): Feature type {(2, 1), (1, 2), (3, 1), (2, 2)}.
        position (tuple): (row, col) position of the feature's top left corner.
        size (tuple): Feature's (height, width)

    Attributes:
        feat_type (tuple): Feature type.
        position (tuple): Feature's top left corner.
        size (tuple): Feature's width and height.
    """

    def __init__(self, feat_type, position, size):
        self.feat_type = feat_type
        self.position = position
        self.size = size

    def _create_two_horizontal_feature(self, shape):
        """Create a feature of type (2, 1).

        Use int division to obtain half the height.

        Args:
            shape (tuple):  Array numpy-style shape (rows, cols).

        Returns:
            numpy.array: Image containing a Haar feature. (uint8).
        """
        sh = self.size[0] // 2
       	(r,c) = self.position
       	(h,w) = self.size
        out_img = np.zeros(shape)
        out_img[r:(r+sh),c:(c+w)] = 255
        out_img[(r+sh):(r+h),c:(c+w)] = 126
        return out_img

        # raise NotImplementedError

    def _create_two_vertical_feature(self, shape):
        """Create a feature of type (1, 2).

        Use int division to obtain half the width.

        Args:
            shape (tuple):  Array numpy-style shape (rows, cols).

        Returns:
            numpy.array: Image containing a Haar feature. (uint8).
        """
        sw = self.size[1] // 2
       	(r,c) = self.position
       	(h,w) = self.size
        out_img = np.zeros(shape)
        out_img[r:(r+h),c:(c+sw)] = 255
        out_img[r:(r+h),(c+sw):(c+w)] = 126
        return out_img
        # raise NotImplementedError

    def _create_three_horizontal_feature(self, shape):
        """Create a feature of type (3, 1).

        Use int division to obtain a third of the height.

        Args:
            shape (tuple):  Array numpy-style shape (rows, cols).

        Returns:
            numpy.array: Image containing a Haar feature. (uint8).
        """
        sh = self.size[0] // 3
       	(r,c) = self.position
       	(h,w) = self.size
        out_img = np.zeros(shape)
        out_img[r:(r+sh),c:(c+w)] = 255
        out_img[(r+sh):(r+sh+sh),c:(c+w)] = 126
        out_img[(r+sh+sh):(r+h),c:(c+w)] = 255
        return out_img
        # raise NotImplementedError

    def _create_three_vertical_feature(self, shape):
        """Create a feature of type (1, 3).

        Use int division to obtain a third of the width.

        Args:
            shape (tuple):  Array numpy-style shape (rows, cols).

        Returns:
            numpy.array: Image containing a Haar feature. (uint8).
        """
        sw = self.size[1] // 3
       	(r,c) = self.position
       	(h,w) = self.size
        out_img = np.zeros(shape)
        out_img[r:(r+h),c:(c+sw)] = 255
        out_img[r:(r+h),(c+sw):(c+sw+sw)] = 126
        out_img[r:(r+h),(c+sw+sw):(c+w)] = 255
        return out_img
        # raise NotImplementedError

    def _create_four_square_feature(self, shape):
        """Create a feature of type (2, 2).

        Use int division to obtain half the width and half the height.

        Args:
            shape (tuple):  Array numpy-style shape (rows, cols).

        Returns:
            numpy.array: Image containing a Haar feature. (uint8).
        """
        sw = self.size[1] // 2
        sh = self.size[0] // 2
       	(r,c) = self.position
       	(h,w) = self.size
        out_img = np.zeros(shape)
        out_img[r:(r+sh),c:(c+sw)] = 126
        out_img[r:(r+sh),(c+sw):(c+w)] = 255
        out_img[(r+sh):(r+h),c:(c+sw)] = 255
        out_img[(r+sh):(r+h),(c+sw):(c+w)] = 126
        return out_img

        # raise NotImplementedError

    def preview(self, shape=(24, 24), filename=None):
        """Return an image with a Haar-like feature of a given type.

        Function that calls feature drawing methods. Each method should
        create an 2D zeros array. Each feature is made of a white area (255)
        and a gray area (126).

        The drawing methods use the class attributes position and size.
        Keep in mind these are in (row, col) and (height, width) format.

        Args:
            shape (tuple): Array numpy-style shape (rows, cols).
                           Defaults to (24, 24).

        Returns:
            numpy.array: Array containing a Haar feature (float or uint8).
        """

        if self.feat_type == (2, 1):  # two_horizontal
            X = self._create_two_horizontal_feature(shape)

        if self.feat_type == (1, 2):  # two_vertical
            X = self._create_two_vertical_feature(shape)

        if self.feat_type == (3, 1):  # three_horizontal
            X = self._create_three_horizontal_feature(shape)

        if self.feat_type == (1, 3):  # three_vertical
            X = self._create_three_vertical_feature(shape)

        if self.feat_type == (2, 2):  # four_square
            X = self._create_four_square_feature(shape)

        if filename is None:
            cv2.imwrite("output/{}_feature.png".format(self.feat_type), X)

        else:
            cv2.imwrite("output/{}.png".format(filename), X)

        return X

    def evaluate(self, ii):
        """Evaluates a feature's score on a given integral image.

        Calculate the score of a feature defined by the self.feat_type.
        Using the integral image and the sum / subtraction of rectangles to
        obtain a feature's value. Add the feature's white area value and
        subtract the gray area.

        For example, on a feature of type (2, 1):
        score = sum of pixels in the white area - sum of pixels in the gray area

        Keep in mind you will need to use the rectangle sum / subtraction
        method and not numpy.sum(). This will make this process faster and
        will be useful in the ViolaJones algorithm.

        Args:
            ii (numpy.array): Integral Image.

        Returns:
            float: Score value.
        """

        # raise NotImplementedError
        ii = ii.astype(np.float32)
        (r,c) = self.position
       	(h,w) = self.size
        if self.feat_type == (2, 1):  # two_horizontal
        	sh = self.size[0] // 2
        	A = ii[r-1][c-1]
        	B = ii[r-1][c+w-1]
        	C = ii[r+sh-1][c-1]
        	D = ii[r+sh-1][c+w-1]
        	sum1 = A + D - B - C
        	E = ii[r+h-1][c-1]
        	F = ii[r+h-1][c+w-1]
        	sum2 = C + F - E - D 
        	return (sum1 - sum2)

        if self.feat_type == (1, 2):  # two_vertical
        	sw = self.size[1] // 2
        	A = ii[r-1][c-1]
        	B = ii[r-1][c+sw-1]
        	C = ii[r+h-1][c-1]
        	D = ii[r+h-1][c+sw-1]
        	sum1 = A + D - B - C
        	E = ii[r-1][c+w-1]
        	F = ii[r+h-1][c+w-1]
        	sum2 = B + F - E - D
        	return (sum1 - sum2)
            

        if self.feat_type == (3, 1):  # three_horizontal
        	sh = self.size[0] // 3
        	A = ii[r-1][c-1]
        	B = ii[r-1][c+w-1]
        	C = ii[r+sh-1][c-1]
        	D = ii[r+sh-1][c+w-1]
        	sum1 = A + D - B - C
        	E = ii[r+sh+sh-1][c-1]
        	F = ii[r+sh+sh-1][c+w-1]
        	sum2 = C + F - E - D 
        	G = ii[r+h-1][c-1]
        	H = ii[r+h-1][c+w-1]
        	sum3 = E + H - F - G
        	return (sum1 - sum2 + sum3)
            

        if self.feat_type == (1, 3):  # three_vertical
        	sw = self.size[1] // 3
        	A = ii[r-1][c-1]
        	B = ii[r-1][c+sw-1]
        	C = ii[r+h-1][c-1]
        	D = ii[r+h-1][c+sw-1]
        	sum1 = A + D - B - C
        	E = ii[r-1][c+sw+sw-1]
        	F = ii[r+h-1][c+sw+sw-1]
        	sum2 = B + F - E - D
        	G = ii[r-1][c+w-1]
        	H = ii[r+h-1][c+w-1]
        	sum3 = E + H - G - F
        	return (sum1 - sum2 + sum3)
            

        if self.feat_type == (2, 2):  # four_square
        	sw = self.size[1] // 2
        	sh = self.size[0] // 2
        	A = ii[r-1][c-1]
        	B = ii[r-1][c+sw-1]
        	C = ii[r+sh-1][c-1]
        	D = ii[r+sh-1][c+sw-1]
        	sum1 = A + D - B - C
        	E = ii[r-1][c+w-1]
        	F = ii[r+sh-1][c+w-1]
        	sum2 = B + F - E - D
        	G = ii[r+h-1][c-1]
        	H = ii[r+h-1][c+sw-1]
        	sum3 = C + H - D - G
        	I = ii[r+h-1][c+w-1]
        	sum4 = D + I - F - H
        	return (sum2 + sum3 - sum1 - sum4)
            


def convert_images_to_integral_images(images):
    """Convert a list of grayscale images to integral images.

    Args:
        images (list): List of grayscale images (uint8 or float).

    Returns:
        (list): List of integral images.
    """

    # raise NotImplementedError
    img_num, H, W = np.shape(images)
    out_list = []
    for i in range(img_num):
    	temp_img = np.zeros((H,W))
    	for h in range(H):
    		for w in range(W):
    			temp_img[h,w] = np.sum(images[i][:(h+1),:(w+1)])
    	out_list.append(temp_img)
    return out_list



class ViolaJones:
    """Viola Jones face detection method

    Args:
        pos (list): List of positive images.
        neg (list): List of negative images.
        integral_images (list): List of integral images.

    Attributes:
        haarFeatures (list): List of haarFeature objects.
        integralImages (list): List of integral images.
        classifiers (list): List of weak classifiers (VJ_Classifier).
        alphas (list): Alpha values, one for each weak classifier.
        posImages (list): List of positive images.
        negImages (list): List of negative images.
        labels (numpy.array): Positive and negative labels.
    """
    def __init__(self, pos, neg, integral_images):
        self.haarFeatures = []
        self.integralImages = integral_images
        self.classifiers = []
        self.alphas = []
        self.posImages = pos
        self.negImages = neg
        self.labels = np.hstack((np.ones(len(pos)), -1*np.ones(len(neg))))

    def createHaarFeatures(self):
        # Let's take detector resolution of 24x24 like in the paper
        FeatureTypes = {"two_horizontal": (2, 1),
                        "two_vertical": (1, 2),
                        "three_horizontal": (3, 1),
                        "three_vertical": (1, 3),
                        "four_square": (2, 2)}

        haarFeatures = []
        for _, feat_type in FeatureTypes.items():
            for sizei in range(feat_type[0], 24 + 1, feat_type[0]):
                for sizej in range(feat_type[1], 24 + 1, feat_type[1]):
                    for posi in range(0, 24 - sizei + 1, 4):
                        for posj in range(0, 24 - sizej + 1, 4):
                            haarFeatures.append(
                                HaarFeature(feat_type, [posi, posj],
                                            [sizei-1, sizej-1]))
        self.haarFeatures = haarFeatures


    def train(self, num_classifiers):

        # Use this scores array to train a weak classifier using VJ_Classifier
        # in the for loop below.
        scores = np.zeros((len(self.integralImages), len(self.haarFeatures)))
        print(" -- compute all scores --")
        for i, im in enumerate(self.integralImages):
            scores[i, :] = [hf.evaluate(im) for hf in self.haarFeatures]

        weights_pos = np.ones(len(self.posImages), dtype='float') * 1.0 / (
                           2*len(self.posImages))
        weights_neg = np.ones(len(self.negImages), dtype='float') * 1.0 / (
                           2*len(self.negImages))
        weights = np.hstack((weights_pos, weights_neg))

        print(" -- select classifiers --")
        
        for i in range(num_classifiers):

            # TODO: Complete the Viola Jones algorithm

            sum_temp = np.sum(weights)
            weights = weights / sum_temp
            vjc = VJ_Classifier(scores, self.labels, weights, thresh=0, feat=0, polarity=1)
            vjc.train()
            error = vjc.error
            self.classifiers.append(vjc)

            beta = float(error) / (1. - error)
            for j in range(len(self.integralImages)):
            	if self.labels[j] == vjc.predict(scores[j]): weights[j] = weights[j] * beta
            	else: weights[j] = weights[j] 
            weights = np.asarray(weights)
            self.alphas.append(math.log((1.)/beta))
	        

            # raise NotImplementedError

    def predict(self, images):
        """Return predictions for a given list of images.

        Args:
            images (list of element of type numpy.array): list of images (observations).

        Returns:
            list: Predictions, one for each element in images.
        """

        ii = convert_images_to_integral_images(images)

        scores = np.zeros((len(ii), len(self.haarFeatures)))

        for i, x in enumerate(ii):
        # Populate the score location for each classifier 'clf' in
        # self.classifiers.
        	for clf in self.classifiers:
        # Obtain the Haar feature id from clf.feature
        		ind = clf.feature

        # Use this id to select the respective feature object from
        # self.haarFeatures
        		feature = self.haarFeatures[ind]

        # Add the score value to score[x, feature id] calling the feature's
        # evaluate function. 'x' is each image in 'ii'
        		scores[i, ind] = feature.evaluate(x)

        result = []

        # Append the results for each row in 'scores'. This value is obtained
        # using the equation for the strong classifier H(x).

        for x in scores:
            # TODO
            temp_sum = 0.
            for j in range(len(self.classifiers)):
            	temp_sum += self.alphas[j] * self.classifiers[j].predict(x)
            temp_alpha = 0.5 * np.sum(self.alphas)
            res = -1
            if temp_sum >= temp_alpha: 
            	res = 1
            result.append(res)
            # raise NotImplementedError

        return result

    def faceDetection(self, image, filename):
        """Scans for faces in a given image.

        Complete this function following the instructions in the problem set
        document.

        Use this function to also save the output image.

        Args:
            image (numpy.array): Input image.
            filename (str): Output image file name.

        Returns:
            None.
        """

        # raise NotImplementedError
        img_temp = np.copy(image)
        img_gray = cv2.cvtColor(img_temp,cv2.COLOR_BGR2GRAY)

        w,b = np.shape(img_gray)
        r = 24
        c = 24
        ul = []
        lr = []
        windows = []
        for i in range(w-r):
        	for j in range(b-c):
        		window = np.zeros((c,r))
        		ul.append([j,i])
        		lr.append([j+c,i+r])
        		window[:,:] = img_gray[i:(i+r),j:(j+c)]
        		windows.append(window)
        # windows = np.asarray(windows)
        # print(np.shape(windows))
        
        # print(np.shape(windows))
        predictions = self.predict(windows)

        pos_ul,pos_lr = [],[]
        for i, pred in enumerate(predictions):
        	if pred == 1:
        		pos_ul.append(ul[i])
        		pos_lr.append(lr[i])

        pos_ul = np.asarray(pos_ul)
        pos_lr = np.asarray(pos_lr)

        ave_ul = np.mean(pos_ul, axis=0).astype(int) + (3,-3)
        ave_lr = np.mean(pos_lr, axis=0).astype(int) + (3,-3)

        cv2.rectangle(img_temp, tuple(ave_ul), tuple(ave_lr), (0,0,255), 2)
        cv2.imwrite("output/{}.png".format(filename), img_temp)




