import re
from dateparser.search import search_dates
from collections import defaultdict

from utils import Neighbour


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

            neighbours_text_clean = [it['text'].lower().replace('#','').replace(':','') for it in neighbours]
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
                                                 int(height * 0.01), width, height)
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


def get_dates(all_lines, height, width, words):
    all_dates = []
    for line in all_lines:
        if search_dates(line['text']):
            text = search_dates(line['text'])[0][0]

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

            cad = {
                'text': line['text'],
                'x1': line['left'],
                'y1': line['top'],
                'x2': line['left'] + line['width'],
                'y2': line['top'] + line['height']
            }
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.3),
                                                  int(height * 0.01), width,
                                                  height)

            if not neighbours:
                all_dates.append({
                    'text': line['text'],
                    'x1': line['left'],
                    'y1': line['top'],
                    'x2': line['left'] + line['width'],
                    'y2': line['top'] + line['height']
                })

            neighbours_text = [it['text'].lower().replace(':','') for it in neighbours]

            if ('date' in neighbours_text or 'issued' in neighbours_text) and 'due' not in neighbours_text:
                all_dates.append({
                    'text': line['text'],
                    'x1': line['left'],
                    'y1': line['top'],
                    'x2': line['left'] + line['width'],
                    'y2': line['top'] + line['height']
                })
    return all_dates


def get_due_dates(all_lines, height, width, words):
    all_dates = []
    for line in all_lines:
        if search_dates(line['text']):
            text = search_dates(line['text'])[0][0]

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
            if 'Hour' in text:
                continue
            if 'hour' in text:
                continue
            if (len(text) > 10) and not (re.search('[a-zA-Z]', text)):
                continue
            if len(text) > 15:
                continue
            if text.isdigit():
                continue
            if '(' in text:
                continue

            cad = {
                'text': line['text'],
                'x1': line['left'],
                'y1': line['top'],
                'x2': line['left'] + line['width'],
                'y2': line['top'] + line['height']
            }
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.3),
                                                  int(height * 0.01), width,
                                                  height)

            neighbours_text = [it['text'].lower() for it in neighbours]

            if 'due' in neighbours_text:
                all_dates.append({
                    'text': line['text'],
                    'x1': line['left'],
                    'y1': line['top'],
                    'x2': line['left'] + line['width'],
                    'y2': line['top'] + line['height']
                })

    return all_dates


def get_amounts(all_words, height, width, words):
    amounts = []
    for word in all_words:
        if word['text'][0]=='0' and word['text'].isdigit():
            continue
        try:
            formatted_word = re.sub(r'[$,]','', word['text'])
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
            neighbours = Neighbour.find_neighbour(cad, words, int(width * 0.5),
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



            if ('total' in neighbours_text and 'days.' not in neighbours_text and 'subtotal' not in neighbours_text) or ('amount' in neighbours_text and 'total' in neighbours_text and 'subtotal' not in neighbours_text) or ('total:' in neighbours_text):
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
                                                  int(height * 0.01), width,
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


def get_bill_to(all_lines, height, width, words):
    bill_to = []
    regexp = ".+ [0-9]{1,4} .+ [A-Z]{2} [0-9]{5}"
    coord_left = []
    for i in range(len(all_lines)):
        if re.findall(regexp, all_lines[i]['Text']):
            cad = {
                'text': all_lines[i]['Text'],
                'x1': all_lines[i]['Geometry']['BoundingBox']['Left'] * width,
                'y1': all_lines[i]['Geometry']['BoundingBox']['Top'] * height,
                'x2': (all_lines[i]['Geometry']['BoundingBox']['Left'] + all_lines[i]['Geometry']['BoundingBox']['Width']) * width,
                'y2': (all_lines[i]['Geometry']['BoundingBox']['Top'] + all_lines[i]['Geometry']['BoundingBox']['Height']) * height
            }
            neighbours = Neighbour.find_neighbour(cad, words,
                                                  int(width * 0.2),
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

        coord_left.append(
            round(all_lines[i]['Geometry']['BoundingBox']['Left'], 2))

    dups = defaultdict(list)
    for i, e in enumerate(coord_left):
        dups[e].append(i)

    for item in dups:
        if len(dups[item]) > 1:
            index_list = [dups[item][0]]
            w_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Width']]
            h_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Height']]
            l_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Left']]
            t_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Top']]
            for j in range(1, len(dups[item])):
                if round(all_lines[dups[item][j]]['Geometry'][
                             'BoundingBox']['Top'], 2) - round(
                        all_lines[dups[item][j - 1]]['Geometry'][
                            'BoundingBox']['Top'], 2) <= 0.021:
                    index_list.append(dups[item][j])
                    w_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Width'])
                    h_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Height'])
                    l_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Left'])
                    t_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Top'])
                else:
                    text = ' '.join(
                        [all_lines[i]['Text'] for i in index_list])
                    coord = [max(w_list), sum(h_list), min(l_list),
                             min(t_list)]
                    index_list = [dups[item][j]]
                    w_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Width']]
                    h_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Height']]
                    l_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Left']]
                    t_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Top']]

                    if re.findall(regexp, text):

                        cad = {
                            'text': text,
                            'x1': coord[2]*width,
                            'y1': coord[3]*height,
                            'x2': (coord[2] + coord[0])*width,
                            'y2': (coord[3] + coord[1])*height
                        }
                        neighbours = Neighbour.find_neighbour(cad, words,
                                                              int(width * 0.2),
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

            text = ' '.join([all_lines[i]['Text'] for i in index_list])
            coord = [max(w_list), sum(h_list), min(l_list), min(t_list)]
            if re.findall(regexp, text):

                cad = {
                    'text': text,
                    'x1': coord[2]*width,
                    'y1': coord[3]*height,
                    'x2': (coord[2] + coord[0])*width,
                    'y2': (coord[3] + coord[1])*height
                }
                neighbours = Neighbour.find_neighbour(cad, words,
                                                      int(width * 0.2),
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
    return bill_to


def get_ship_to(all_lines, height, width, words):
    ship_to = []
    regexp = ".+ [0-9]{1,4} .+ [A-Z]{2} [0-9]{5}"
    coord_left = []
    for i in range(len(all_lines)):
        if re.findall(regexp, all_lines[i]['Text']):
            cad = {
                'text': all_lines[i]['Text'],
                'x1': all_lines[i]['Geometry']['BoundingBox']['Left'] * width,
                'y1': all_lines[i]['Geometry']['BoundingBox']['Top'] * height,
                'x2': (all_lines[i]['Geometry']['BoundingBox']['Left'] +
                       all_lines[i]['Geometry']['BoundingBox']['Width']) * width,
                'y2': (all_lines[i]['Geometry']['BoundingBox']['Top'] +
                       all_lines[i]['Geometry']['BoundingBox']['Height']) * height
            }
            neighbours = Neighbour.find_neighbour(cad, words,
                                                  int(width * 0.2),
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

        coord_left.append(
            round(all_lines[i]['Geometry']['BoundingBox']['Left'], 2))

    dups = defaultdict(list)
    for i, e in enumerate(coord_left):
        dups[e].append(i)

    for item in dups:
        if len(dups[item]) > 1:
            index_list = [dups[item][0]]
            w_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Width']]
            h_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Height']]
            l_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Left']]
            t_list = [all_lines[dups[item][0]]['Geometry']['BoundingBox'][
                          'Top']]
            for j in range(1, len(dups[item])):
                if round(all_lines[dups[item][j]]['Geometry'][
                             'BoundingBox']['Top'], 2) - round(
                        all_lines[dups[item][j - 1]]['Geometry'][
                            'BoundingBox']['Top'], 2) <= 0.021:
                    index_list.append(dups[item][j])
                    w_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Width'])
                    h_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Height'])
                    l_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Left'])
                    t_list.append(all_lines[dups[item][j]]['Geometry'][
                                      'BoundingBox']['Top'])
                else:
                    text = ' '.join(
                        [all_lines[i]['Text'] for i in index_list])
                    coord = [max(w_list), sum(h_list), min(l_list),
                             min(t_list)]
                    index_list = [dups[item][j]]
                    w_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Width']]
                    h_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Height']]
                    l_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Left']]
                    t_list = [all_lines[dups[item][j]]['Geometry'][
                                  'BoundingBox']['Top']]

                    if re.findall(regexp, text):
                        cad = {
                            'text': text,
                            'x1': coord[2]*width,
                            'y1': coord[3]*height,
                            'x2': (coord[2] + coord[0])*width,
                            'y2': (coord[3] + coord[1])*height
                        }
                        neighbours = Neighbour.find_neighbour(cad, words,
                                                              int(width * 0.2),
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

            text = ' '.join([all_lines[i]['Text'] for i in index_list])
            coord = [max(w_list), sum(h_list), min(l_list), min(t_list)]
            if re.findall(regexp, text):
                cad = {
                    'text': text,
                    'x1': coord[2]*width,
                    'y1': coord[3]*height,
                    'x2': (coord[2] + coord[0])*width,
                    'y2': (coord[3] + coord[1])*height
                }
                neighbours = Neighbour.find_neighbour(cad, words,
                                                      int(width * 0.2),
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
    return ship_to


def get_candidates(data, height, width):
        BlockType_word = [item for item in data['Blocks'] if
                          item['BlockType'] == 'WORD']
        all_words = []
        for item in BlockType_word:
            all_words.append({
                'text': item['Text'],
                'left': item['Geometry']['BoundingBox']['Left'] * width,
                'top': item['Geometry']['BoundingBox']['Top'] * height,
                'width': item['Geometry']['BoundingBox']['Width'] * width,
                'height': item['Geometry']['BoundingBox']['Height'] * height})

        BlockType_line = [item for item in data['Blocks'] if
                          item['BlockType'] == 'LINE']
        all_lines = []
        for item in BlockType_line:
            all_lines.append({
                'text': item['Text'],
                'left': item['Geometry']['BoundingBox']['Left'] * width,
                'top': item['Geometry']['BoundingBox']['Top'] * height,
                'width': item['Geometry']['BoundingBox']['Width'] * width,
                'height': item['Geometry']['BoundingBox']['Height'] * height})

        words = []
        for item in BlockType_word:
            words.append({
                'text': item['Text'],
                'x1': item['Geometry']['BoundingBox']['Left'] * width,
                'y1': item['Geometry']['BoundingBox']['Top'] * height,
                'x2': item['Geometry']['BoundingBox']['Left'] * width +
                      item['Geometry']['BoundingBox']['Width'] * width,
                'y2': item['Geometry']['BoundingBox'][
                          'Height'] * height + item['Geometry']['BoundingBox'][
                          'Top'] * height})

        try:
            invoice_date_candidates = get_dates(all_lines, height, width, words)
        except Exception as e:
            print(e)
            invoice_date_candidates = []
        try:
            invoice_due_date_candidates = get_due_dates(all_lines, height, width, words)
        except Exception as e:
            print(e)
            invoice_due_date_candidates = []
        try:
            total_amount_candidates = get_amounts(all_words, height, width, words)
        except Exception as e:
            print(e)
            total_amount_candidates = []
        try:
            invoice_no_candidates = get_invoice_nums(all_words, height, width, words)
        except Exception as e:
            print(e)
            invoice_no_candidates = []
        try:
            pt_candidates = get_pt(all_words, height, width, words)
        except Exception as e:
            print(e)
            pt_candidates = []
        try:
            po_candidates = get_po(all_words, height, width, words)
        except Exception as e:
            print(e)
            po_candidates = []
        try:
            tax_candidates = get_tax(all_words, height, width, words)
        except Exception as e:
            print(e)
            tax_candidates = []
        try:
            subtotal_candidates = get_subtotal(all_words, height, width, words)
        except Exception as e:
            print(e)
            subtotal_candidates = []
        try:
            bill_to_candidates = get_bill_to(BlockType_line, height, width, words)
        except Exception as e:
            print(e)
            bill_to_candidates = []
        try:
            ship_to_candidates = get_ship_to(BlockType_line, height, width, words)
        except Exception as e:
            print(e)
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
