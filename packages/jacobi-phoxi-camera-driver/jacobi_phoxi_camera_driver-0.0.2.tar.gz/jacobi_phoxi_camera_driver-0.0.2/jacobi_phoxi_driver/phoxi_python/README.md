# PhoXi Camera Driver
Replace `/opt/Photoneo/PhoXiControl-1.13.1/API/include/PhoXiOpenCVSupport.h` with `./custom/PhoXiOpenCVSupport.h`.

Make PhoXi Control API visible as a dynamic shared library:
`export LD_LIBRARY_PATH=/opt/Photoneo/PhoXiControl-1.13.1/API/lib/`.

Build this driver.
```
mkdir build && cd build
cmake ..
make -j8
```
