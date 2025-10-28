import argparse
import sys
from .reader import build_cache, default_cache_dir

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="fastjsonlreader",
        description="Utilities for fast random access to JSONL via .bcl caches",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Primary command name: "index" (clearer), plus alias "create-bcl"
    p_index = sub.add_parser("index", help="Build the .bcl cache for a JSONL file")
    p_index.add_argument("file", help="Path to the JSONL file")
    p_index.add_argument("--num-lines", type=int, default=None,
                         help="Only index the first N lines")
    p_index.add_argument("--cache-dir", default=None,
                         help="Cache directory (default: ~/.fastjsoncache)")
    p_index.add_argument("--force", action="store_true",
                         help="Rebuild even if cache exists")

    # Backwards-compatible alias
    p_alias = sub.add_parser("create-bcl", help="Alias for `index`")
    p_alias.add_argument("file", help="Path to the JSONL file")
    p_alias.add_argument("--num-lines", type=int, default=None)
    p_alias.add_argument("--cache-dir", default=None)
    p_alias.add_argument("--force", action="store_true")

    # Optional: show where caches default to
    p_where = sub.add_parser("cache-dir", help="Print the default cache directory")

    args = parser.parse_args(argv)

    if args.cmd in {"index", "create-bcl"}:
        cache_path = build_cache(
            file_path=args.file,
            cache_dir=args.cache_dir,
            num_lines=args.num_lines,
            force=args.force,
        )
        print(cache_path)
        return 0
    elif args.cmd == "cache-dir":
        print(default_cache_dir())
        return 0

    parser.print_help()
    return 1

if __name__ == "__main__":
    raise SystemExit(main())

