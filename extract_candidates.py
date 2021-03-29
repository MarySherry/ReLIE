import re
from dateparser.search import search_dates


def get_invoice_nums(all_words):
    inv_nums = []
    invoice_no_re = r'^[0-9a-zA-Z-]+$'
    for word in all_words:
        if '-' in word['text']:
            continue
        if not re.search('\d', word['text']):
            continue
        if len(word['text']) < 2:
            continue
        result = re.findall(invoice_no_re,word['text'])
        if result:
            inv_nums.append({
                'text': word['text'],
                'x1': word['left'],
                'y1': word['top'],
                'x2': word['left'] + word['width'],
                'y2': word['top'] + word['height']
            })

    return inv_nums


def get_dates(all_text, all_words):
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

        token_length = len(text.split(' '))
        idx = all_text.find(match[0])
        text_len = len(text)
        index = len(all_text[:idx].strip().split(' '))
        if idx == 0:
            index = 0

        replaced_text = ' '.join(['*'*len(i) for i in text.split(' ')])

        indices.append(list(range(index, index + token_length)))

        index += token_length
        all_text = all_text[:idx + text_len].replace(text, replaced_text) + all_text[idx + text_len:]

    for date_indices in indices:
        date = ''
        left, top, right, bottom = [], [], [], []
        for i in date_indices:
            date += ' ' + all_words[i]['text']
            left.append(all_words[i]['left'])
            top.append(all_words[i]['top'])
            right.append(all_words[i]['left'] + all_words[i]['width'])
            bottom.append(all_words[i]['top'] + all_words[i]['height'])
        all_dates.append({
            'text': date.strip(),
            'x1': min(left),
            'y1': min(top),
            'x2': max(right),
            'y2': max(bottom)
        })

    return all_dates


def get_amounts(all_words):
    amounts = []
    amount_re = r"\$?([0-9]*,)*[0-9]{3,}(\.[0-9]+)?"
    for word in all_words:
        if word['text'][0]=='0':
            continue
        if "$" in word['text']:
            formatted_word = re.sub(r'[$,]', '', word['text'])
            if not any(char.isdigit() for char in formatted_word):
                continue

            amounts.append({
                'text': word['text'],
                'x1': word['left'],
                'y1': word['top'],
                'x2': word['left'] + word['width'],
                'y2': word['top'] + word['height']
            })
        if not re.search(amount_re, word['text']):
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
            if '(' in word['text']:
                continue
            if len(word['text'].split('.')) == 3:
                if len(word['text'].split('.')[2]) == 4:
                    continue
        
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


def get_pt(all_words):
    pt = []
    for word in all_words:
        if word['text'].isdigit():
            if 0 < int(word['text']) < 33:
                pt.append({
                    'text': word['text'],
                    'x1': word['left'],
                    'y1': word['top'],
                    'x2': word['left'] + word['width'],
                    'y2': word['top'] + word['height']
                })
    return pt


def get_candidates(data, height, width):
        # all_words = []
        # for idx, word in enumerate(data['text']):
        #     if word.strip() != "":
        #         all_words.append({
        #             'text': data['text'][idx],
        #             'left': data['left'][idx],
        #             'top': data['top'][idx],
        #             'width': data['width'][idx],
        #             'height': data['height'][idx]})
        # text = ' '.join([word['text'].strip() for word in all_words])

        BlockType_word = [item for item in data['Blocks'] if
                          item['BlockType'] == 'WORD']
        words = [item['Text'] for item in BlockType_word]
        all_words = []
        for item in BlockType_word:
            all_words.append({
                'text': item['Text'],
                'left': item['Geometry']['BoundingBox']['Left'] * width,
                'top': item['Geometry']['BoundingBox']['Top'] * height,
                'width': item['Geometry']['BoundingBox']['Width'] * width,
                'height': item['Geometry']['BoundingBox']['Height'] * height})
        text = ' '.join(words)

        try:
            invoice_date_candidates = get_dates(text,all_words)
        except Exception as e:
            print(e)
            invoice_date_candidates = []
        try:
            total_amount_candidates = get_amounts(all_words)
        except Exception as e:
            print(e)
            total_amount_candidates = []
        try:
            invoice_no_candidates = get_invoice_nums(all_words)
        except Exception as e:
            print(e)
            invoice_no_candidates = []
        try:
            pt_candidates = get_pt(all_words)
        except Exception as e:
            print(e)
            pt_candidates = []
        try:
            po_candidates = get_invoice_nums(all_words)
        except Exception as e:
            print(e)
            po_candidates = []
        try:
            tax_candidates = get_amounts(all_words)
        except Exception as e:
            print(e)
            tax_candidates = []


        candidate_data = {
            'invoice_no': invoice_no_candidates,
            'invoice_date': invoice_date_candidates,
            'total': total_amount_candidates,
            'due_date': invoice_date_candidates,
            'payment_terms': pt_candidates,
            'purchase_order': po_candidates,
            'total_tax_amount': tax_candidates,
        }

        return candidate_data
