#!/usr/bin/env python3
"""Deterministic synthetic model; not a ReMAP or real training validation."""
import argparse
import hashlib
import json
from pathlib import Path


def simulate(horizon, interval, checkpoint_cost, failures):
    if any(type(x) is not int or x <= 0 for x in (horizon, interval, checkpoint_cost)):
        raise ValueError('horizon, interval and checkpoint cost must be positive integers')
    if any(type(t) is not int or not 1 <= t <= horizon for t in failures):
        raise ValueError('failure ticks must be integers within the horizon')
    if len(set(failures)) != len(failures):
        raise ValueError('duplicate failure ticks')
    failures = set(failures)
    saved = pending = lost = overhead = recovery = remaining = 0
    for tick in range(1, horizon + 1):
        if tick in failures:
            lost += pending
            pending = remaining = 0
            recovery += 1
        elif remaining:
            overhead += 1
            remaining -= 1
            if remaining == 0:
                saved += pending
                pending = 0
        else:
            pending += 1
            if pending == interval:
                remaining = checkpoint_cost
    assert saved + pending + lost + overhead + recovery == horizon
    return {
        'interval': interval, 'deliveredCorrectWorkTicks': saved,
        'uncommittedWorkTicks': pending, 'lostWorkTicks': lost,
        'checkpointOverheadTicks': overhead, 'recoveryTicks': recovery,
        'deliveredCorrectWorkPerWallTick': saved / horizon,
    }


def evaluate(path):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if data.get('scope') != 'synthetic' or data.get('modelVersion') != 'integer-checkpoint-v1':
        raise ValueError('Only the specified synthetic model is supported')
    if not data.get('intervals'):
        raise ValueError('At least one interval is required')
    return {
        'scope': 'synthetic', 'modelVersion': data['modelVersion'],
        'inputSha256': hashlib.sha256(raw).hexdigest(),
        'sourceSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'metric': 'Persisted correct work ticks / fixed wall-clock horizon ticks',
        'assumptions': data['assumptions'],
        'results': [simulate(data['horizonTicks'], n, data['checkpointCostTicks'],
                             data['failureTicks']) for n in data['intervals']],
        'limitations': ['Synthetic, deterministic; no statistical inference.',
                       'Correctness is assumed, not measured on a training system.',
                       'Does not verify a real product KPI or ReMAP implementation.'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
