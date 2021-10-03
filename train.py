import yaml
import os
import torch

torch.backends.cudnn.benchmark = True

import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
import random
from datasets import TrainDataset
import numpy as np
import utils
from model import MLP
from tqdm import tqdm
from tensorboardX import SummaryWriter
from sklearn.model_selection import train_test_split
from warmup_scheduler import GradualWarmupScheduler

## Set Seeds
random.seed(1234)
np.random.seed(1234)
torch.manual_seed(1234)
torch.cuda.manual_seed_all(1234)

## Load yaml configuration file
with open('training.yaml', 'r') as config:
    opt = yaml.safe_load(config)
Train = opt['TRAINING']

## Model and log path direction
print('==> Build folder path')
start_epoch = 1
network_dir = os.path.join(Train['SAVE_DIR'], Train['Network'])
utils.mkdir(network_dir)
save_dir = os.path.join(network_dir)
utils.mkdir(save_dir)
model_dir = os.path.join(network_dir, 'models')
utils.mkdir(model_dir)
log_dir = os.path.join(network_dir, 'log')
utils.mkdir(log_dir)
train_dir = Train['TRAIN_DIR']
writer = SummaryWriter(log_dir=log_dir, filename_suffix=f'_log')

# GPU device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Model
print('==> Build model')
model = MLP(n_inputs=4, hidden_layer1=128, hidden_layer2=256, hidden_layer3=128)
if Train['GPU']:
    model.to(device=device)

# Optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=Train['LR'])

## Scheduler (Strategy)
warmup_epochs = 3
scheduler_cosine = optim.lr_scheduler.CosineAnnealingLR(optimizer, Train['EPOCH'] - warmup_epochs, eta_min=float(Train['LR_MIN']))
scheduler = GradualWarmupScheduler(optimizer, multiplier=1, total_epoch=warmup_epochs, after_scheduler=scheduler_cosine)
scheduler.step()

# Loss function
criterion = nn.MSELoss()

# DataLoaders
print('==> Data preparation')
total_dataset = TrainDataset(train_dir)
train_data, val_data = train_test_split(total_dataset, random_state=666, train_size=Train['VAL_RATE'])
train_loader = DataLoader(dataset=train_data, batch_size=Train['BATCH'],
                          shuffle=True, num_workers=0, drop_last=False, pin_memory=False)
val_loader = DataLoader(dataset=val_data, batch_size=1, shuffle=False, num_workers=0,
                        drop_last=False, pin_memory=False)

print(f'''==> Training details:
------------------------------------------------------------------
    Network:            {Train['Network']}
    Training data:      {len(train_data)}
    Validation data:    {len(val_data)}
    Start/End epochs:   {str(start_epoch) + '~' + str(Train['EPOCH'])}
    Batch sizes:        {Train['BATCH']}
    Learning rate:      {Train['LR']}
    GPU:                {Train['GPU']}''')
print('------------------------------------------------------------------')

# train
print('==> Start training')
best_val_loss = float('inf')

best_epoch_loss = 0

for epoch in range(start_epoch, Train['EPOCH'] + 1):
    epoch_loss = 0
    y_max = 0
    model.train()
    for i, data in enumerate(tqdm(train_loader, ncols=50, total=len(train_loader), leave=True), 0):

        for param in model.parameters():
            param.grad = None

        inputs = data[0].cuda()
        GT = data[1].cuda()
        out = model(inputs)
        loss = criterion(out, GT)

        # optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()

    # validation (evaluation)
    if epoch % Train['VAL_AFTER_EVERY'] == 0:
        model.eval()
        epoch_val_loss = 0
        for ii, data_val in enumerate(val_loader, 0):
            inputs = data_val[0].cuda()
            GT = data_val[1].cuda()
            with torch.no_grad():
                out = model(inputs)
            val_loss = criterion(out, GT)
            epoch_val_loss += val_loss.item()



        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_epoch_loss = epoch
            torch.save({'epoch': epoch, 'state_dict': model.state_dict(), 'optimizer': optimizer.state_dict()},
                       os.path.join(model_dir, "mini_loss_model.pth"))


        print(
            'validation: Loss: %.4f\n'
            '  -> mini_loss_epoch  %d Best_loss %.4f \n'
            % (epoch_val_loss/len(val_loader),
               best_epoch_loss, best_val_loss/len(val_loader)))
        writer.add_scalar('val/loss', epoch_val_loss/len(val_loader), epoch)
    print('  training: Loss: {:.4f}                   epoch [{:3d}/{}] '
          .format(epoch_loss/len(train_loader), epoch, Train['EPOCH']))
    print("------------------------------------------------------------------")
    torch.save({'epoch': epoch, 'state_dict': model.state_dict(), 'optimizer': optimizer.state_dict()},
               os.path.join(model_dir, "model_latest.pth"))
    scheduler.step()
    writer.add_scalar('train/loss', epoch_loss / len(train_loader), epoch)
    writer.add_scalar('train/lr', scheduler.get_lr()[0], epoch)
writer.close()
