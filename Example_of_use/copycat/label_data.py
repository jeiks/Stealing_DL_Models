#torch
import torch
import torchvision.transforms as transforms
#local files
from model import CNN
from image_list import ImageList
#general
from tqdm import tqdm
#system
from sys import argv, exit, stderr

if __name__ == '__main__':
    if len(argv) != 4 and len(argv) != 5:
        print('Use: {} model_file.pth image_list.txt output.txt [batch_size (default: 1024)]'.format(argv[0]), file=stderr)
        exit(1)

    model_fn   = argv[1]
    imglist_fn = argv[2]
    output_fn  = argv[3]
    batch_size = int(argv[4]) if len(argv) == 5 else 1024
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CNN()
    model.load_state_dict(torch.load(model_fn))
    model = model.to(device)
    
    print('Handling images...')
    transform = transforms.Compose([ transforms.Resize( (32,32) ), transforms.ToTensor() ])
    dataset = ImageList(imglist_fn, color=True, transform=transform, return_filename=True)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)

    print('Generating labels from oracle...')
    with torch.no_grad():
        model.eval()
        with open(output_fn, 'w') as output_fd:
            for images, _, filenames in tqdm(loader):
                images = images.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                output_fd.writelines(['{} {}\n'.format(img_fn, label) for img_fn, label in zip(filenames, predicted)])
                
