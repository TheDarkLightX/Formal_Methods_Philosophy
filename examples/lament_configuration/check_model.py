#!/usr/bin/env python3
"""Exhaustive checks of the declared toy graph; standard library only."""
import json
from collections import deque
from pathlib import Path

root = Path(__file__).resolve().parent
model = json.loads((root / 'model.json').read_text())
zal = json.loads((root / 'zal-evidence.json').read_text())
actions = model['actions']
safe_states = set(model['safe_states'])
safe_effects = set(model['safe_effects'])

def tab(machine):
    rows = machine['rows']
    table = {(s, a): (n, e) for s, a, n, e in rows}
    assert len(table) == len(rows), 'duplicate rows'
    assert set(table) == {(s, a) for s in machine['states'] for a in actions}
    assert all(n in machine['states'] for n, e in table.values())
    return table

def reach(machine):
    table = tab(machine)
    paths = {model['initial']: []}
    queue = deque(paths)
    bad = None
    while queue:
        state = queue.popleft()
        for action in actions:
            next_state, effect = table[(state, action)]
            path = paths[state] + [action]
            if (next_state not in safe_states or effect not in safe_effects) and bad is None:
                bad = {'actions': path, 'next_state': next_state, 'effect': effect}
            if next_state not in paths:
                paths[next_state] = path
                queue.append(next_state)
    return {'states': sorted(paths), 'reward_path': paths.get('Reward'), 'bad_path': bad}

original = reach(model['unsafe'])
redesigned = reach(model['redesigned'])
safe_table = tab(model['redesigned'])
assert model['initial'] in safe_states
assert set(model['redesigned']['states']) == safe_states
assert all(n in safe_states and e in safe_effects for n, e in safe_table.values())
assert original['bad_path']['actions'] == ['Twist', 'Slide', 'Twist']
assert redesigned['bad_path'] is None
assert redesigned['reward_path'] == ['Twist', 'Slide']
assert len(safe_table) == 9

# State labels alone do not prevent a forbidden effect. Detect this mutation.
mutant = dict(model['redesigned'])
mutant['rows'] = [[s, a, n, 'Summon' if (s, a) == ('Reward', 'Twist') else e]
                  for s, a, n, e in model['redesigned']['rows']]
assert all(n in safe_states for s, a, n, e in mutant['rows'])
mutant_result = reach(mutant)
assert mutant_result['bad_path'] is not None
assert mutant_result['bad_path']['next_state'] == 'Reward'
assert mutant_result['bad_path']['effect'] == 'Summon'

# Read the observed ZAL meaning: upper bound is exclusive.
document = zal['good_check']['data']['document']
spec = document['definition']
assert (spec['lower'], spec['upper']) == (0, 3)
def admits(bounds, byte):
    return bounds['lower'] <= byte < bounds['upper']
admitted = [b for b in range(256) if admits(spec, b)]
assert admitted == [model['encoding'][s] for s in model['safe_states']]
assert model['encoding']['Summon'] not in admitted
for record in document['records']:
    bounds = record['request']['candidate']
    mismatches = [b for b in range(256) if admits(spec, b) != admits(bounds, b)]
    result = record['result']
    assert result['checked_cases'] == 256
    assert result['mismatch_count'] == len(mismatches)
    if mismatches:
        assert mismatches == [3]
        assert result['status'] == 'refuted'
        assert result['counterexample'] == {'actual': True, 'byte': 3, 'expected': False}
    else:
        assert result['status'] == 'checked'
        assert result['counterexample'] is None
assert zal['replay']['data']['records'] == [
    {'id': 'r1', 'status': 'matches-replay', 'replayed_result_status': 'refuted'},
    {'id': 'r2', 'status': 'matches-replay', 'replayed_result_status': 'checked'}]

print(json.dumps({
    'status': 'all declared finite-model checks passed',
    'original_rows': len(model['unsafe']['rows']),
    'redesigned_rows': len(safe_table),
    'unsafe': original, 'redesigned': redesigned,
    'state_only_check_misses_effect_mutation': mutant_result['bad_path'],
    'state_admission': {'domain_size': 256, 'admitted': admitted, 'excluded_summon_code': 3},
    'zal_replay': zal['replay']['data']['records'],
    'scope': 'Complete reachability and row enumeration of the invented finite model. No theorem prover, native Rust, physical mechanism or arbitrary program was verified.'
}, indent=2))
