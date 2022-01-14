import re
from dateparser.search import search_dates
from collections import defaultdict

from utils import Neighbour


flatten_list = lambda irregular_list:[element for item in irregular_list for element in flatten_list(item)] if type(irregular_list) is list else [irregular_list]


def get_invoice_nums(all_words, height, width, words):
    inv_nums = []
    invoice_no_re = r'^[0-9a-zA-Z-]+$'
    for word in all_words:
        if not re.search('\d', word['text']):
            continue
        if len(word['text']) < 2:
            continue
        if len(word['text'].split('-')) > 2:
            continue
        result = re.findall(invoice_no_re, word['text'])
        if result:
            cad = {
                'text': word['text'],
                'x1': word['left'],
                'y1': word['top'],
                'x2': word['left'] + word['width'],
                'y2': word['top'] + word['height']
            }
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.3),
                                                  int(height * 0.02), width,
                                                  height)

            neighbours_text_clean = [
                it['text'].lower().replace('#', '').replace(':', '') for it in
                neighbours]
            neighbours_text = [it['text'].lower() for it in neighbours]

            if not neighbours:
                inv_nums.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })

            if 'invoice' in neighbours_text_clean or '#' in neighbours_text:
                inv_nums.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })

    return inv_nums


def get_po(all_words, height, width, words):
    inv_nums = []
    invoice_no_re = r'^[0-9a-zA-Z-]+$'
    for word in all_words:
        if not re.search('\d', word['text']):
            continue
        if len(word['text']) < 2:
            continue
        if len(word['text'].split('-')) > 2:
            continue
        result = re.findall(invoice_no_re,word['text'])
        if result:
            cad = {
                'text': word['text'],
                'x1': word['left'],
                'y1': word['top'],
                'x2': word['left'] + word['width'],
                'y2': word['top'] + word['height']
            }
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.3),
                                                 int(height * 0.02), width, height)
            neighbours_text = [it['text'].lower().replace('#','').replace(':','') for it in neighbours]

            if ('po' in neighbours_text and 'box' not in neighbours_text) or ('p.o.' in neighbours_text and 'box' not in neighbours_text) or 'purchase' in neighbours_text or ('order' in neighbours_text and 'date' not in neighbours_text):
                inv_nums.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })

    return inv_nums


def get_dates(all_text, all_words, height, width, words):
    dates, all_dates = [], []
    indices = []
    matches = search_dates(all_text)

    for match in matches:
        text = match[0]

        if len(text.strip()) < 8:
            continue
        if '$' in text:
            continue
        if 'day' in text:
            continue
        if '%' in text:
            continue
        if '#' in text:
            continue
        if ':' in text:
            continue
        if 'hour' in text.lower():
            continue
        if (len(text) > 10) and not (re.search('[a-zA-Z]', text)):
            continue
        if len(text) > 15:
            continue
        if text.isdigit():
            continue
        if '(' in text:
            continue

        token_length = len(text.split(' '))
        idx = all_text.find(match[0])
        text_len = len(text)
        index = len(all_text[:idx].strip().split(' '))
        if idx == 0:
            index = 0

        replaced_text = ' '.join(['*' * len(i) for i in text.split(' ')])

        indices.append(list(range(index, index + token_length)))

        index += token_length
        all_text = all_text[:idx + text_len].replace(text,
                                                     replaced_text) + all_text[
                                                                      idx + text_len:]

    for date_indices in indices:
        date = ''
        left, top, right, bottom = [], [], [], []
        for i in date_indices:
            date += ' ' + all_words[i]['text']
            left.append(all_words[i]['left'])
            top.append(all_words[i]['top'])
            right.append(all_words[i]['left'] + all_words[i]['width'])
            bottom.append(all_words[i]['top'] + all_words[i]['height'])
        cad = {
            'text': all_words[i]['text'],
            'x1': all_words[i]['left'],
            'y1': all_words[i]['top'],
            'x2': all_words[i]['left'] + all_words[i]['width'],
            'y2': all_words[i]['top'] + all_words[i]['height']
        }
        neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.3),
                                              int(height * 0.02), width,
                                              height)

        if not neighbours:
            all_dates.append({
                'text': date.strip(),
                'x1': min(left),
                'y1': min(top),
                'x2': max(right),
                'y2': max(bottom)
            })

        for item in neighbours:
            if 'date' in item['text'].lower() or 'issued' in item['text'].lower():
                all_dates.append({
                    'text': date.strip(),
                    'x1': min(left),
                    'y1': min(top),
                    'x2': max(right),
                    'y2': max(bottom)
                })

    return all_dates


def due_dates(all_text, all_words, height, width, words):
    dates, all_dates = [], []
    indices = []
    matches = search_dates(all_text)

    for match in matches:
        text = match[0]

        if len(text.strip()) < 8:
            continue
        if '$' in text:
            continue
        if 'day' in text:
            continue
        if '%' in text:
            continue
        if '#' in text:
            continue
        if ':' in text:
            continue
        if 'hour' in text.lower():
            continue
        if (len(text) > 10) and not (re.search('[a-zA-Z]', text)):
            continue
        if len(text) > 15:
            continue
        if text.isdigit():
            continue
        if '(' in text:
            continue

        token_length = len(text.split(' '))
        idx = all_text.find(match[0])
        text_len = len(text)
        index = len(all_text[:idx].strip().split(' '))
        if idx == 0:
            index = 0

        replaced_text = ' '.join(['*' * len(i) for i in text.split(' ')])

        indices.append(list(range(index, index + token_length)))

        index += token_length
        all_text = all_text[:idx + text_len].replace(text,
                                                     replaced_text) + all_text[
                                                                      idx + text_len:]

    for date_indices in indices:
        date = ''
        left, top, right, bottom = [], [], [], []
        for i in date_indices:
            date += ' ' + all_words[i]['text']
            left.append(all_words[i]['left'])
            top.append(all_words[i]['top'])
            right.append(all_words[i]['left'] + all_words[i]['width'])
            bottom.append(all_words[i]['top'] + all_words[i]['height'])
        cad = {
            'text': all_words[i]['text'],
            'x1': all_words[i]['left'],
            'y1': all_words[i]['top'],
            'x2': all_words[i]['left'] + all_words[i]['width'],
            'y2': all_words[i]['top'] + all_words[i]['height']
        }
        neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.3),
                                              int(height * 0.02), width,
                                              height)

        for item in neighbours:
            if 'due' in item['text'].lower():
                all_dates.append({
                    'text': date.strip(),
                    'x1': min(left),
                    'y1': min(top),
                    'x2': max(right),
                    'y2': max(bottom)
                })

    return all_dates


def get_amounts(all_words, height, width, words):
    amounts = []
    for word in all_words:
        if word['text'][0] == '0' and word['text'].isdigit():
            continue
        try:
            formatted_word = re.sub(r'[$,]', '', word['text'])
            if not any(char.isdigit() for char in formatted_word):
                continue
            if '-' in word['text']:
                continue
            if re.search('[a-zA-Z]', word['text']):
                continue
            if '/' in word['text']:
                continue
            if len(word['text']) > 15:
                continue
            if word['text'].isdigit() and len(word['text']) > 4:
                continue
            if '(' in word['text']:
                continue
            if len(word['text'].split('.')) == 3:
                if len(word['text'].split('.')[2]) == 4:
                    continue

            cad = {
                'text': word['text'],
                'x1': word['left'],
                'y1': word['top'],
                'x2': word['left'] + word['width'],
                'y2': word['top'] + word['height']
            }
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.4),
                                                  int(height * 0.02), width,
                                                  height)

            if not neighbours:
                amounts.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })

            neighbours_text = [it['text'].lower() for it in neighbours]

            if (
                    'total' in neighbours_text and 'days.' not in neighbours_text) or (
                    'amount' in neighbours_text and 'total' in neighbours_text) or (
                    'total:' in neighbours_text):
                amounts.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })

        except ValueError:
            continue

    return amounts


def get_tax(all_words, height, width, words):
    amounts = []
    for word in all_words:
        if word['text'][0] == '0' and word['text'].isdigit():
            continue
        try:
            formatted_word = re.sub(r'[$,]', '', word['text'])
            if not any(char.isdigit() for char in formatted_word):
                continue
            if '-' in word['text']:
                continue
            if re.search('[a-zA-Z]', word['text']):
                continue
            if '/' in word['text']:
                continue
            if len(word['text']) > 15:
                continue
            if word['text'].isdigit() and len(word['text']) > 4:
                continue
            if '(' in word['text']:
                continue
            if '%' in word['text']:
                continue
            if len(word['text'].split('.')) == 3:
                if len(word['text'].split('.')[2]) == 4:
                    continue

            cad = {
                'text': word['text'],
                'x1': word['left'],
                'y1': word['top'],
                'x2': word['left'] + word['width'],
                'y2': word['top'] + word['height']
            }
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.5),
                                                  int(height * 0.02), width,
                                                  height)

            neighbours_text = [it['text'].lower() for it in neighbours]

            if 'tax' in neighbours_text:
                amounts.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })

        except ValueError:
            continue

    return amounts


def get_pt(all_words, height, width, words):
    pt = []
    for word in all_words:
        if word['text'].isdigit():
            if 0 < int(word['text']) < 33:
                cad = {
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                }
                neighbours = Neighbour.find_neighbour(cad, words,
                                                      int(width * 0.3),
                                                      int(height * 0.02), width,
                                                      height)
                neighbours_text = [it['text'].lower().replace('.', '') for it in neighbours]

                if 'net' in neighbours_text or 'terms' in neighbours_text or ('due' in neighbours_text and 'days' in neighbours_text):
                    pt.append({
                        'text': word['text'],
                        'x1': word['left'],
                        'y1': word['top'],
                        'x2': word['left'] + word['width'],
                        'y2': word['top'] + word['height']
                    })
    return pt


def get_subtotal(all_words, height, width, words):
    amounts = []
    for word in all_words:
        if word['text'][0] == '0' and word['text'].isdigit():
            continue
        try:
            formatted_word = re.sub(r'[$,]', '', word['text'])
            if not any(char.isdigit() for char in formatted_word):
                continue
            if '-' in word['text']:
                continue
            if re.search('[a-zA-Z]', word['text']):
                continue
            if '/' in word['text']:
                continue
            if len(word['text']) > 15:
                continue
            if word['text'].isdigit() and len(word['text']) > 4:
                continue
            if '(' in word['text']:
                continue
            if '%' in word['text']:
                continue
            if len(word['text'].split('.')) == 3:
                if len(word['text'].split('.')[2]) == 4:
                    continue

            cad = {
                'text': word['text'],
                'x1': word['left'],
                'y1': word['top'],
                'x2': word['left'] + word['width'],
                'y2': word['top'] + word['height']
            }
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.5),
                                                  int(height * 0.01), width,
                                                  height)

            neighbours_text = [it['text'].lower() for it in neighbours]

            if 'subtotal' in neighbours_text:
                amounts.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })

        except ValueError:
            continue

    return amounts


def get_bill_to(lines, height, width, words):
    bill_to = []
    regexp = ".+ [0-9]{1,4} .+ [A-Z]{2} [0-9]{5}"
    coord_left = []
    for l in lines:
        coord_left.append(l['bbox'][0])

    dups = defaultdict(list)
    for i, e in enumerate(coord_left):
        dups[e].append(i)

    index_list = []
    x1_list = []
    y1_list = []
    x2_list = []
    y2_list = []
    key_list = []
    for key in sorted(dups):
        if not index_list:
            key_list.append(key)
            index_list.append(dups[key])
            index_list = flatten_list(index_list)
            for item in index_list:
                x1_list.append(lines[item]['bbox'][0])
                y1_list.append(lines[item]['bbox'][1])
                x2_list.append(lines[item]['bbox'][2])
                y2_list.append(lines[item]['bbox'][3])
        else:
            if key - key_list[-1] == 1:
                key_list.append(key)
                index_list.append(dups[key])
                index_list = flatten_list(index_list)
                index_list = sorted(index_list)
                pop_ind = []
                rem_list = []
                for ind in range(1, len(index_list)):
                    delta_y1 = (lines[index_list[ind]]['bbox'][1] - \
                                lines[index_list[ind - 1]]['bbox'][1]) / height
                    if delta_y1 < 0.021:
                        pop_ind.append(index_list[ind - 1])
                        pop_ind.append(index_list[ind])
                        pop_ind = list(set(pop_ind))
                        text_0 = ' '.join([lines[i]['text'] for i in pop_ind])
                        text_0 = re.sub(' +', ' ', text_0)
                        x1_list.append(lines[index_list[ind - 1]]['bbox'][0])
                        y1_list.append(lines[index_list[ind - 1]]['bbox'][1])
                        x2_list.append(lines[index_list[ind - 1]]['bbox'][2])
                        y2_list.append(lines[index_list[ind - 1]]['bbox'][3])
                        bb_coord_0 = [min(x1_list), min(y1_list), max(x2_list),
                                      max(y2_list)]
                        if re.findall(regexp, text_0):
                            cad = {
                                'text': text_0,
                                'x1': bb_coord_0[0],
                                'y1': bb_coord_0[1],
                                'x2': bb_coord_0[2],
                                'y2': bb_coord_0[3]
                            }
                            neighbours = Neighbour.find_neighbour(cad, words,
                                                                  int(
                                                                      width * 0.2),
                                                                  int(
                                                                      height * 0.01),
                                                                  width,
                                                                  height)

                            neighbours_text = [it['text'].lower() for it in
                                               neighbours]

                            if 'bill' in neighbours_text or 'address' in neighbours_text:
                                bill_to.append(
                                    cad
                                )
                    else:
                        txt = lines[index_list[ind - 1]]['text']
                        x1 = [lines[index_list[ind - 1]]['bbox'][0]]
                        y1 = [lines[index_list[ind - 1]]['bbox'][1]]
                        x2 = [lines[index_list[ind - 1]]['bbox'][2]]
                        y2 = [lines[index_list[ind - 1]]['bbox'][3]]
                        bb_coord = [min(x1), min(y1), max(x2), max(y2)]
                        rem_list.append(index_list[ind - 1])
                        if re.findall(regexp, txt):
                            cad = {
                                'text': txt,
                                'x1': bb_coord[0],
                                'y1': bb_coord[1],
                                'x2': bb_coord[2],
                                'y2': bb_coord[3]
                            }
                            neighbours = Neighbour.find_neighbour(cad, words,
                                                                  int(
                                                                      width * 0.2),
                                                                  int(
                                                                      height * 0.01),
                                                                  width,
                                                                  height)

                            neighbours_text = [it['text'].lower() for it in
                                               neighbours]


                            if 'bill' in neighbours_text or 'address' in neighbours_text:
                                bill_to.append(
                                    cad
                                )

                txt = lines[index_list[-1]]['text']
                x1 = [lines[index_list[-1]]['bbox'][0]]
                y1 = [lines[index_list[-1]]['bbox'][1]]
                x2 = [lines[index_list[-1]]['bbox'][2]]
                y2 = [lines[index_list[-1]]['bbox'][3]]
                bb_coord = [min(x1), min(y1), max(x2), max(y2)]
                if re.findall(regexp, txt):
                    rem_list.append(index_list[-1])
                    cad = {
                        'text': txt,
                        'x1': bb_coord[0],
                        'y1': bb_coord[1],
                        'x2': bb_coord[2],
                        'y2': bb_coord[3]
                    }
                    neighbours = Neighbour.find_neighbour(cad, words,
                                                          int(
                                                              width * 0.2),
                                                          int(
                                                              height * 0.01),
                                                          width,
                                                          height)

                    neighbours_text = [it['text'].lower() for it in
                                       neighbours]

                    if 'bill' in neighbours_text or 'address' in neighbours_text:
                        bill_to.append(
                            cad
                        )
                for ind in rem_list:
                    index_list.remove(ind)
            else:
                if len(index_list) == 1:
                    index_list = flatten_list(index_list)
                text = ' '.join([lines[i]['text'] for i in index_list])
                text = re.sub(' +', ' ', text)
                coord = [min(x1_list), min(y1_list), max(x2_list),
                         max(y2_list)]
                if re.findall(regexp, text):
                    cad = {
                        'text': text,
                        'x1': coord[0],
                        'y1': coord[1],
                        'x2': coord[2],
                        'y2': coord[3]
                    }
                    neighbours = Neighbour.find_neighbour(cad, words,
                                                          int(
                                                              width * 0.2),
                                                          int(
                                                              height * 0.01),
                                                          width,
                                                          height)

                    neighbours_text = [it['text'].lower() for it in
                                       neighbours]


                    if 'bill' in neighbours_text or 'address' in neighbours_text:
                        bill_to.append(
                            cad
                        )
                key_list = [key]
                index_list = [dups[key]]
                for item in dups[key]:
                    x1_list = [lines[item]['bbox'][0]]
                    y1_list = [lines[item]['bbox'][1]]
                    x2_list = [lines[item]['bbox'][2]]
                    y2_list = [lines[item]['bbox'][3]]

    return bill_to


def get_ship_to(lines, height, width, words):
    ship_to = []
    regexp = ".+ [0-9]{1,4} .+ [A-Z]{2} [0-9]{5}"
    coord_left = []
    for l in lines:
        coord_left.append(l['bbox'][0])

    dups = defaultdict(list)
    for i, e in enumerate(coord_left):
        dups[e].append(i)

    index_list = []
    x1_list = []
    y1_list = []
    x2_list = []
    y2_list = []
    key_list = []
    for key in sorted(dups):
        if not index_list:
            key_list.append(key)
            index_list.append(dups[key])
            index_list = flatten_list(index_list)
            for item in index_list:
                x1_list.append(lines[item]['bbox'][0])
                y1_list.append(lines[item]['bbox'][1])
                x2_list.append(lines[item]['bbox'][2])
                y2_list.append(lines[item]['bbox'][3])
        else:
            if key - key_list[-1] == 1:
                key_list.append(key)
                index_list.append(dups[key])
                index_list = flatten_list(index_list)
                index_list = sorted(index_list)
                pop_ind = []
                rem_list = []
                for ind in range(1, len(index_list)):
                    delta_y1 = (lines[index_list[ind]]['bbox'][1] - \
                               lines[index_list[ind - 1]]['bbox'][1])/height
                    if delta_y1 < 0.021:
                        pop_ind.append(index_list[ind - 1])
                        pop_ind.append(index_list[ind])
                        pop_ind = list(set(pop_ind))
                        text_0 = ' '.join([lines[i]['text'] for i in pop_ind])
                        text_0 = re.sub(' +', ' ', text_0)
                        x1_list.append(lines[index_list[ind - 1]]['bbox'][0])
                        y1_list.append(lines[index_list[ind - 1]]['bbox'][1])
                        x2_list.append(lines[index_list[ind - 1]]['bbox'][2])
                        y2_list.append(lines[index_list[ind - 1]]['bbox'][3])
                        bb_coord_0 = [min(x1_list), min(y1_list), max(x2_list),
                                      max(y2_list)]
                        if re.findall(regexp, text_0):
                            cad = {
                                'text': text_0,
                                'x1': bb_coord_0[0],
                                'y1': bb_coord_0[1],
                                'x2': bb_coord_0[2],
                                'y2': bb_coord_0[3]
                            }
                            neighbours = Neighbour.find_neighbour(cad, words,
                                                                  int(
                                                                      width * 0.2),
                                                                  int(
                                                                      height * 0.01),
                                                                  width,
                                                                  height)

                            neighbours_text = [it['text'].lower() for it in
                                               neighbours]

                            if 'ship' in neighbours_text and 'bill' not in neighbours_text:
                                ship_to.append(
                                    cad
                                )
                    else:
                        txt = lines[index_list[ind - 1]]['text']
                        x1 = [lines[index_list[ind - 1]]['bbox'][0]]
                        y1 = [lines[index_list[ind - 1]]['bbox'][1]]
                        x2 = [lines[index_list[ind - 1]]['bbox'][2]]
                        y2 = [lines[index_list[ind - 1]]['bbox'][3]]
                        bb_coord = [min(x1), min(y1), max(x2), max(y2)]
                        rem_list.append(index_list[ind - 1])
                        if re.findall(regexp, txt):
                            cad = {
                                'text': txt,
                                'x1': bb_coord[0],
                                'y1': bb_coord[1],
                                'x2': bb_coord[2],
                                'y2': bb_coord[3]
                            }
                            neighbours = Neighbour.find_neighbour(cad, words,
                                                                  int(
                                                                      width * 0.2),
                                                                  int(
                                                                      height * 0.01),
                                                                  width,
                                                                  height)

                            neighbours_text = [it['text'].lower() for it in
                                               neighbours]


                            if 'ship' in neighbours_text and 'bill' not in neighbours_text:
                                ship_to.append(
                                    cad
                                )

                txt = lines[index_list[-1]]['text']
                x1 = [lines[index_list[-1]]['bbox'][0]]
                y1 = [lines[index_list[-1]]['bbox'][1]]
                x2 = [lines[index_list[-1]]['bbox'][2]]
                y2 = [lines[index_list[-1]]['bbox'][3]]
                bb_coord = [min(x1), min(y1), max(x2), max(y2)]
                if re.findall(regexp, txt):
                    rem_list.append(index_list[-1])
                    cad = {
                        'text': txt,
                        'x1': bb_coord[0],
                        'y1': bb_coord[1],
                        'x2': bb_coord[2],
                        'y2': bb_coord[3]
                    }
                    neighbours = Neighbour.find_neighbour(cad, words,
                                                          int(
                                                              width * 0.2),
                                                          int(
                                                              height * 0.01),
                                                          width,
                                                          height)

                    neighbours_text = [it['text'].lower() for it in
                                       neighbours]

                    if 'ship' in neighbours_text and 'bill' not in neighbours_text:
                        ship_to.append(
                            cad
                        )
                for ind in rem_list:
                    index_list.remove(ind)
            else:
                if len(index_list) == 1:
                    index_list = flatten_list(index_list)
                text = ' '.join([lines[i]['text'] for i in index_list])
                text = re.sub(' +', ' ', text)
                coord = [min(x1_list), min(y1_list), max(x2_list),
                         max(y2_list)]
                if re.findall(regexp, text):
                    cad = {
                        'text': text,
                        'x1': coord[0],
                        'y1': coord[1],
                        'x2': coord[2],
                        'y2': coord[3]
                    }
                    neighbours = Neighbour.find_neighbour(cad, words,
                                                          int(
                                                              width * 0.2),
                                                          int(
                                                              height * 0.01),
                                                          width,
                                                          height)

                    neighbours_text = [it['text'].lower() for it in
                                       neighbours]

                    if 'ship' in neighbours_text and 'bill' not in neighbours_text:
                        ship_to.append(
                            cad
                        )
                key_list = [key]
                index_list = [dups[key]]
                for item in dups[key]:
                    x1_list = [lines[item]['bbox'][0]]
                    y1_list = [lines[item]['bbox'][1]]
                    x2_list = [lines[item]['bbox'][2]]
                    y2_list = [lines[item]['bbox'][3]]

    return ship_to


def get_candidates(data, height, width):
    all_lines = []
    max_line_num = max(data['line_num'])
    max_block_num = max(data['block_num'])
    for i in range(1, max_line_num + 1):
        for k in range(1, max_block_num + 1):
            text = ""
            coord_w = []
            coord_h = []
            coord_l = []
            coord_t = []
            for item in range(len(data['line_num'])):
                if data['line_num'][item] == i and data['block_num'][
                    item] == k:
                    text += data['text'][item] + " "
                    coord_w.append(data['width'][item])
                    coord_h.append(data['height'][item])
                    coord_l.append(data['left'][item])
                    coord_t.append(data['top'][item])
            x1 = min(coord_l[1:])
            y1 = min(coord_t[1:])
            x2 = min(coord_l[1:]) + sum(coord_w[1:]) + len(coord_w[1:]) * 7
            y2 = min(coord_t[1:]) + max(coord_h[1:])
            all_lines.append({"text": text, "bbox": [x1, y1, x2, y2]})
    all_words = []
    for idx, word in enumerate(data['text']):
        if word.strip() != "":
            all_words.append({
                'text': data['text'][idx],
                'left': data['left'][idx],
                'top': data['top'][idx],
                'width': data['width'][idx],
                'height': data['height'][idx]})
    text = ' '.join([word['text'].strip() for word in all_words])

    empty_index = [i for i, ele in enumerate(data['text']) if ele == ""]
    for key in data.keys():
        data[key] = [j for i, j in enumerate(data[key]) if i not in empty_index]

    words = []
    for txt, x, y, w, h in zip(data['text'], data['left'], data['top'], data['width'],
                               data['height']):
        x2 = x + w
        y2 = y + h

        words.append({'text': txt, 'x1': x, 'y1': y, 'x2': x2, 'y2': y2})

    try:
        invoice_date_candidates = get_dates(text, all_words, height, width, words)
    except Exception as e:
        print(e)
        print('invoice_date_candidates')
        invoice_date_candidates = []
    try:
        invoice_due_date_candidates = due_dates(text, all_words, height, width, words)
    except Exception as e:
        print(e)
        print('invoice_due_date_candidates')
        invoice_due_date_candidates = []
    try:
        total_amount_candidates = get_amounts(all_words, height, width, words)
    except Exception as e:
        print(e)
        print('total_amount_candidates')
        total_amount_candidates = []
    try:
        invoice_no_candidates = get_invoice_nums(all_words, height, width,
                                                 words)
    except Exception as e:
        print(e)
        print('invoice_no_candidates')
        invoice_no_candidates = []
    try:
        pt_candidates = get_pt(all_words, height, width, words)
    except Exception as e:
        print(e)
        print('pt_candidates')
        pt_candidates = []
    try:
        po_candidates = get_po(all_words, height, width, words)
    except Exception as e:
        print(e)
        print('po_candidates')
        po_candidates = []
    try:
        tax_candidates = get_tax(all_words, height, width, words)
    except Exception as e:
        print(e)
        print('tax_candidates')
        tax_candidates = []
    try:
        subtotal_candidates = get_subtotal(all_words, height, width, words)
    except Exception as e:
        print(e)
        print('subtotal_candidates')
        subtotal_candidates = []
    try:
        bill_to_candidates = get_bill_to(all_lines, height, width, words)
    except Exception as e:
        print(e)
        print('bill_to_candidates')
        bill_to_candidates = []
    try:
        ship_to_candidates = get_ship_to(all_lines, height, width, words)
    except Exception as e:
        print(e)
        print('ship_to_candidates')
        ship_to_candidates = []

    candidate_data = {
        'invoice_id': invoice_no_candidates,
        'invoice_date': invoice_date_candidates,
        'total_amount': total_amount_candidates,
        'due_date': invoice_due_date_candidates,
        'payment_terms': pt_candidates,
        'purchase_order': po_candidates,
        'total_tax_amount': tax_candidates,
        'net_amount': subtotal_candidates,
        'receiver_address': bill_to_candidates,
        'ship_to_address': ship_to_candidates,
    }

    return candidate_data
