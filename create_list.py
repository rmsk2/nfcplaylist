import sys
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import playlist
from nfcplaylistconsts import *
import cli_tools


def gen_listing(src_path):
    only_files = [f for f in listdir(src_path) if isfile(join(src_path, f))]
    only_files.sort()

    return only_files


def create_new_playlist(dir_to_list, out_name, card_id, playlist_name):
    data_dir = Path(dir_to_list)    

    print("Generating directory listing ...")
    play_list = playlist.PlayList(card_id, out_name, gen_listing(data_dir))
    play_list.play_list = playlist_name
    play_list.data_dir = str(data_dir)

    play_list.save()   


def make_playlist(playlist_dir, out_name, event_insert):
    playlist_name = input("Enter playlist name          : ")
    sys.stdout.write("Place playlist card on reader: ")
    sys.stdout.flush()

    card_id = cli_tools.wait_for_card(event_insert)
    print(f"Card id {card_id}")
    create_new_playlist(playlist_dir, out_name, card_id, playlist_name)
    print("\nNew playlist successfully created")


if __name__ == "__main__":
    os.system(CLEAR_COMMAND)
    
    if len(sys.argv) < 3:
        print("usage: create_list <dir to list> <new playlist file>")
        sys.exit(42)

    cli_tools.main(lambda x: make_playlist(sys.argv[1], sys.argv[2], x))

        