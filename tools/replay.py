#!/usr/bin/env python3
"""Re-run decisions on supplied snapshots. Does not simulate outcomes or score."""
import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'CoreGeek' / 'src'))
from agent.brain import decide


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Request JSON or recorded JSONL')
    args = parser.parse_args()
    raw = args.input.read_text()
    try:
        records = [json.loads(raw)]
    except json.JSONDecodeError:
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    failures = 0
    for record in records:
        payload = record.get('request', record)
        started = perf_counter()
        try:
            response = {'roleCommandMap': decide(payload)}
            result = {'roundNo': payload['roundNo'], 'response': response,
                      'decisionMs': round((perf_counter() - started) * 1000, 3)}
            if 'response' in record:
                result['changed'] = response != record['response']
        except Exception as exc:
            failures += 1
            result = {'error': type(exc).__name__ + ': ' + str(exc)}
        print(json.dumps(result, ensure_ascii=False))
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
