from time import time

import matplotlib.pyplot as plt
import numpy as np
from cv2 import cv2
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

dims = (20, 20)
colors = np.array([[255, 255, 255], [0, 0, 255], [0, 0, 102], [255, 255, 0], [255, 0, 0],
                 [0, 255, 0], [255, 51, 153], [255, 153, 51]])


def color(color):
    distances = np.sqrt(np.sum((colors - color) ** 2, axis=1))
    index_of_smallest = np.where(distances == np.amin(distances))
    smallest_distance = colors[index_of_smallest][0]
    if smallest_distance.shape[0] != 3:
        breakpoint()
    return smallest_distance


def map_colors(image):
    mapped = np.apply_along_axis(color, arr=image, axis=2)
    return mapped


def fit(image):
    shaped = np.reshape(image, (image.shape[0]*image.shape[1], 3))
    print("Fitting KMeans")
    t0 = time()
    shuffled = shuffle(shaped, n_samples=min(1000, shaped.shape[0]), random_state=0)
    kmeans = KMeans(n_clusters=len(colors), init=colors, random_state=0).fit(shuffled)
    print(f"done in {time() - t0:0.3f}s.")
    return kmeans


def quant(kmeans, image):
    assert image.shape[2] == 3
    shaped = np.reshape(image, (image.shape[0]*image.shape[1], 3))
    print("Clustering KMeans")
    t0 = time()
    labels = kmeans.predict(shaped)
    print(f"done in {time() - t0:0.3f}s.")
    return np.array(kmeans.cluster_centers_[labels].reshape(image.shape[0], image.shape[1], -1), dtype='uint8')


def pixelartify(image, sharpen=False, brightness=0, contrast=1, size=dims):
    if sharpen:
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        image = cv2.filter2D(image, -1, kernel)
    if size is None:
        size = dims
    resized = cv2.resize(image, dsize=size, interpolation=cv2.INTER_NEAREST)
    alphas = np.rint(resized[:, :, 3] / 255) * 255
    image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

    kmeans = fit(image[:, :, :3])
    resized = resized[:, :, :3]
    quantized = quant(kmeans, resized)
    colored = map_colors(quantized)
    with_alphas = np.array(np.dstack((colored, alphas)), dtype='uint8')
    return quantized, resized, with_alphas, alphas


def show(image):
    quantized, resized, with_alphas, alphas = pixelartify(image, sharpen=False, brightness=30)
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].imshow(with_alphas)
    axs[0, 1].imshow(quantized)
    axs[1, 1].imshow(resized)
    axs[1, 0].imshow(image)
    plt.show()


def save_file(file, path, brightness=0, contrast=1, size=dims, recolor=True):
    img = cv2.cvtColor(cv2.imread(file, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGBA)
    quantized, resized, with_alphas, alphas = \
        pixelartify(img, brightness=brightness, contrast=contrast, size=size)
    image = with_alphas
    if not recolor:
        image = np.array(np.dstack((quantized, alphas)), dtype='uint8')
    cv2.imwrite(path, cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA))


if __name__ == '__main__':
    show(cv2.cvtColor(cv2.imread('images/unnamed.jpg', cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGBA))
