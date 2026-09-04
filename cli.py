import logging
from wikisearch.pipeline import generate_video

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    term = input('Enter a term: ').strip()
    while True:
        if not term:
            term = input('Please enter a term: ').strip()
            continue
        break

    print(f'Generating video for {term}...')
    video = generate_video(term)
    if video is None:
        print('No video generated')
    else:
        print(f'Video generated: {video}')