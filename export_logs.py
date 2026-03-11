#!/usr/bin/env python3
"""Export .glog files to JSON for the web visualizer."""
import bz2
import json
import os
import re

LOGS_DIR = os.path.join(os.path.dirname(__file__), 'server', 'logs')
OUT_FILE = os.path.join(os.path.dirname(__file__), 'visualizer', 'games.js')

TYPE_MAP = {82: 'R', 78: 'N', 66: 'B', 81: 'Q', 75: 'K', 80: 'P'}


def parse_sexpr(s):
    """Minimal S-expression parser."""
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == '(':
            tokens.append('(')
            i += 1
        elif c == ')':
            tokens.append(')')
            i += 1
        elif c == '"':
            j = i + 1
            while j < len(s) and s[j] != '"':
                j += 1
            tokens.append(s[i+1:j])
            i = j + 1
        elif c in ' \t\n\r':
            i += 1
        else:
            j = i
            while j < len(s) and s[j] not in '() \t\n\r"':
                j += 1
            tok = s[i:j]
            try:
                tok = int(tok)
            except ValueError:
                try:
                    tok = float(tok)
                except ValueError:
                    pass
            tokens.append(tok)
            i = j

    def read_list(pos):
        result = []
        pos += 1  # skip '('
        while pos < len(tokens) and tokens[pos] != ')':
            if tokens[pos] == '(':
                sub, pos = read_list(pos)
                result.append(sub)
            else:
                result.append(tokens[pos])
                pos += 1
        return result, pos + 1  # skip ')'

    results = []
    pos = 0
    while pos < len(tokens):
        if tokens[pos] == '(':
            sub, pos = read_list(pos)
            results.append(sub)
        else:
            pos += 1
    return results


def extract_states(data):
    """Extract board states from parsed log data."""
    states = []
    players = None
    winner_info = None

    for expr in data:
        if not expr:
            continue
        if expr[0] == 'status':
            state = {'pieces': [], 'moves': [], 'turn': None}
            for sub in expr[1:]:
                if not sub:
                    continue
                if sub[0] == 'game':
                    state['turn'] = sub[1]  # turn number
                    state['currentPlayer'] = sub[2]  # whose turn
                elif sub[0] == 'Piece':
                    for p in sub[1:]:
                        if isinstance(p, list) and len(p) >= 6:
                            piece = {
                                'id': p[0],
                                'owner': p[1],
                                'file': p[2],
                                'rank': p[3],
                                'hasMoved': p[4],
                                'type': TYPE_MAP.get(p[5], '?')
                            }
                            state['pieces'].append(piece)
                elif sub[0] == 'Move':
                    for m in sub[1:]:
                        if isinstance(m, list) and len(m) >= 6:
                            move = {
                                'id': m[0],
                                'fromTurn': m[1],
                                'fromFile': m[2],
                                'toFile': m[3],
                                'toRank': m[4],
                                'type': TYPE_MAP.get(m[5], '?')
                            }
                            state['moves'].append(move)
                elif sub[0] == 'Player':
                    players = []
                    for pl in sub[1:]:
                        if isinstance(pl, list) and len(pl) >= 3:
                            players.append({
                                'id': pl[0],
                                'name': pl[1],
                                'time': pl[2]
                            })
                    state['players'] = players
            states.append(state)
        elif expr[0] == 'game-winner':
            winner_info = {
                'gameId': expr[1] if len(expr) > 1 else None,
                'name': expr[2] if len(expr) > 2 else None,
                'playerId': expr[3] if len(expr) > 3 else None,
                'reason': expr[4] if len(expr) > 4 else None
            }

    return states, winner_info


def process_logs():
    games = {}
    for f in sorted(os.listdir(LOGS_DIR)):
        if not f.endswith('.glog'):
            continue
        gid = f.replace('.glog', '')
        with open(os.path.join(LOGS_DIR, f), 'rb') as fh:
            raw = bz2.decompress(fh.read()).decode('utf-8', errors='replace')

        parsed = parse_sexpr(raw)
        states, winner = extract_states(parsed)

        # Deduplicate consecutive identical states
        unique_states = []
        for s in states:
            if not unique_states or s['turn'] != unique_states[-1]['turn']:
                unique_states.append(s)

        if len(unique_states) > 1:  # skip trivially short games
            games[gid] = {
                'states': unique_states,
                'winner': winner
            }

    return games


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    games = process_logs()
    with open(OUT_FILE, 'w') as f:
        f.write('const GAMES = ')
        json.dump(games, f)
        f.write(';\n')
    print(f"Exported {len(games)} games to {OUT_FILE}")
    for gid, g in sorted(games.items(), key=lambda x: int(x[0])):
        w = g['winner']
        reason = w['reason'] if w else 'unknown'
        print(f"  Game {gid}: {len(g['states'])} turns - {reason}")
