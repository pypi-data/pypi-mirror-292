import argparse
import os
from .main import load_config, download_images_from_post

def main():
    parser = argparse.ArgumentParser(description='Download images from Reddit posts and comments.')
    parser.add_argument('post_url', help='URL of the Reddit post')
    parser.add_argument('--output', default='images.zip', help='Name of the output ZIP file (default: images.zip)')
    args = parser.parse_args()

    if not os.path.isfile('config.json'):
        print("Error: config.json file not found.")
        exit(1)

    config = load_config()
    download_images_from_post(args.post_url, args.output, config)

if __name__ == '__main__':
    main()
