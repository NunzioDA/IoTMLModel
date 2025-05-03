import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms

# Transforming image
transform = transforms.Compose([
    transforms.Resize((72, 42)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# This class describes the CNN used to check 
# if a veicle is present in a parking space
class VehicleDetectionCNN(nn.Module):
    def __init__(self):
        super(VehicleDetectionCNN, self).__init__()
        
        # Convolutional layers + BatchNorm
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        self.conv4 = nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Dimension after 4 convolutional and pool:
        # 72x42 → 36x21 → 18x10 → 9x5 → 4x2
        self.fc1 = nn.Linear(256 * 4 * 2, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 1)

        # Dropout
        self.dropout = nn.Dropout(0.5)

        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        
        x = torch.flatten(x, start_dim=1)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.dropout(F.relu(self.fc2(x)))
        x = self.fc3(x)  

        x = self.sigmoid(x)
        return x
