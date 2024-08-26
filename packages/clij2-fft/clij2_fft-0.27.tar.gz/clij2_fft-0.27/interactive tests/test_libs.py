from clij2fft.libs import getlib
from clij2fft.richardson_lucy import richardson_lucy, richardson_lucy_nc
import numpy as np


lib = getlib()
lib.print_platforms_and_devices()

img= np.ones((256, 256, 128), dtype=np.float32)
psf = np.ones((128, 128, 64), dtype=np.float32)

print('testing Richardson Lucy')
result = richardson_lucy(img, psf, 100, 0, platform=0, device=0)
print()
print(result.shape, result.mean())

print('testing non-circulant Richardson Lucy')
result = richardson_lucy_nc(img, psf, 100, 0, platform=0, device=0)
print()
print(result.shape, result.mean())