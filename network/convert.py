import torch

if __name__ == '__main__':
    model = torch.load('/Users/god/Projects/Representation-Learning-for-Information-Extraction/output/model.pth')
    traced_model = torch.jit.script(model)
    traced_model.save("traced_model.pth")