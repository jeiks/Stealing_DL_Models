#torch
import torch
#local files
from model import CNN
from cifar_data import get_datasets
#general
from tqdm import tqdm
import numpy as np
from sklearn.metrics import f1_score
#system
from sys import argv, exit, stderr

if __name__ == '__main__':
    if len(argv) != 2:
        print('Use: {} model_file.pth'.format(argv[0]), file=stderr)
        exit(1)

    model = CNN()
    model.load_state_dict(torch.load(argv[1]))
    
    batch_size = 16
    dataset = get_datasets(train=False, batch=batch_size)

    print('Testing the model...')
    correct = 0
    total = 0
    results = np.zeros([dataset['n_test'], 2], dtype=np.int)
    res_pos = 0
    with torch.no_grad():
        model.eval()
        for data in tqdm(dataset['test']):
            images, labels = data
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            results[res_pos:res_pos+batch_size, :] = np.array([labels.tolist(), predicted.tolist()]).T
            res_pos += batch_size
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    micro_avg = f1_score(results[:,0], results[:,1], average='micro')
    macro_avg = f1_score(results[:,0], results[:,1], average='macro')
    print('\nAverage: {:.2f}% ({:d} images)'.format(100. * (correct/total), total))
    print('Micro Average: {:.6f}'.format(micro_avg))
    print('Macro Average: {:.6f}'.format(macro_avg))

    #print('Accuracy: {:.2f}%'.format(100. * correct / total))
