import numpy as np


def shuffle_filelistcsv(filename):
    """This file is to produce shuffled dataset by different data ids into train/valid/test.
    """

    valid_rate = [0.6, 0.8, 1.0]    # the valid and test part

    dataset = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            nid = line.split(',')[0]
            if nid not in dataset:
                dataset.append(nid)

        # Shuffle and divided into three part
        split1 = int(np.floor(valid_rate[0] * len(dataset)))
        split2 = int(np.floor(valid_rate[1] * len(dataset)))
        np.random.shuffle(dataset)
        train_set, valid_set, test_set = dataset[:split1], dataset[split1: split2], dataset[split2:]

        # Save the three part of data into three csv files
        f_train = open('train_set.csv', 'w')
        f_valid = open('valid_set.csv', 'w')
        f_test = open('test_set.csv', 'w')

        for line in lines:
            if line.split(',')[0] in train_set:
                f_train.write(line)
            elif line.split(',')[0] in valid_set:
                f_valid.write(line)
            elif line.split(',')[0] in test_set:
                f_test.write(line)

        f_train.close()
        f_valid.close()
        f_test.close()


if __name__ == '__main__':
    shuffle_filelistcsv('ImageSaveRadiomics//filelist.csv')
    