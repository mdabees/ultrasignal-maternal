"""Write reports/FROZEN.json: the sha256 of the detector and everything it depends on."""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from watcher.scoring import frozen_manifest
from watcher.util import ROOT

if __name__ == "__main__":
    manifest = frozen_manifest()
    with open(ROOT / "reports" / "FROZEN.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=1, sort_keys=True)
        handle.write("\n")
    print("detector_sha256", manifest["detector_sha256"])
    print("bundle_sha256  ", manifest["bundle_sha256"])
