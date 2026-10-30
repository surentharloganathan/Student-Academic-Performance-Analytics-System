
import os
import sys
import json
import subprocess
import time
import threading

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

SPARK_PYTHON = BASE_DIR / "venv-spark" / "Scripts" / "python.exe"
SPARK_SCRIPT = BASE_DIR / "spark_analysis.py"


# Cache configuration
_cached_analytics = None
_cache_time = 0
CACHE_DURATION = 30

_cache_lock = threading.Lock()


def get_spark_analytics(force_refresh=False):

    global _cached_analytics, _cache_time

    with _cache_lock:

        # Check whether valid cached data exists
        if (
            not force_refresh
            and _cached_analytics is not None
            and time.time() - _cache_time < CACHE_DURATION
        ):
            print("Using cached Spark analytics")
            return _cached_analytics

        print("Running fresh Spark analytics...")

        env = os.environ.copy()

        java_home = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

        env["JAVA_HOME"] = java_home
        env["PATH"] = java_home + r"\bin;" + env.get("PATH", "")

        env["PYSPARK_PYTHON"] = str(SPARK_PYTHON)
        env["PYSPARK_DRIVER_PYTHON"] = str(SPARK_PYTHON)

        result = subprocess.run(
            [str(SPARK_PYTHON), str(SPARK_SCRIPT)],
            cwd=str(BASE_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )

        print("Spark return code:", result.returncode)

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        # Extract JSON output
        for line in reversed(result.stdout.splitlines()):

            try:
                data = json.loads(line)

                if isinstance(data, dict):

                    if "error" in data:
                        raise RuntimeError(data["error"])

                    # Save analytics in cache
                    _cached_analytics = data
                    _cache_time = time.time()

                    return _cached_analytics

            except json.JSONDecodeError:
                continue

        raise RuntimeError("Spark did not return valid JSON output.")

def invalidate_spark_cache():

    global _cached_analytics, _cache_time

    with _cache_lock:
        _cached_analytics = None
        _cache_time = 0

    print("Spark analytics cache cleared.")
