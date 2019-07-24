import numpy as np
from matplotlib import pyplot as plt


def show_3D_npimg(img):
    data = np.load(img)
    print(data.shape)

    channels = data.shape[2]

    fig, ax = plt.subplots(1, channels)

    for x in range(channels):
        ax[x].imshow(data[:,:,x], cmap=plt.cm.gray)
        ax[x].set_title((x))
    fig.show()
    input()


if __name__ == '__main__':
    show_3D_npimg('D:\\Memory\\Year.JiHai\\Workshop\\DataPreprocessing\\ImageSaveRadiomics\\Non-MVI ROI\\01305897\\Portal venou phase1_ud.npy')
    show_3D_npimg('D:\\Memory\\Year.JiHai\\Workshop\\DataPreprocessing\\ImageSaveRadiomics\\Non-MVI ROI\\01305897\\Portal venou phase1.npy')
    show_3D_npimg('D:\\Memory\\Year.JiHai\\Workshop\\DataPreprocessing\\ImageSaveRadiomics\\Non-MVI ROI\\01305897\\Portal venou phase1_r270.npy')
    show_3D_npimg('D:\\Memory\\Year.JiHai\\Workshop\\DataPreprocessing\\ImageSaveRadiomics\\Non-MVI ROI\\01305897\\Portal venou phase1_udr180.npy')
