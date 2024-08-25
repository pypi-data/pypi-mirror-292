from collections import defaultdict


def index(makefile='makefile'):
    targets = dict()
    for n, line in enumerate(open(makefile)):
        first, line = ord(line[0]), line.rstrip()
        if first == 9:
            pass
        elif first == 10:
            end = n-1
            targets[target] = start, end
        else:
            target, _, prereq = line.partition(':')
            start = n
    return targets


def parse(makefile='makefile'):
    targets = defaultdict(list)
    for line in open(makefile):
        first, line = ord(line[0]), line.rstrip()
        if first == 9:
            targets[target].append(line)
        elif first == 10:
            pass
        else:
            target, _, prereq = line.partition(':')
            if pre := prereq.strip():
                targets[target].append(pre)
    return targets


def show(makefile='makefile'):
    for target, commands in parse(makefile).items():
        print(f'{target}:')
        for cmd in commands:
            print(f'    {cmd}')
        print()
