import json
import os
import subprocess
import unittest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLI = os.path.join(REPO_ROOT, "bin", "meteorites")
DATASET = os.path.join(REPO_ROOT, "docs", "meteorite_landings.json")


class TestMeteoritesCLI(unittest.TestCase):
    def test_json_output_matches_expected(self) -> None:
        proc = subprocess.run(
            [CLI, "--file", DATASET, "--json"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(proc.stdout)

        self.assertEqual(payload["count"], 1000)
        self.assertEqual(payload["max_mass"]["name"], "Sikhote-Alin")
        self.assertEqual(payload["max_mass"]["mass_g"], 23000000)
        self.assertEqual(payload["most_frequent_year"]["year"], "1933")
        self.assertEqual(payload["most_frequent_year"]["count"], 16)


if __name__ == "__main__":
    unittest.main()

