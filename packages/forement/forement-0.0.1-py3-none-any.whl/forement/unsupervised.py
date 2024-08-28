import cv2
import numpy as np
from scipy import stats
from orchard_bouman.orchard_bouman import OrchardBouman


def kmeans(image: np.ndarray, k: int) -> tuple:
    """Segment image channels by kmeans clustering.

    Args:
        image (np.ndarray): Image as numpy array (i.e. loaded via opencv).
        k (int): Number of clusters to use.

    Returns:
        tuple: Segmented image where mean of cluster center represents the label, array of cluster mean values for each cluster.
    """

    image = image[:, :, :3]

    m = image.shape[0]
    n = image.shape[1]

    # reshape image and apply kMeans
    x = np.reshape(image, (m * n, 3))
    pixel_vals = np.float32(x)

    # for k in range(1, n_cluster + 1):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    compactness, labels, centers = cv2.kmeans(pixel_vals, k, None, criteria, 10,
                                                cv2.KMEANS_RANDOM_CENTERS)

    # convert data into 8-bit values
    centers = np.uint8(centers)
    segmented_data = centers[labels.flatten()]
    # reshape data into the original image dimensions
    clustered_image = segmented_data.reshape(image.shape)

    return clustered_image, np.unique(centers)


def exp_max(image: np.ndarray, k) -> tuple:
    """Cluster via expectation maximization

    Args:
        image (np.ndarray): Image as numpy array (i.e. loaded via opencv).
        k (int): Number of clusters to use.

    Returns:
        tuple: Segmented image where mean of cluster center represents the label, array of cluster mean values for each cluster.
    """

    samples = image[:,:,:3].flatten()
    em = cv2.ml.EM.create()
    
    em.setClustersNumber(k)
    retval, log_like, labels, probs = em.trainEM(samples=samples)
    centers = em.getMeans()

    clustered_image = centers[labels].reshape(image.shape)
    # binary_image = labels.reshape(image.shape)

    return clustered_image, centers


def ob_exp_max(image: np.ndarray, k: int, channel: int) -> tuple:
    """Cluster via expectation maximization, using orchard bouman as the initial clustering step

    Args:
        image (np.ndarray): Image as numpy array (i.e. loaded via opencv).
        k (int): Number of clusters to use.

    Returns:
        tuple: Clustered image where mean of cluster center represents the label, array of cluster mean values for each cluster.
    """
    # TODO test flatten vs T flatten
    ob = OrchardBouman(image=image, k=k)
    nodes = ob.nodes
    centers = [node.Q[0, channel] for node in nodes]
    means = np.array(centers).reshape(len(centers), 1)

    samples = image[:,:,:3].flatten()
    em = cv2.ml.EM.create()
    
    em.setClustersNumber(2**k)
    retval, log_like, labels, probs = em.trainE(samples=samples, means0=means)
    retval, log_like, labels, probs = em.trainM(samples=samples, probs0=probs)
    centers = em.getMeans()
    clustered_image = centers[labels].reshape(image.shape)
    # binary_image = labels.reshape(image.shape)

    return clustered_image, centers

def create_binary_mask(clustered_image: np.ndarray, centers: list | np.ndarray, channel: int = 0):
    """Create a binary mask from a clustered image, where 1 is the foreground and 0 is the background.

    Args:
        clustered_image (np.ndarray): Clustered image.
        centers (list | np.ndarray): Array of cluster mean values.
        channel (int, optional): Color channel to use when running mode counts on images. Defaults to 0.

    Returns:
        np.ndarray: A binary mask, where 1 is the foreground and 0 is the background.
    """

    # find the most common cluster represented on the outermost border of the image
    outside_mode = stats.mode(
        np.concatenate([clustered_image[0, :, channel], clustered_image[:, 0, channel], clustered_image[-1, :, channel],
                        clustered_image[:, -1, channel]]))

    # assign the image background to 0, foreground to 1, and return the binary image
    vals = [np.abs((outside_mode[0] - center)) for center in centers]
    binary_mask = np.where(clustered_image[:, :, channel] == centers[vals.index(np.min(vals))], 0, 1).astype(np.uint8) * 255

    return binary_mask


def create_grabcut_mask(image: np.ndarray, binary_mask: np.ndarray):
    """Segment an image in grabcut using a mask produced by an unsupervised clustering algorithm.

    Args:
        image (np.ndarray): Original image as a numpy array.
        binary_mask (np.ndarray): Binary segmentation mask from an unsupervised clustering algorithm.

    Returns:
        np.ndarray: An image with the foreground segmented.
    """

    cv2.imshow("original", (image / 255))
    cv2.waitKey()

    cv2.imshow("mask", binary_mask)
    cv2.waitKey()
    binary_mask[binary_mask > 0] = cv2.GC_PR_FGD
    binary_mask[binary_mask == 0] = cv2.GC_PR_BGD

    # create foreground and background masks
    fg_model = np.zeros((1, 65), dtype="float")
    bg_model = np.zeros((1, 65), dtype="float")

    mask, bg_model, fg_model = cv2.grabCut(img=image.astype(np.uint8), mask=binary_mask, rect=None, fgdModel=fg_model,
                                           bgdModel=bg_model, iterCount=5, mode=cv2.GC_INIT_WITH_MASK)

    output_mask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD),
                           0, 1)

    # trimap = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD) | (mask == cv2.GC_PR_FGD),
    #                   0, 1, 2)

    # apply bitwise AND to the image using our mask generated by GrabCut to generate our final output image
    segmented_image = cv2.bitwise_and(image, image, mask=output_mask)

    return segmented_image
