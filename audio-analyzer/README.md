# Combile libkeyfinder via gcc

## MacOS

```bash
brew install gcc
cd libkeyfinder && g++ -shared -o wrapper.dylib -fPIC wrapper.cpp -lkeyfinder
```

## Linux

```bash
sudo apt-get install g++
cd libkeyfinder && g++ -shared -o wrapper.so -fPIC wrapper.cpp -lkeyfinder
```