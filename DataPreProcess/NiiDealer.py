import numpy as np

import cv2
from matplotlib import pyplot as plt
# import imageio
# import skimage.io as io

import pydicom as dicom
import nibabel as nib
import SimpleITK as sitk
from numpy import mean
from skimage import transform
import scipy
import os


class NiiDealer:

    def __init__(self, filename):
        """Read a nii and deal with it

        Args:
            filename: the file of nii
        """
        self.dcmfile = nib.load(filename)
        self.img = self.dcmfile.get_data().astype('uint8').transpose(1, 0, 2)

    def compute_center(self):
        """Compute the center of the nii, using minimal enclosing circle from cv2

        Return:
            the center
        """
        center = []
        for i in range(self.img.shape[2]):
            # print(self.img[:, :, i].sum())
            mask = self.img[:, :, i].copy()

            # find contours in the mask and initialize the current (x, y) center of the ball
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                center.append((int(x), int(y), i, radius))

        center = mean(center, axis=0)
        return (round(center[0]), round(center[1]), round(center[2])), center[3]

    def compute_thickness(self):
        """To compute the thickness of nii

        Return:
             the thickness
        """
        minZ = 1000
        maxZ = 0
        for i in range(self.img.shape[2]):
            mask = self.img[:, :, i].copy()
            if mask.sum() <= 0:
                continue
            if minZ > i:
                minZ = i
            if maxZ < i:
                maxZ = i
        return maxZ - minZ


def statics(directory):
    """To Give the area and the length of all the nii space
        
    Args:
        directory:
    """
    radius = []
    width = []
    debugc = 3000      # for debug
    for dir_name in os.listdir(directory):
        # 963245-W

        debugc -= 1
        if debugc == 0:
            break

        # if dir_name[0] is not 'Z':
        # continue

        dir_now = os.path.join(directory, dir_name)
        if not os.path.isdir(dir_now):
            continue

        # \MVI-ROI\963245-W

        for filename in os.listdir(dir_now):
            # 963245Delayed phase-W
            dir_now_2 = os.path.join(dir_now, filename)
            # \MVI-ROI\963245-W\963245Delayed phase-W

            if not os.path.isdir(dir_now_2):
                continue

            for sub_filename in os.listdir(dir_now_2):
                # This subfile is just for nii
                if sub_filename.split('.')[-1] == 'gz' or sub_filename.split('.')[-1] == 'nii':
                    print(os.path.join(dir_now_2, sub_filename))
                    dcmfile = NiiDealer(os.path.join(dir_now_2, sub_filename))
                    radi = dcmfile.compute_center()[1]
                    radius.append(radi)
                    width.append(dcmfile.compute_thickness())
                    break

    # fig, ax = plt.subplots(1, 2)
    plt.hist(radius, facecolor='yellowgreen')
    new_ticks1 = np.linspace(0, 80, 10)
    plt.xticks(new_ticks1)
    plt.show()
    plt.hist(width)
    new_ticks2 = np.linspace(0, 30, 10)
    plt.xticks(new_ticks2)
    plt.show()
    print(len(radius), len(width))


def main():
    statics('D:\\Memory\\MVI\\MVI_reg\\Non-MVI ROI')
    statics('D:\\Memory\\MVI\\MVI_reg\\MVI-ROI')


if __name__ == '__main__':
    main()
