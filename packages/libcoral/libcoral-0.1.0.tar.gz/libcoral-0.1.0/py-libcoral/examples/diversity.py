import libcoral # import the libcoral library
import time
import numpy as np
import matplotlib.pyplot as plt


def main():
    data, labels, embedding = load_fashion_mnist()

    # # Remote-edge diversity: maximize the minimum distance between
    # # any two points in the solution
    # start = time.time()
    # diversity = libcoral.DiversityMaximization(10, "remote-edge", coreset_size=100)
    # solution = diversity.solve(data)
    # end = time.time()
    # print("found remote-edge solution with cost", diversity.cost(data[solution]), "in time", end - start)
    #
    # plt.scatter(embedding[:,0], embedding[:,1])
    # plt.scatter(embedding[solution,0], embedding[solution,1], color="red")
    # plt.savefig("remote-edge.png")
    
    # Remote-clique diversity: maximize the sum of distances of
    # all points in the solution
    start = time.time()
    diversity = libcoral.DiversityMaximization(10, "remote-clique", coreset_size=1000)
    solution = diversity.solve(embedding)
    end = time.time()
    print("found remote-clique solution with cost", diversity.cost(embedding[solution]), "in time", end - start)

    plt.scatter(embedding[:,0], embedding[:,1])
    plt.scatter(embedding[solution,0], embedding[solution,1], color="red")
    plt.savefig("remote-clique.png")


def load_fashion_mnist():
    """This function just downloads the 60k training images of fashion-mnist locally, if not already available,
    and returns them as a float32 array.
    """
    import urllib.request
    import os
    import gzip
    import umap

    fashion_local = "train-images-idx3-ubyte.gz"
    fashion_url = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/train-images-idx3-ubyte.gz"
    fashion_labels_local = "train-labels-idx1-ubyte.gz"
    fashion_labels_url = "https://github.com/zalandoresearch/fashion-mnist/raw/master/data/fashion/train-labels-idx1-ubyte.gz"
    if not os.path.isfile(fashion_local):
        print("downloading fashion-mnist file")
        urllib.request.urlretrieve(fashion_url, fashion_local)
    if not os.path.isfile(fashion_labels_local):
        print("downloading fashion-mnist file")
        urllib.request.urlretrieve(fashion_labels_url, fashion_labels_local)
    with gzip.open(fashion_local, 'rb') as imgpath:
        images = np.frombuffer(imgpath.read(), dtype=np.uint8,
                               offset=16).reshape(60000, 784)
    with gzip.open(fashion_labels_local, 'rb') as lbpath:
        labels = np.frombuffer(lbpath.read(), dtype=np.uint8,
                               offset=8)

    data = images.astype(np.float32)

    umap_file = "fashion-mnist-umap.npy"
    if not os.path.isfile(umap_file):
        embed = umap.UMAP()
        embedding = embed.fit_transform(data)
        np.save(umap_file, embedding)
    embedding = np.load(umap_file)

    return data, labels.astype(np.uint32), embedding



main()

