import pyximport; pyximport.install() # NOQA
import time

import numpy as np

from skeleton.thinning import cy_getThinned3D # NOQA
from skimage.morphology import skeletonize

"""
Thinning algorithm as described in
A Parallel 3D 12-Subiteration Thinning Algorithm Kálmán Palágyi,Graphical Models and Image Processing
Volume 61, Issue 4, July 1999, Pages 199-221 Attila Kuba, 1999
z is the nth image of the stack in 3D array and is the first dimension in this program
"""


def getThinned(binaryArr):
    """
    Return thinned output
    Parameters
    ----------
    binaryArr : Numpy array
        2D or 3D binary numpy array

    Returns
    -------
    result : Numpy array
        2D or 3D binary thinned numpy array of the same shape
    """
    voxCount = np.sum(binaryArr)
    if len(binaryArr.shape) == 2:
        return skeletonize(binaryArr)
    else:
        assert np.max(binaryArr) in [0, 1], "input must always be a binary array"
        start_skeleton = time.time()
        zOrig, yOrig, xOrig = np.shape(binaryArr)
        orig = np.pad(np.uint64(binaryArr), 1, mode='constant', constant_values=0)
        cy_getThinned3D(orig)
        print("thinned %i number of pixels in %0.2f seconds" % (voxCount, time.time() - start_skeleton))
    return orig[1:zOrig + 1, 1: yOrig + 1, 1: xOrig + 1]


if __name__ == '__main__':
    sample = np.ones((5, 5, 5), dtype=np.uint8)
    resultSkel = getThinned(sample)