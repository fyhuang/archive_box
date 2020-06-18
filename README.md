# Archive Box

Archive Box is a way to organize your files across devices that provides more flexibility than traditional directory hierarchies.
Organization by keyword, by tag, and full-text search make it easy to keep a collection of files organized.
Files of all types are supported, but initial work is focused on documents (e.g. PDFs) and multimedia (video, audio, and images).

## Backend-less synchronization

Archive Box supports synchronization of file metadata across devices without requiring an active backend service or database.
The only requirement is a location where files can be downloaded and uploaded.
Cloud storage services like S3, GCS, and B2 are a perfect fit for Archive Box, as they are highly available, trivial to set up, and the cost scales arbitrarily low with usage.
With some additional work, Archive Box could even sychronize using a simple FTP or SCP server.

# Setup

Our eventual goal is to package Archive Box into an easy-to-use self-contained executable.
In the current early development stage, you can install the package manually:

```bash
# TODO: consolidate these
pip install -r requirements.txt
./setup.py install
```

Consider installing in a virtualenv to avoid conflicts with other packages.

# Developing

First install the additional dependencies for development (like `mypy`):

```bash
pip install -r requirements-dev.txt
```

Run the type checker and unit tests:

```bash
make checks
```

Run a test coverage report:

```bash
make coverage
```

Protobuf is used in some places in the codebase.
If you edit any of the `.proto` files in `proto/`, you must regenerate the Python generated protobuf code:

```bash
make proto
```
