# fastjsonlreader

Disclaimer: README written by GPT-5

Fast random access to JSONL files via a cached **byte-count lookup index** (`.bcl`).  

JSONL (JSON Lines) is a common format where each line is a valid JSON object.  
Normally, accessing the *nth* line requires scanning from the beginning.  
`fastjsonlreader` builds and reuses a lightweight cache of byte offsets so you can jump directly to any line in **O(1) file seek time**.

---

## 🚀 Features
- **Fast random access** to JSON objects in large `.jsonl` files.  
- **Cache file (`.bcl`)** stores line lengths or offsets for reuse.  
- **Command-line interface (CLI)** for building caches ahead of time.  
- **Python API** for easy integration into data pipelines.  
- Works on **any size JSONL file** (limited only by disk size).  
- Simple, dependency-free implementation (only standard library).  

---

## 📦 Installation

From PyPI:

```bash
pip install fastjsonlreader
```

From source:
```bash
git clone https://github.com/yourname/fastjsonlreader.git
cd fastjsonlreader
pip install .
```

For development:
```bash
pip install -e .
```

## 🔧 Usage

### CLI

You can build the index (cache file) before using it in code:

```bash
# Build the index (preferred command name)
python -m fastjsonlreader index data.jsonl

# Or using the alias:
python -m fastjsonlreader create-bcl data.jsonl

# Limit to the first N lines:
python -m fastjsonlreader index data.jsonl --num-lines 1000000

# Force rebuild even if a cache exists:
python -m fastjsonlreader index data.jsonl --force

# Show where caches are stored by default:
python -m fastjsonlreader cache-dir
```

### Python API
```python
from fastjsonlreader import FastJSONLReader, build_cache

# Build cache manually (optional; normally auto-generated)
build_cache("data.jsonl")

# Load reader
reader = FastJSONLReader("data.jsonl")

print(len(reader))       # number of lines in the file
print(reader[0])         # first JSON object (parsed as dict)
print(reader[12345])     # 12,346th JSON object
```
The reader behaves like a list:
* __len__ → number of lines
* __getitem__ → parsed JSON object

## ⚡ Performance
* The first time you use a file, fastjsonlreader scans it and writes a .bcl file with the byte lengths of each line.
* Subsequent runs load the .bcl instead of rescanning the file, saving time.
* Lookups currently require summing the line lengths before the target line. For extremely large files, an offset-based cache (storing cumulative sums directly) is recommended — planned for a future release.

## 📂 Cache Files

* Cache files are stored in ~/.fastjsoncache/ by default (one .bcl per JSONL file).
* You can override this with --cache-dir or when initializing the reader:
```python
reader = FastJSONLReader("data.jsonl", cache_dir="/tmp/mycache")
```

## 📄 License

MIT License © 2025 Rafael Rivera Soto