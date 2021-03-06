.PHONY: tags check_all test_all proto

PROTOC=extern/protoc/bin/protoc
PACKAGES=archive_box dtsdb cfgparse tools

tags:
	ctags -R $(PACKAGES)

checks:
	mypy $(PACKAGES)
	python3 -m unittest

coverage:
	coverage run -m unittest
	find $(PACKAGES) -name '*.py' -exec coverage html '{}' +

proto:
	mkdir -p temp
	
	$(PROTOC) -I proto --python_out=temp --mypy_out=. \
		proto/dtsdb/*.proto
	./postprocess_proto.sh temp/dtsdb/schema_pb2.py dtsdb/schema_pb2.py
	./postprocess_proto.sh temp/dtsdb/test_pb2.py dtsdb/test_pb2.py
	
	$(PROTOC) -I proto --python_out=temp --mypy_out=. \
		proto/archive_box/*.proto
	./postprocess_proto.sh temp/archive_box/archive_box_pb2.py archive_box/archive_box_pb2.py
	
	# clean up
	rm -rf temp
