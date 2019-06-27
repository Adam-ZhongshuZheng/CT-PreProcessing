
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


class ReadDicomDir():
    """Get the dicom and nii list and them into ndarray saved as .npy.
    Besides, Combine the img and the handycraft features
    """

    def __init__(self, directory, image_save_dir, label_save_dir, yon, bigpath=''):
        self.dire = directory
        self.bigpath = bigpath
        self.label_save_dir = label_save_dir
        self.image_save_dir = image_save_dir
        self.default = ('0.0,' * 37) + '0.0\n'
        self.yon = yon

    def __check_dir(self, path):
        # save npy must have checked dir first
        if not os.path.exists(path):
            os.makedirs(path)

    def __write_3D_dicom(self, filename, savename):
        # print(filename)
        image = transform.resize(image, (256, 256, 16))
        self.__check_dir(savename)
        np.save(savename + '.npy', image)
        print(filename)
        # print(image.shape)
        # input()
        # data = np.load(os.path.join(savename, filename.split('/')[-1] + '.npy'))
        # print(data.shape)
        # plt.imshow(data[15,:,:])
        # plt.show()

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
        f = open('Condata.csv', 'r')
        all_lines = f.readlines()
        databook = {}
        for line in all_lines:
            index = line.split(',', 1)[0]
            databook[index] = line.split(',', 1)[1]

            # print(index, databook[line])
        f.close()
        return databook

    def run(self):
        """walk the directory and read files to_ndarray
        Need to rewrite the structure of the directory
        """

        debug_count = 2  # for quick debug

        condata = self.__get_condata('Condata.csv')     # TODO: set the file path here
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
            print(patient_id)

            # To produce the contact data for imgs.
            if patient_id in condata:
                i_contdata = condata[patient_id]
            else:
                i_contdata = self.default

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

                self.__write_3D_dicom(dir_now_2, self.image_save_dir + '/' + save_path_2)
                # TODO: the process here about the cut Dicom

                for sub_filename in os.listdir(dir_now_2):
                    # This subfile is just for nii
                    if sub_filename.split('.')[-1] == 'gz' or sub_filename.split('.')[-1] == 'nii':
                        # self.__write_nii(dir_now_2 + '/' + sub_filename, self.label_save_dir + '/' + save_path_2)

                        if 'A' in filename:
                            Arter = os.path.join(self.image_save_dir, save_path_2 + '.npy') + ',' + os.path.join(
                                self.label_save_dir, save_path_2 + '.npy')

                        elif 'D' in filename:
                            Delay = os.path.join(self.image_save_dir, save_path_2 + '.npy') + ',' + os.path.join(
                                self.label_save_dir, save_path_2 + '.npy')

                        elif 'P' in filename:
                            Portal = os.path.join(self.image_save_dir, save_path_2 + '.npy') + ',' + os.path.join(
                                self.label_save_dir, save_path_2 + '.npy')

            f.write(str(patient_id) + ',' + self.yon + ',' + Arter + ',' + Delay + ',' + Portal + ',' + i_contdata)

        f.close()


def main():
    mvipath = 'MVI-ROI'
    nonmvipath = 'Non-MVI ROI'
    ReadDicomDir(nonmvipath, 'ImageSaveRadiomics', 'LabelSaveRadiomics', '0').run()
    ReadDicomDir(mvipath, 'ImageSaveRadiomics', 'LabelSaveRadiomics', '1').run()
