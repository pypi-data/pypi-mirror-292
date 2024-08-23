#!/bin/bash

set -e

# pip3 install grpcio-tools

#protoc -I.. ../core.proto --python_out=plugins=grpc:.
#mv gitlab.com/mergetb/xir/lang/go/v0.3/core.pb.go .
#rm -rf gitlab.com

python3 -m grpc_tools.protoc -I.. \
    --python_out=./mergexp/pb \
    --grpc_python_out=./mergexp/pb \
    ../core.proto
