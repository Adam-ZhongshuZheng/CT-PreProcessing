# -*-coding:utf-8-*-

########################################################################################################
# This program is used for do the data regular on MVI data
# including: --> turning the DICOM img and NII img into numpy -> .npy
#            --> clean the EXCEL data
#            --> provide a csv data for all data in order to used in deep network
#            --> Cut the dicom into little blocks we may needed
#            --> Compute the all sizes of the nii
#
# By Adam Mo
# 6/13/2019
########################################################################################################

import numpy as np

# import cv2
from matplotlib import pyplot as plt
# import imageio
# import skimage.io as io

import pydicom as dicom
import nibabel as nib
import SimpleITK as sitk
from skimage import transform
import scipy
import os


class DicomDealer:

    def __init__(self, filename):
        """Read a Dicom and deal with it

        Args:
            filename: The directory name of the 3d-dicoms
        """
        self.dcmfile = self.__load_scan(filename)
        self.img = self.__get_pixels_hu().transpose(1, 2, 0)

    @staticmethod
    def __load_scan(filename):
        """load the dicom directory and return all the slices
        """
        slices = []
        testt = []
        for s in os.listdir(filename):
            if s[0] is 'I':
                slices.append(dicom.read_file(os.path.join(filename, s)))
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        try:
            slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
        except:
            slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

        for s in slices:
            s.SliceThickness = slice_thickness

        return slices

    def cut_3D(self, center, size):
        """give a size like (64, 64, 4) and the center point

        Args:
            center: The central point of the desired cutting position
            size: The size of the desired cutting part

        Return:
            the cut one
        """
        xmin = int(center[0] - size[0] / 2)
        xmax = int(center[0] + size[0] / 2)
        ymin = int(center[1] - size[1] / 2)
        ymax = int(center[1] + size[1] / 2)
        zmin = int(center[2] - size[2] / 2)
        zmax = int(center[2] + size[2] / 2)

        img = self.img[xmin:xmax, ymin:ymax, zmin:zmax].copy()
        self.img = img
        return img

    def window_reset(self, normal=True):
        """truncated image according to window center and window width.
           It is necessary for CT images to do this!

        Args:
            normal: if to change the pixel to 0~1 or not. (0~255)

        Return:
            changed one
        """
        windowCenter = self.dcmfile[0].WindowCenter
        windowWidth = self.dcmfile[0].WindowWidth
        minWindow = float(windowCenter) - 0.5 * float(windowWidth)
        newimg = (self.img - minWindow) / float(windowWidth)
        newimg[newimg < 0] = 0
        newimg[newimg > 1] = 1
        if not normal:
            newimg = (newimg * 255).astype('uint8')

        self.img = newimg
        return newimg

    def __get_pixels_hu(self):
        """Convert the 2D list to a 3D array and reset some of vacant pixels
        """
        image = np.stack([s.pixel_array for s in self.dcmfile])
        # Convert to int16 (from sometimes int16),
        # should be possible as values should always be low enough (<32k)
        image = image.astype(np.int16)

        # Set outside-of-scan pixels to 0
        # The intercept is usually -1024, so air is approximately 0
        image[image <= -2000] = 0

        # Convert to Hounsfield units (HU)
        for slice_number in range(len(self.dcmfile)):

            intercept = self.dcmfile[slice_number].RescaleIntercept
            slope = self.dcmfile[slice_number].RescaleSlope

            if slope != 1:
                image[slice_number] = slope * image[slice_number].astype(np.float64)
                image[slice_number] = image[slice_number].astype(np.int16)

            image[slice_number] += np.int16(intercept)

        return np.array(image, dtype=np.int16)

    def resample(self, new_spacing=[1, 1, 1]):
        """Change the REAL distance between the slices and pixels in order to make 3d-Convolution works better
           !!! It wastes too much time !!! You'd better cut the img first and try this.

        Args:
            new_spacing: The real distances you want images to be changed.
        """
        image = self.img
        spacing = np.array(
            [self.dcmfile[0].SliceThickness, self.dcmfile[0].PixelSpacing[0], self.dcmfile[0].PixelSpacing[1]],
            dtype=np.float32)

        resize_factor = spacing / new_spacing
        new_real_shape = image.shape * resize_factor
        new_shape = np.round(new_real_shape)
        real_resize_factor = new_shape / image.shape
        # new_spacing = spacing / real_resize_factor

        image = scipy.ndimage.interpolation.zoom(image, real_resize_factor, mode='nearest')

        return image


def main():
    d = DicomDealer('C:\\Users\\Hivot\\Desktop\\Portal venous phase')    # 1070979Delayed phase-W
    print(len(d.dcmfile))
    fig, ax = plt.subplots(1, 3)
    ax0 = ax[0].imshow(d.dcmfile[10].pixel_array, cmap=plt.cm.gray)
    ax1 = ax[1].imshow(d.img[10], cmap=plt.cm.gray)
    ax2 = ax[2].imshow(d.window_reset()[10], cmap=plt.cm.gray)

    fig.colorbar(ax0, ax=ax[0])
    fig.colorbar(ax1, ax=ax[1])
    fig.colorbar(ax2, ax=ax[2])
    fig.show()
    input()
    print(d.img.shape)
    print(d.resample().shape)
    # set the size is (128, 128, 10)

    from NiiDealer import NiiDealer

    dcmfile = NiiDealer('C:\\Users\\Hivot\\Desktop\\Portal venous phase\\1062674P.nii.gz')   # 1070979Delayed phase-W\\1070979d.nii
    center = dcmfile.compute_center()[0]

    d.window_reset()
    img = d.cut_3D(center, [128, 128, 10], )

    fig, ax = plt.subplots(2, 4)
    for x in range(0, 2):
        for y in range(0, 4):
            ax[x, y].imshow(img[:, :, x * y + 1], cmap=plt.cm.gray)
    fig.show()


if __name__ == '__main__':
    main()
