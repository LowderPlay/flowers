from time import time

import numpy as np
from skimage import img_as_float
from skimage.exposure import adjust_gamma
from skimage.filters import unsharp_mask
from skimage.io import imread, imsave
from skimage.transform import resize
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

dims = (20, 20)
colors = np.array([[255, 255, 255], [0, 0, 255], [0, 0, 102], [255, 255, 0], [255, 0, 0],
                   [0, 255, 0], [255, 51, 153], [255, 153, 51]])


def color_dist(color):
    distances = np.sqrt(np.sum((colors - color) ** 2, axis=1))
    index_of_smallest = np.where(distances == np.amin(distances))
    smallest_distance = colors[index_of_smallest][0]
    if smallest_distance.shape[0] != 3:
        breakpoint()
    return smallest_distance


def map_colors(image):
    mapped = np.apply_along_axis(color_dist, arr=image, axis=2)
    return mapped


def fit(image):
    shaped = np.reshape(image, (image.shape[0] * image.shape[1], 3))
    print("Fitting KMeans")
    t0 = time()
    shuffled = shuffle(shaped, n_samples=min(1000, shaped.shape[0]), random_state=0)
    kmeans = KMeans(n_clusters=len(colors), init=colors, random_state=0).fit(shuffled)
    print(f"done in {time() - t0:0.3f}s.")
    return kmeans


def quant(kmeans, image):
    assert image.shape[2] == 3
    shaped = np.reshape(image, (image.shape[0] * image.shape[1], 3))
    print("Clustering KMeans")
    t0 = time()
    labels = kmeans.predict(shaped)
    print(f"done in {time() - t0:0.3f}s.")
    return np.array(kmeans.cluster_centers_[labels].reshape(image.shape[0], image.shape[1], -1), dtype='uint8')


def transform(image, brightness=0, gamma=1, size=dims, sharpen=True):
    if size is None:
        size = dims
    resized = resize(image, output_shape=size, order=0, anti_aliasing=False)
    if image.shape[2] < 4:
        alphas = np.full(resized.shape[:2], 255)
    else:
        alphas = np.rint(resized[:, :, 3])
    resized = img_as_float(resized[:, :, :3])
    if sharpen:
        resized = unsharp_mask(resized)
    resized *= (brightness+100)/100
    resized = np.clip(resized, 0, 1)
    resized = adjust_gamma(resized, gamma)
    resized = np.rint(resized*255)
    kmeans = fit(image[:, :, :3])
    quantized = quant(kmeans, resized)
    colored = map_colors(quantized)
    with_alphas = np.array(np.dstack((colored, alphas)), dtype='uint8')
    return quantized, resized, with_alphas, alphas


# def show(image):
#     quantized, resized, with_alphas, alphas = transform(image, brightness=30)
#     fig, axs = plt.subplots(2, 2)
#     axs[0, 0].imshow(with_alphas)
#     axs[0, 1].imshow(quantized)
#     axs[1, 1].imshow(resized)
#     axs[1, 0].imshow(image)
#     plt.show()


def save_file(file, path, brightness=0, contrast=1, size=dims, recolor=True, sharpen=True):
    img = imread(file)
    quantized, resized, with_alphas, alphas = \
        transform(img, brightness=brightness, gamma=contrast, size=size, sharpen=sharpen)
    image = with_alphas
    if not recolor:
        image = np.array(np.dstack((quantized, alphas)), dtype='uint8')
    imsave(path, image)


# if __name__ == '__main__':
#     show(imread('images/unnamed.jpg'))
