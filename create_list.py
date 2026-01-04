import sys
import os
import playlist
from nfcplaylistconsts import *
import cli_tools
import argparse
import book_package


def make_playlist(playlist_dir, out_name, zip_file, event_insert):
    print(f"Importing audio book from {args.zip_file}\n")

    audio_book = book_package.AudioBookPackage(zip_file)
    book_info = audio_book.install(playlist_dir)
    audio_book_name = book_info['audio_book_name']

    print(f"\nAudio book '{audio_book_name}' found\n")

    sys.stdout.write("Please put desired playlist card on reader ... ")
    sys.stdout.flush()
    card_id = cli_tools.wait_for_card(event_insert)
    print(f"Card id {card_id}")
    playlist.create_new_playlist(playlist_dir, out_name, card_id, audio_book_name)
    print("\nNew playlist successfully created")


if __name__ == "__main__":
    os.system(CLEAR_COMMAND)

    parser = argparse.ArgumentParser(description="Install new audio book")
    parser.add_argument("--zip-file", required=True, help="Path to the zip file containing audiobook data")
    parser.add_argument("--target-dir", required=True, help="Target directory to extract audiobook data to")
    parser.add_argument("--list-name", required=True, help="Filename of new playlist to create")
    
    args = parser.parse_args()

    absolute_dir = os.path.abspath(args.target_dir)
    cli_tools.main(lambda x: make_playlist(absolute_dir, args.list_name, args.zip_file, x))

        