#!/usr/bin/env python3

import typer
from graphlib import TopologicalSorter
from typing import List
from pathlib import Path

app = typer.Typer(add_completion=False, help='')

MappingPath = Path(__file__).parent.parent / 'mappings'


def parse(line: str) -> List[str]:
    if '#' not in line and '[' in line and ']' in line:
        pegs = line.split('[')[1].split(']')[0].split(',')
        pegs = [p.strip(' ').strip('"').strip('<').strip('>') for p in pegs]
        if len(pegs) == 4:
            return pegs
        else:
            typer.echo(f'error len != 4 {line}')
    return None


@app.command()
def check():
    public = set()
    private = set()

    graph = {}

    for f in MappingPath.glob('*.imp'):
        for line in f.read_text().split('\n'):
            if pegs := parse(line):
                if pegs[3] == 'public' and 'bits/' in pegs[2]:
                    continue
                if pegs[1] == 'public':
                    public.add(pegs[0])
                else:
                    private.add(pegs[0])
                if pegs[3] == 'public':
                    public.add(pegs[2])
                else:
                    private.add(pegs[2])

                if pegs[0] in graph:
                    graph[pegs[0]].add(pegs[2])
                else:
                    graph[pegs[0]] = {pegs[2]}

    typer.echo(f'public: {len(public)}, private: {len(private)}')
    inter = public.intersection(private)

    cycle_deps = set([
        'boost/contract/detail/checking.hpp',
        'boost/numeric/odeint/integrate/detail/integrate_adaptive.hpp',
        'boost/numeric/odeint/iterator/integrate/detail/integrate_const.hpp',
        'boost/python/detail/type_list_impl.hpp',
        'boost/variant/detail/multivisitors_cpp14_based.hpp',
    ])

    for f in MappingPath.glob('*.imp'):
        result = []
        for line in f.read_text().split('\n'):
            if pegs := parse(line):
                if pegs[3] == 'public' and 'bits/' in pegs[2]:
                    continue
                if pegs[2] in cycle_deps:
                    continue
                if pegs[3] == 'public' and pegs[2] in inter:
                    continue
            result.append(line)
        f.write_text('\n'.join(result))

    print(public.intersection(private))
    t = list(TopologicalSorter(graph=graph).static_order())


if __name__ == "__main__":
    app()
