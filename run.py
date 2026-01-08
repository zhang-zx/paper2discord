#!/usr/bin/env python3
import sys
import os

# Ensure the package can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_paper_digest.main import start_scheduler, run_daily_digest
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true", help="Run the digest immediately")
    args = parser.parse_args()
    
    if args.run_now:
        run_daily_digest()
    else:
        start_scheduler()
