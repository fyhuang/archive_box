#!/bin/bash

wget --continue "https://github.com/protocolbuffers/protobuf/releases/download/v3.12.1/protoc-3.12.1-linux-x86_64.zip"
mkdir -p protoc
cd protoc && unzip ../protoc-3.12.1-linux-x86_64.zip
