# dadude

Lakehouse management and orchestration tool.

## Status

- The ultimate target lakehouse is the unity catalog, which is to provide benefits from both `deltalake` and `iceberg`.
- To support writing data to the lakehouse, we currently use the `deltalake-rs` python bindings.
- For testing purposes, we use the `minio` instance at `http://192.168.18.206:9000`.

## Installation

This package is published to the PyPI repository, so you can install it using `pip` anywhere:
```bash
pip install dadude
```

## Usage

First export the following environment variables:
```bash
export STORAGE_ACCESS_KEY_ID=xxx STORAGE_SECRET_ACCESS_KEY=xxx STORAGE_ENDPOINT_URL=http://192.168.18.206:9000
```

Then you can use the `dadude` module CLI to interact with the lakehouse:
```bash
python -m dadude.cli.read_table staging <table_name> --save_dir <save_dir>
python -m dadude.cli.write_table write_json_table --local_json_file_path data/silver/xxx.json
```