#!/usr/bin/env python3

import argparse
import sys
import json
import re
from cfour_parser.util import skip_to
from cfour_parser.text import pretty_introduce_section


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('QUADRATURE')
    parser.add_argument('-j', '--json', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    args = parser.parse_args()
    return args


def find_catches(lines, highlights, offset: int = 0):
    """
    First step on the way of parsing a section of the CFOUR's output is to spot
    places that mark opening of new sections or data points, these are called
    catches.

    Then use the turner function to turn this catch into a section template,
    i.e., try to find an end of the section, its beginning (if it is earlier or
    later than the catch line), ...

    """

    catches = list()
    for ln, line in enumerate(lines[offset:]):
        for highlight in highlights:
            pattern = highlight['pattern']
            match = pattern.match(line)
            if match is None:
                continue
            catch = {
                'name': highlight['name'],
                'start': ln + offset,
                'end': None,
                'match': match,
                'turner': highlight['turner'],
                'parser': highlight['parser'],
                'sections': [],
                'data': {},
                'metadata': {},
            }
            catches += [catch]
            break

    return catches


def catch2section_frequency(catch, lines, end_cap: int = None):
    """
    Find the end of the section
    """
    start = catch['start']
    header_offset = 3
    for end, line in enumerate(lines[start + header_offset:]):
        if line[0] == "%":
            break

    end += header_offset + start

    if end_cap is not None:
        catch['end'] = min(end, end_cap)
    else:
        catch['end'] = end


def parse_frequency(catch, lines, offset):
    catch['data']['frequency, cm-1'] = float(lines[1])

    nmodes = []
    for line in lines[3:]:
        nmodes += [float(i) for i in line.split()]

    name = 'back-tranformed dimensionless normal coordinates (in bohr)'
    catch['data'][name] = nmodes


def catch2section_reference(catch, lines, end_cap: int = None):
    """
    Find the end of the section
    """
    start = catch['start']
    end = start + len(lines[start:])

    if end_cap is not None:
        catch['end'] = min(end, end_cap)
    else:
        catch['end'] = end


def parse_reference(catch, lines, offset):
    geometry = []
    for line in lines[1:]:
        geometry += [float(x) for x in line.split()]

    catch['data']['Reference (undisplaced) coordinates'] = geometry


def parse_quadrature(quadrature_lines):

    quadrature = {
        'name': 'quadrature',
        'start': 0,
        'end': len(quadrature_lines),
        'sections': [],
        'data': {},
        'metadata': {},
    }

    offset = quadrature['start']

    highlights = [
        {'pattern': re.compile(r'% frequency \(in cm\*\*-1\)'),
         'name': 'dimensionless normal coordinates',
         'turner': catch2section_frequency,
         'parser': parse_frequency,
         },
        {'pattern': re.compile(r'% Reference \(undisplaced\) coordinates are: '),
         'name': 'reference coordinates',
         'turner': catch2section_reference,
         'parser': parse_reference,
         },
        # {'pattern': re.compile(r''),
        #  'name': '',
        #  'turner': None,
        #  'parser': None,
        #  },
    ]

    catches = find_catches(quadrature_lines, highlights, offset)
    for catch in catches:
        turner = catch['turner']
        turner(catch, quadrature_lines, end_cap=len(quadrature_lines))
        parser = catch['parser']
        start = catch['start']
        end = catch['end']
        parser(catch, quadrature_lines[start:end], offset=start)

        del catch['turner']
        del catch['parser']
        del catch['match']

        quadrature['sections'] += [catch]

    return quadrature


def main():
    args = get_args()
    with open(args.QUADRATURE, 'r') as quadrature_file:
        quadrature_lines = quadrature_file.readlines()

    quadrature = parse_quadrature(quadrature_lines)

    if args.verbose is True:
        pretty_introduce_section(quadrature, 1)

    if args.json is True:
        print(json.dumps(quadrature))


if __name__ == "__main__":
    main()
