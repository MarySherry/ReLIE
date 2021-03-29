from pytesseract import Output
import pytesseract
from glob import glob
import cv2
from tqdm import tqdm
import os
import json

import extract_candidates
from utils import config


def get_tesseract_results(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ocr_result = pytesseract.image_to_data(image, config='--oem 1 --psm 3', output_type=Output.DICT)
    return ocr_result


if __name__ == '__main__':

    dataset_dir = 'data'
    images_dir = os.path.join(dataset_dir, 'images')
    tesseract_results = os.path.join(dataset_dir, 'tesseract_results_lstm')

    assert os.path.exists(images_dir), "images directory doesn't exist"
    if not os.path.exists(tesseract_results):
        os.makedirs(tesseract_results)

    images = glob(os.path.join(images_dir, '*.png'))

    for image in tqdm(images, desc='Generating Tesseract Results'):
        image_name = os.path.splitext(os.path.split(image)[-1])[0]
        result = get_tesseract_results(image)
        candidate_data = extract_candidates.get_candidates(result)
        file_path = config.CANDIDATE_DIR / (
                    image.split('/')[-1].split('.')[0] + ".json")
        with open(file_path, 'w') as outfile:
            json.dump(candidate_data, outfile)
        with open(os.path.join(tesseract_results, image_name + '.json'), 'w') as f:
            json.dump(result, f)
