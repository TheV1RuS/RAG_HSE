from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse

from src.fill_testset import fill_testset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="test_set_Shalugin_Dmitrii.xlsx")
    parser.add_argument("--out", dest="out", default="outputs/test_set_Shalugin_Dmitrii.xlsx")
    args = parser.parse_args()

    out = fill_testset(args.inp, args.out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
