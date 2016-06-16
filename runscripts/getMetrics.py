import numpy as np

from scipy import ndimage
from six.moves import cPickle

from KESMAnalysis.imgtools import loadStack, saveStack
from KESMAnalysis.pipeline.pipelineComponents import watershedMarker
from KESMAnalysis.segmentation.colorSegmentation import cleanupLabeledImage

from skeleton.thin3DVolume import getThinned3D
from skeleton.orientationStatisticsSpline import getStatistics, plotKDEAndHistogram, getImportantMetrics
from skeleton.unitwidthcurveskeleton import getShortestPathSkeleton
from skeleton.segmentStats import getSegmentStats

# load 2D facelets median filtered to be vectorized
filePath = input("please enter a root directory where your median filtered 2D slices are----")
stack = loadStack(filePath)

# load aspect ratio to make the 3D volume isotropic using quadratic interpolation
# aspectRatio = input("please enter resolution of a voxel in 3D with resolution in x followed by y and z (spaces in between)")
# aspectRatio = [float(item) for item in aspectRatio.split(' ')]
aspectRatio = [0.7, 0.7, 5]
stack = ndimage.interpolation.zoom(stack, zoom=aspectRatio, order=2, prefilter=False)

# binarize using 3D watershed transform
binaryVol = watershedMarker(stack)

# save binary volume
# np.save(filePath + "/" + "binary.npy", binaryVol)
cleanupLabeledImage(binaryVol)

# save binary volume
np.save(filePath + "/" + "binaryLCC.npy", binaryVol)

# convert to boolean becasue getThinned expects a boolean input
binaryVol = binaryVol.astype(bool)

# thin binarized volume of vessels
thinnedVol = getThinned3D(binaryVol)

# decluster thinned volume
skeletonVol = getShortestPathSkeleton(thinnedVol)

# save the skeleton volume as pngs
saveStack(skeletonVol, filePath + "/skeleton")

# save the skeleton volume as npy
np.save(filePath + "/skeleton/" + "skeleton.npy", skeletonVol)

# vectorize and find metrics
segmentCountdict, segmentLengthdict, segmentTortuositydict, totalSegments, typeGraphdict, avgBranching, endP, branchP, segmentContractiondict, segmentHausdorffDimensiondict, cycleInfo = getSegmentStats(skeletonVol)

# save the metrics dumping using cPickle as a list of elements as obtained from getSegmentStats
# as segmentCountdict, segmentLengthdict, segmentTortuositydict, totalSegments, typeGraphdict, avgBranching, endP, branchP, segmentContractiondict, segmentHausdorffDimensiondict

outputList = [segmentCountdict, segmentLengthdict, segmentTortuositydict, totalSegments, typeGraphdict, avgBranching, endP, branchP, segmentContractiondict, segmentHausdorffDimensiondict, cycleInfo]
varList = ['segmentCountdict', 'segmentLengthdict', 'segmentTortuositydict', 'totalSegments', 'typeGraphdict', 'Average Branching', 'end Points', 'branch Points', 'segmentContractiondict', 'segmentHausdorffDimensiondict', 'cycleInfo']
outputDict = {}
for var, op in zip(varList, outputList):
    outputDict[var] = op
cPickle.dump(outputDict, open(filePath + "/" + "metrics.p", "wb"))

# to load the statistics
# outputDict = cPickle.load(open("/home/3scan-data/exports/78c507c6e37294470/block-00000000/region-00023120-00023632-00023124-00023636-00000282-00000354/median/skeleton/skeletonregion-00023120-00023632-00023124-00023636-00000282-00000354.npymetrics.p", "rb"))

# save important statistics in a json file
getImportantMetrics(outputDict, binaryVol, skeletonVol)
getStatistics(segmentLengthdict, "Segment Length")

getStatistics(segmentContractiondict, "Segment Contraction")

getStatistics(segmentHausdorffDimensiondict, "Segment Hausdorff Dimension")

plotKDEAndHistogram(list(segmentLengthdict.values()), "/home/pranathi/Pictures/segment Length Histogram.png", 'Length(um)', True)
plotKDEAndHistogram(list(segmentContractiondict.values()), "/home/pranathi/Pictures/segment Contraction Histogram.png", 'Contraction')
plotKDEAndHistogram(list(segmentHausdorffDimensiondict.values()), "/home/pranathi/Pictures/segment Hausdorff Dimension Histogram.png", 'Hausdorff Dimension')
plotKDEAndHistogram(list(typeGraphdict.values()), "/home/pranathi/Pictures/Sub-graph in a network Histogram.png", 'subgraphs')
