# lib-one-proto

Insta360 Proto Buffer files from libOne.so contained into the Android app compiled in python.

- Insta360 APK Version: 1.66.1

# Installation

```bash
pip install lib-one-proto
```

# Compile Yourself

1. Download the insta360 apk.
2. Use apktool to decompile the apk: `apktool d insta360.apk`
3. Copy the `libOne.so` file from the `lib/armeabi-*` folder to the current directory.
4. Make sure you have the `protoc` compiler installed.
5. Give execution permission to the script and run: `./extract_proto_and_compile.sh`
6. The extracted proto files will be in the `proto_files` folder and the compiled python files in the `lib_one_proto` folder.
