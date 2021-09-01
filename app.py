import argparse
import os
import json

LINE_PREFIX = '*CHI:'

def main():
    parser = argparse.ArgumentParser(description='Parse sentences for Sankey chart.')
    parser.add_argument('input', type=str, nargs='+',
                        help='input files to be parsed')
    parser.add_argument('--trans', dest='trans', type=str,
                        help='transformations to be applied to input files before parsing them')

    args = parser.parse_args()

    for file in args.input:
        lines = list(map(lambda line: sanitize_line(line), get_lines(file)))
        words_line = list(map(lambda line: to_words(line), lines))
        result_dict, links = to_dict(words_line)

    print(json.dumps({
        'sankey': {
            'nodes': list(result_dict.values()),
            'links': links
        },
        'params': [0.5,0.25,0,0,0]
    }))

def get_lines(file_path):
    if not os.path.isfile(file_path):
        print(f'file {file_path}  does not exist.')
        return

    lines = []

    with open(file_path) as fp:
        line = fp.readline().strip()
        while line:
            if not line.startswith(LINE_PREFIX):
                lines[len(lines) - 1] += f' {line}'
            else:
                lines.append(line)

            line = fp.readline().strip()

    return lines

def sanitize_line(line):
    clean_line = ''
    skippers = [
        {'start': '[', 'end': ']', 'skipping': False},
        {'start': '<', 'end': '>', 'skipping': False},
        {'start': '(', 'end': ')', 'skipping': False},
        {'start': '&', 'end': ' ', 'skipping': False},
        {'start': '+', 'end': ' ', 'skipping': False},
    ]
    for c in line:
        skipping = False
        for skip in skippers:
            skipping = skip['skipping'] or skipping
        if not skipping:
            for skip in skippers:
                if skip['start'] == c:
                    skipping = True
                    skip['skipping'] = True

        for skip in skippers:
            if skip['end'] == c:
                skip['skipping'] = False
        if skipping:
            continue

        clean_line += c

    return clean_line

def to_words(line):
    return line.split(LINE_PREFIX)[1].split('.')[0].strip().split()

def to_dict(words_line):
    result = dict()
    indexes = dict()
    links = []

    count = -1
    for words in words_line:
        for i in range(len(words)):
            lower_word = words[i].lower()
            key = f'{lower_word}#{i}'
            if key not in result:
                count += 1
                indexes[key] = count
                result[key] = {
                    'layer': i + 1,
                    'value': 1,
                    'name': lower_word
                }
            else:
                result[key]['value'] += 1

    for words in words_line:
        previous_index = -1
        for i in range(len(words)):
            lower_word = words[i].lower()
            key = f'{lower_word}#{i}'

            if previous_index != -1:
                links.append({
                    'source': previous_index,
                    'target': indexes[key],
                    'value': result[key]['value']
                })
            previous_index = indexes[key]

    return (result, links)

main()
