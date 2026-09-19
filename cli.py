import logging
import argparse
from wikisearch.pipeline import generate_video

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--term', type=str)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    term = args.term
    if term is None:
        term = input('Enter a term: ').strip()
        while not term:
            term = input('Please enter a term: ').strip()

    print(f'Generating video for {term}...')
    video = generate_video(term)
    if video is None:
        print('No video generated')
    else:
        print(f'Video generated: {video}')