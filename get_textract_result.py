from glob import glob
from tqdm import tqdm
import os
import json
import cv2
import boto3

import extract_candidates
from utils import config


def get_textract_results(file, bucket):
    response = client.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': file
            }
        })
    return response


if __name__ == '__main__':

    dataset_dir = 'data'
    images_dir = os.path.join(dataset_dir, 'images')
    textract_results = os.path.join(dataset_dir, 'textract_results')

    #client = boto3.client('textract')

    if not os.path.exists(textract_results):
        os.makedirs(textract_results)

    bucket_name = 'invoice-parsing-ocr'
    filename = 'invoice-parsing/synthetic_data/images/'
    images = glob(os.path.join(images_dir, '*.png'))

    for image in tqdm(images, desc='Generating Textract Results'):
        image_name = os.path.splitext(os.path.split(image)[-1])[0]
        #result = get_textract_results(filename + image_name + ".jpg", bucket_name)
        imagesize = cv2.imread(str(image))
        height, width, _ = imagesize.shape
        with open(textract_results + "/" + image_name + ".json", 'r') as f:
            result = json.load(f)
        candidate_data = extract_candidates.get_candidates(result, height, width)
        file_path = config.CANDIDATE_DIR / (
                    image.split('/')[-1].split('.')[0] + ".json")
        with open(file_path, 'w') as outfile:
            json.dump(candidate_data, outfile)
        # with open(os.path.join(textract_results, image_name + '.json'), 'w') as f:
        #     json.dump(result, f)
