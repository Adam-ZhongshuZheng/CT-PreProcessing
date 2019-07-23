# -*-coding:utf-8-*-

########################################################################################################
# This program is used for do the data regular on MVI, using the DicomDealer and NiiDealer
#
# By Adam Mo
# 6/28/2019
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

from DataPreProcess import DicomDealer, NiiDealer


class ReadDicomDir():
    """Get the dicom and nii list and them into ndarray saved as .npy.
    Besides, Combine the img and the handycraft features
    """

    def __init__(self, directory, image_save_dir, label_save_dir, mvi,
                 bigpath='MVI\\MVI_reg'):
        self.dire = directory
        self.bigpath = bigpath
        self.label_save_dir = label_save_dir
        self.image_save_dir = image_save_dir
        self.default = ('0.0,' * 37) + '0.0\n'
        self.yon = mvi

    def __check_dir(self, path):
        # save npy must have checked dir first
        if not os.path.exists(path):
            os.makedirs(path)

    def __get_id(self, str_a):
        # make a string like 'Z-234345-d' into '234345'
        begin = 100
        for i in range(len(str_a) + 1):
            if i == len(str_a):
                break
            if str_a[i].isdigit() and i < begin and str_a[i] is not '0':
                begin = i
            if (not str_a[i].isdigit()) and i > begin:
                break
        # print(str_a[begin:i])
        return str_a[begin:i]

    def __get_condata(self, filepath):
        # get the csv data from the csv path
        # in the type of dictionary, with the index as key and others strings as value
        f = open(filepath, 'r')
        all_lines = f.readlines()
        databook = {}
        for line in all_lines:
            index = line.split(',', 1)[0]
            databook[index] = line.split(',', 1)[1]

            # print(index, databook[line])
        f.close()
        return databook

    def __check_center(self, center):
        top = 462
        buttom = 50
        if center[0] > top:
            center[0] = top
        if center[0] < buttom:
            center[0] = buttom
        if center[1] > top:
            center[1] = top
        if center[1] < buttom:
            center[1] = buttom
        return center

    def deal_pair(self, d, n, savepath, filename, move=(0,0,0)):
        # print(savepath)

        # debug:
        # fig, ax = plt.subplots(1, 4)

        center = list(n.compute_center()[0])
        # print(center,)
        center[0] += move[0]
        center[1] += move[1]
        center[2] += move[2]
        center = self.__check_center(center)

        # print(center)
        d.cut_3D(center, [100, 100, 4])

        d.window_reset()

        # print('bef:' + str(d.img.shape))
        # for x in range(4):
        #         ax[x].imshow(d.img[:,:,x], cmap=plt.cm.gray)
        #         ax[x].set_title((x))
        # fig.show()

        # d.resample([d.dcmfile[0].PixelSpacing[0], d.dcmfile[0].PixelSpacing[1], 1])
        #
        # print('aft:' + str(d.img.shape))
        # for x in range(4):
        #         ax[x].imshow(d.img[:,:,x * 5], cmap=plt.cm.gray)
        #         ax[x].set_title((x*5))
        # fig.show()

        image = transform.resize(d.img, (128, 128, 4))

        # print('fin:' + str(image.shape))
        # for x in range(4):
        #         ax[x].imshow(image[:,:,x], cmap=plt.cm.gray)
        #         ax[x].set_title((x))
        # fig.show()
        # input()

        self.__check_dir(savepath)
        np.save(os.path.join(savepath, filename + '.npy'), image)

        # print(os.path.join(savepath, filename + '.npy') + '.npy')

        # data = np.load(os.path.join(savepath, filename + '.npy'))
        # print(data.shape)
        # plt.imshow(data[:,:,2], cmap=plt.cm.gray)
        # plt.show()

    def run(self):
        """walk the directory and read files to_ndarray
        Need to rewrite the structure of the directory
        """

        debug_count = 30000  # for quick debug
        flag = 0

        da = (15, 15, 1) # Data Augment

        condata = self.__get_condata(os.path.join(self.bigpath, 'EXCEL deal', 'Condata.csv'))
        # get the condata in the type of dictionary, with the index as key and others strings as value

        f = open(self.dire + ' datafile.csv', 'w')
        # \MVI-ROI
        for dir_name in os.listdir(os.path.join(self.bigpath, self.dire)):
            # 963245-W

            # for quick debug
            if debug_count <= 0:
                return
            debug_count -= 1

            # if dir_name[0] is not 'Z':
            # continue

            dir_now = os.path.join(self.bigpath, self.dire, dir_name)
            if not os.path.isdir(dir_now):
                continue

            patient_id = self.__get_id(dir_name)
            # print(patient_id)

            # To produce the contact data for imgs.
            if patient_id in condata:
                i_contdata = condata[patient_id]
            else:
                i_contdata = self.default


            # This loop is for data agumentation.
            for cid, center in enumerate([(0, 0, 0), (da[0], -da[1], 0), (da[0], da[1], 0), (-da[0], -da[1], 0), (-da[0], da[1], 0), (da[0], -da[1], da[2]), (da[0], da[1], da[2]), (-da[0], -da[1], da[2]), (-da[0], da[1], da[2])]):

                # for saving queue in the csv:
                Arter = ''
                Delay = ''
                Portal = ''

                # \MVI-ROI\963245-W
                save_path = os.path.join(self.dire, dir_name)
                for filename in os.listdir(dir_now):
                    # 963245Delayed phase-W
                    dir_now_2 = os.path.join(dir_now, filename)
                    # \MVI-ROI\963245-W\963245Delayed phase-W

                    save_path_2 = os.path.join(save_path, filename)
                    if not os.path.isdir(dir_now_2):
                        continue

                    idic = DicomDealer(dir_now_2)

                    for sub_filename in os.listdir(dir_now_2):
                        # This subfile is just for nii
                        if sub_filename.split('.')[-1] == 'gz' or sub_filename.split('.')[-1] == 'nii':
                            inii = NiiDealer(dir_now_2 + '/' + sub_filename)

                            self.deal_pair(idic, inii, os.path.join(self.image_save_dir, save_path), filename=filename + str(cid), move=center)

                            if 'A' in filename:
                                Arter = os.path.join(self.image_save_dir, save_path_2 + str(cid) + '.npy') + ',' + os.path.join(
                                    self.label_save_dir, save_path_2 + '.npy')

                            elif 'D' in filename:
                                Delay = os.path.join(self.image_save_dir, save_path_2 + str(cid) + '.npy') + ',' + os.path.join(
                                    self.label_save_dir, save_path_2 + '.npy')

                            elif 'P' in filename:
                                Portal = os.path.join(self.image_save_dir, save_path_2 + str(cid) + '.npy') + ',' + os.path.join(
                                    self.label_save_dir, save_path_2 + '.npy')

                            break

                f.write(str(patient_id) + ',' + self.yon + ',' + Arter + ',' + Delay + ',' + Portal + ',' + i_contdata)
                # These two lines to comfix all the data together to make it bigger
                # f.write(str(patient_id) + ',' + self.yon + ',' + Delay + ',' + Delay + ',' + Portal + ',' + i_contdata)
                # f.write(str(patient_id) + ',' + self.yon + ',' + Portal + ',' + Delay + ',' + Portal + ',' + i_contdata)
                print('debug:' + str(patient_id) + ',' + self.yon + ',' + Arter + ',' + Delay + ',' + Portal + ',' + i_contdata)
        f.close()


def main():
    bigpath = 'Data\\MVI\\MVI_reg'
    mvipath = 'MVI-ROI'
    nonmvipath = 'Non-MVI ROI'
    ReadDicomDir(nonmvipath, 'ImageSaveRadiomics', 'LabelSaveRadiomics', '0', bigpath=bigpath).run()
    ReadDicomDir(mvipath, 'ImageSaveRadiomics', 'LabelSaveRadiomics', '1', bigpath=bigpath).run()


if __name__ == '__main__':
    main()
