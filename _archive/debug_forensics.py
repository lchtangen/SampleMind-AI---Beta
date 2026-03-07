
import sys
import os
import traceback
import time
from pathlib import Path

print("Debug: Forensics Analyzer Import Trace")
sys.path.append(str(Path.cwd() / "src"))

def test_import():
    try:
        t0 = time.time()
        
        print(f"[{time.time()-t0:.4f}] Importing processing.exceptions...")
        import samplemind.core.processing.exceptions
        print(f"[{time.time()-t0:.4f}] Passed.")

        print(f"[{time.time()-t0:.4f}] Importing processing.audio_pipeline...")
        import samplemind.core.processing.audio_pipeline
        print(f"[{time.time()-t0:.4f}] Passed.")

        print(f"[{time.time()-t0:.4f}] Importing processing.stem_separation...")
        import samplemind.core.processing.stem_separation
        print(f"[{time.time()-t0:.4f}] Passed.")
        
        print(f"[{time.time()-t0:.4f}] Importing processing.forensics_analyzer...")
        import samplemind.core.processing.forensics_analyzer
        print(f"[{time.time()-t0:.4f}] Passed.")
        
        return True
    except Exception:
        print("Import failed with exception:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_import()
