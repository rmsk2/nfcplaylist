import sys
import os
import playlist
from nfcplaylistconsts import *
import cli_tools


def make_playlist(playlist_dir, out_name, event_insert):
    playlist_name = input("Enter playlist name          : ")
    sys.stdout.write("Place playlist card on reader: ")
    sys.stdout.flush()

    card_id = cli_tools.wait_for_card(event_insert)
    print(f"Card id {card_id}")
    playlist.create_new_playlist(playlist_dir, out_name, card_id, playlist_name)
    print("\nNew playlist successfully created")


if __name__ == "__main__":
    os.system(CLEAR_COMMAND)
    
    if len(sys.argv) < 3:
        print("usage: create_list <dir to list> <new playlist file>")
        sys.exit(42)

    cli_tools.main(lambda x: make_playlist(sys.argv[1], sys.argv[2], x))

        