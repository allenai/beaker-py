BEAKER_PROTO_PATH = "../beaker/msg"

.PHONY : docs
docs :
	rm -rf docs/build/
	sphinx-autobuild -b html --watch beaker/ --watch README.md docs/source/ docs/build/

.PHONY : build
build :
	rm -rf *.egg-info/
	python -m build

.PHONY : grpc
grpc :
	python -m grpc_tools.protoc --python_out=./beaker/ --pyi_out=./beaker/ --grpc_python_out=./beaker/ -I $(BEAKER_PROTO_PATH) $(BEAKER_PROTO_PATH)/beaker.proto
	sed -i '' 's/import beaker_pb2 as beaker__pb2/from . import beaker_pb2 as beaker__pb2/' beaker/beaker_pb2_grpc.py
