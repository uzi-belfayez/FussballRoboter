import torch



if torch.cuda.is_available():
    device = torch.device("cuda")          # a CUDA device object
    print("CUDA is available. Using GPU.")
else:
    device = torch.device("cpu")           # a CPU device object
    print("CUDA is not available. Using CPU.")