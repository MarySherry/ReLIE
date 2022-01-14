from inference import evaluation
from pathlib import Path
import glob
import os
import json
import datetime
import dateparser
from functools import partial
from decimal import Decimal
from re import sub
from tqdm import tqdm
import pandas as pd
from sklearn.metrics import f1_score


def acc_field_detection(label, pred):
    field_detection = []
    for i in range(len(label)):
        if (pred[i] == 'nan' and label[i] != 'nan') or (pred[i] != 'nan' and label[i] == 'nan') or \
        (pred[i] == '' and label[i] != '') or (pred[i] != '' and label[i] == ''):
            field_detection.append(0)
        else:
            field_detection.append(1)
    print(field_detection)
    return sum(field_detection)/len(field_detection)


METRICS = {
    'f1': partial(f1_score, average='micro'),
    # 'accuracy': accuracy_score,
    # 'precision': partial(precision_score, average='micro'),
    # 'recall': partial(recall_score, average='micro'),
    # 'acc_field_detection': acc_field_detection
}


def id_conv(invoice_id):
    return invoice_id.strip()
    # if "#" in invoice_id:
    #     invoice_id = sub('#', '', invoice_id)
    #     return invoice_id.lstrip()
    # else:
    #     return invoice_id


def date_conv(d):
    return d
    # if d == 'nan' or d == '':
    #     return 'nan'
    # else:
    #     return dateparser.parse(d,settings={'PREFER_DAY_OF_MONTH': 'first', }).date().isoformat()


def pt_conv(pt_init):
    pt = str(pt_init).lower().split()
    if 'net' in pt:
        for item in pt:
            if item.isdigit():
                return item
    elif 'due' in pt:
        for item in pt:
            if item.isdigit():
                return item
            elif isinstance(dateparser.parse(item), datetime.date):
                return item
            else:
                return str(pt_init).lower()
    if 'within' in pt:
        for item in pt:
            if item.isdigit():
                return item
    else:
        return str(pt_init).lower()


def money_conv(m):
    if m and m != 'nan' and any(map(str.isdigit, m)):
        return "{:.2f}".format(Decimal(sub(r'[^\d.]', '', m)))
    else:
        return 'nan'


def calculate_metrics(
    predictions: str,
    dataset_path: str,
    fields_path: str,
):
    dataset = pd.read_json(dataset_path)

    with open(fields_path) as file:
        fields = json.load(file)

    #predictions = pd.read_csv(predictions_path)

    # Filling empty predictions with empty strings
    dataset = dataset.fillna('')
    predictions = predictions.fillna('')

    metrics = {}
    field_names = {field['name'] for field in fields['fields']}
    for field_name in field_names:
        if field_name not in predictions.columns:
            print(f'"{field_name}" is not present in predictions. Skipping!')
        else:
            merged_df = pd.merge(predictions[['filename', field_name]],
                                 dataset[['filename', field_name]],
                                 on='filename')
            for metric_name, metric_func in METRICS.items():
                # Compare fields as strings
                field_pred = merged_df[f'{field_name}_x'].apply(str)
                field_true = merged_df[f'{field_name}_y'].apply(str)
                if field_name == "invoice_id":
                    field_pred = field_pred.apply(id_conv)
                    field_true = field_true.apply(id_conv)
                if field_name == 'invoice_date' or field_name == 'due_date':
                    field_pred = field_pred.apply(date_conv)
                    field_true = field_true.apply(date_conv)
                    # print(field_pred, field_true)
                if field_name == 'total_tax_amount' or field_name == 'total_amount':
                    field_pred = field_pred.apply(money_conv)
                    field_true = field_true.apply(money_conv)
                    # print(field_pred, field_true)
                if field_name == 'payment_terms':
                    field_pred = field_pred.apply(pt_conv)
                    field_true = field_true.apply(pt_conv)
                metrics[f'{field_name}_{metric_name}'] = metric_func(field_true, field_pred)


    print(metrics)


if __name__ == '__main__':
    output = []
    folder = Path('data/images')
    files = glob.glob(os.path.join(folder,'*.png'))
    # out3 = pd.read_csv("out_lab.csv")
    # k = 0
    # for filepath in tqdm(files, total=len(files)):
    #     print(f'Processing file: {filepath}')
    #     result = evaluation(filepath, 'output/cached_data_val.pickle', 'output/model.pth')
    #     d = dict(out3.iloc[k])
    #     d.pop("filename", None)
    #     print(d)
    #     k += 1

    with open('test_labels.json') as file:
        fields = json.load(file)
    for item in fields[:47]:
        print(f'Processing file: {item["filename"]}')
        filepath = Path('data/images') / (item["filename"].split('.')[0] + ".png")
        result = evaluation(str(filepath), 'output/cached_data_val.pickle',
                            'output/model.pth')
        output.append({'filename': f'{item["filename"]}.pdf', **result})
        item.pop("filename", None)
        print(item)
        print(result)
    with open('test.json', 'w') as f:
        json.dump(output, f)
    # df = pd.DataFrame(output)
    # df.columns = ['filename', 'invoice_id', 'total_amount', 'due_date', 'purchase_order', 'total_tax_amount', 'invoice_date', 'payment_terms']
    # df.loc[0]['filename'] = '12.pdf'
    # df.loc[1]['filename'] = '3.pdf'
    # df.loc[8]['filename'] = '6.pdf'
    # df.loc[12]['filename'] = '2.PDF'
    # df.loc[17]['filename'] = '8.pdf'
    # df.loc[19]['filename'] = '11.pdf'
    # df.loc[20]['filename'] = '5.pdf'
    # df.loc[25]['filename'] = '4.pdf'
    # df.loc[28]['filename'] = '10.pdf'
    # df.loc[30]['filename'] = '9.PDF'
    # df.loc[31]['filename'] = '1.pdf'
    # df.loc[40]['filename'] = '7.pdf'
    # df.loc[38]['filename'] = '4_1.pdf'
    # df.loc[41]['filename'] = '5_1.pdf'
    # df.loc[42]['filename'] = '7_1.pdf'
    # df.loc[43]['filename'] = '6_1.pdf'
    # df.loc[45]['filename'] = '3_1.pdf'
    # df.to_csv("out_val.csv", index=False)
    # calculate_metrics(df, "dataset.json", "fields.json")

