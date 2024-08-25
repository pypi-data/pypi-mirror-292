import GPUtil

def foo():
    print('this is yanivtils')


def get_freest_gpu():
    gpus = GPUtil.getGPUs()
    freest_gpu = max(gpus, key=lambda gpu: gpu.memoryFree)
    return freest_gpu.id

