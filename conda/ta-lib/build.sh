#!/bin/bash
wget https://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz &&
sudo tar xvfz ta-lib-0.4.0-src.tar.gz &&
export PREFIX=/usr/local &&
sudo apt-get install gcc-multilib g++-multilib &&
echo "Installing TA-Lib in $PREFIX" &&
ls ta-lib &&
pushd ta-lib &&
./configure --prefix=$PREFIX &&
sudo make &&
sudo make install &&
sudo ldconfig &&
popd &&
rm ta-lib-0.4.0-src.tar.gz &&
rm -r ta-lib &&

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PREFIX/lib &&
export TA_INCLUDE_PATH=$PREFIX/include &&
export TA_LIBRARY_PATH=$PREFIX/lib &&
python setup.py build &&
python setup.py install --prefix=$PREFIX
