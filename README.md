# KubeCon Seattle 2018

This repository contains examples and code from the Deep Dive: Open Policy Agent
session from KubeCon Seattle 2018.

## Data Filtering demo

> Requires Python and virtualenv.

1. Start OPA in the example directory

```bash
opa run -w -s sql/example
```

2. Start example server

```bash
cd sql
virtualenv env
source env/bin/activate
pip install -r requirements.txt
pip install -e .
python data_filter_example/server.py
```

3. Load the example in your browser at localhost:5000

You can change the data filtering policy at **sql/example/filtering.rego** and
the OPA server will reload it automatically.

## WebAssembly demo

1. Build the WebAssembly binary for the example policy:

```bash
cd wasm
opa build -d example.rego 'data.example.allow = true'
```

2. Run the example Node JS code that invokes the Wasm binary:

```bash
node app.js '{"method": "get", "path": "/trades"}'
```

```
node app.js '{"method": "post", "path": "/trades"}'
```

```
node app.js '{"method": "post", "path": "/trades", "role": "admin"}'
```
