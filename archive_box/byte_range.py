class ByteRangeReader(object):
    def __init__(self, wrapped_stream, range_start: int, range_end: int) -> None:
        self.wrapped_stream = wrapped_stream
        # Both ends of the byte range are inclusive (like HTTP)
        self.max_bytes = range_end - range_start + 1
        self.read_so_far = 0

        wrapped_stream.seek(range_start)

    def __enter__(self) -> 'ByteRangeReader':
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.wrapped_stream.__exit__(exc_type, exc_value, traceback)

    def read(self, wanted_size = -1) -> bytes:
        remaining = self.max_bytes - self.read_so_far
        if remaining <= 0:
            return b''

        if wanted_size < 0:
            read_size = remaining
        else:
            read_size = min(remaining, wanted_size)

        result = self.wrapped_stream.read(read_size)
        self.read_so_far += len(result)
        return result


