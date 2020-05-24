.PHONY: tags check_all test_all proto

PROTOC=extern/protoc/bin/protoc
PACKAGES=archive_box dtsdb

tags:
	ctags -R $(PACKAGES)

checks:
	mypy $(PACKAGES)
	python3 -m unittest

proto:
	mkdir -p temp
	
	$(PROTOC) -I proto/dtsdb --python_out=temp --mypy_out=dtsdb \
		proto/dtsdb/*.proto
	./postprocess_proto.sh temp/schema_pb2.py dtsdb/schema_pb2.py
	./postprocess_proto.sh temp/test_pb2.py dtsdb/test_pb2.py
	
	$(PROTOC) \
		-I proto \
		--python_out=temp \
		proto/archive_box.proto
	
	# clean up
	rm -rf temp
