import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter"))
from vector_snapshot import validate


class VectorSnapshotTests(unittest.TestCase):
    def test_rejects_wrong_identity_and_nonfinite_vectors(self):
        chunks = [{"id": "a"}]
        snapshot = {"strategy": "C", "dimensions": 384, "vectors": [{"id": "a", "embedding": [1.] * 384}]}
        validate(snapshot, chunks)
        snapshot["vectors"][0]["embedding"][0] = float("nan")
        with self.assertRaises(ValueError):
            validate(snapshot, chunks)
        snapshot["vectors"][0]["embedding"][0] = 1.
        snapshot["vectors"][0]["id"] = "b"
        with self.assertRaises(ValueError):
            validate(snapshot, chunks)


if __name__ == "__main__":
    unittest.main()
