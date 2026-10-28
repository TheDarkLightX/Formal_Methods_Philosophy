#!/usr/bin/env python3
"""Independent exhaustive checks of exported finite tables, not deployed code."""
import json
from collections import deque
from pathlib import Path

root = Path(__file__).resolve().parent
evidence = json.loads((root / 'zal-evidence.json').read_text())
layers = evidence['zal_layers']['data']
nodes = {n['id']: n['model'] for n in layers['nodes']}

def table(model):
    return {(s, event, tuple(context)): tuple(tuple(o) for o in outcomes)
            for s, (event, context), outcomes in model['rows']}

def image(outcomes, mapping, keep_reason):
    return {(decision, reason if keep_reason else '', mapping[state])
            for decision, reason, state in outcomes}

def check_map(source, target, mapping, exact, keep_reason):
    dst = table(target)
    assert mapping[source['initial']] == target['initial']
    for (state, event, context), outcomes in table(source).items():
        observed = image(outcomes, mapping, keep_reason)
        allowed = set(dst[(mapping[state], event, context)])
        assert observed == allowed if exact else observed <= allowed
    return len(source['rows'])

def explore(model):
    """Count accepted reserves, saturated at 2; exhaust every reachable pair."""
    rows = table(model)
    start = (model['initial'], 0)
    paths = {start: []}
    queue = deque([start])
    first_bad = None
    while queue:
        state, count = queue.popleft()
        for (s, event, context), outcomes in rows.items():
            if s != state:
                continue
            for decision, reason, next_state in outcomes:
                next_count = min(2, count + int(event == 'reserve' and decision == 'Accept'))
                key = (next_state, next_count)
                step = {'state': state, 'event': event, 'authorized': context[0],
                        'decision': decision, 'reason': reason, 'next_state': next_state}
                path = paths[(state, count)] + [step]
                if next_count == 2 and first_bad is None:
                    first_bad = path
                if key not in paths:
                    paths[key] = path
                    queue.append(key)
    return {'reachable_control_monitor_pairs': len(paths),
            'at_most_one_accepted_reserve': first_bad is None,
            'counterexample': first_bad}

audit = next(e for e in layers['edges'] if e['id'] == 'audit_erasure')
occupancy = next(e for e in layers['edges'] if e['id'] == 'hide_identity')
report = {'scope': 'Finite exported transition tables; full reachability for safety; no production-code or authentication claim.'}
report['six_to_three_exact_rows'] = check_map(nodes['detailed'], nodes['lifecycle'], audit['mapping'], True, True)
report['three_to_two_sound_rows'] = check_map(nodes['lifecycle'], nodes['occupancy'], occupancy['mapping'], False, False)
report['refined_exact_rows'] = check_map(nodes['lifecycle'], layers['refinement']['abstract'], layers['refinement']['mapping'], True, False)

left, right = table(nodes['lifecycle']), table(nodes['alternative'])
differences = [key for key in left if left[key] != right[key]]
assert differences == [('released', 'reserve', (True,))]
report['policy_difference'] = {'state': 'released', 'event': 'reserve', 'authorized': True}
for name in ['lifecycle', 'alternative']:
    rows = table(nodes[name])
    assert rows[('unseen', 'reserve', (True,))] == (('Accept', '', 'held'),)
    assert all(decision == 'Reject' for (_, _, ctx), outcomes in rows.items() if not ctx[0]
               for decision, _, _ in outcomes)
report['authorization_and_first_admission'] = 'both finite models satisfy their Boolean-input rules'

report['one_use'] = explore(nodes['lifecycle'])
report['reusable'] = explore(nodes['alternative'])
report['occupancy'] = explore(nodes['occupancy'])
assert report['one_use']['at_most_one_accepted_reserve']
assert not report['reusable']['at_most_one_accepted_reserve']
assert not report['occupancy']['at_most_one_accepted_reserve']
assert len(report['occupancy']['counterexample']) == 3

# Lift exactly the abstract trace returned by ZAL, preserving observed classes.
possible = {nodes['lifecycle']['initial']}
failure_step = None
for i, step in enumerate(layers['witness']['trace'], 1):
    possible = {next_state for state in possible
                if occupancy['mapping'][state] == step['state']
                for decision, _, next_state in left[(state, step['event'], (step['context']['authorized'],))]
                if decision == step['outcome'] and occupancy['mapping'][next_state] == step['next_state']}
    if not possible:
        failure_step = i
        break
assert failure_step == 3
report['spurious_trace_first_impossible_step_one_based'] = failure_step

checked = evidence['requirement_check']['data']['record']['result']
assert checked['status'] == 'refuted'
assert checked['result']['status'] == 'inconsistent-request'
assert checked['result']['witness'] == ['released', 'reserve', 'yes']
conflict = next(r for r in checked['conjoined']['rows'] if r['input'] == ['released', 'reserve', 'yes'])
assert conflict['outputs'] == []
assert evidence['requirement_replay']['data']['records'] == [
    {'id': 'r1', 'status': 'matches-replay', 'replayed_result_status': 'refuted'}]
report['requirement_conjunction'] = 'inconsistent at released, reserve, authorized; remote replay matched the refutation'
report['status'] = 'all independent finite-table checks passed'
print(json.dumps(report, indent=2))
