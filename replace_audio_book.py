import argparse
import os
import playlist
import book_package

def main():
    parser = argparse.ArgumentParser(description="Install new audio book")
    parser.add_argument("--zip-file", required=True, help="Path to the zip file containing audiobook data")
    parser.add_argument("--target-dir", required=True, help="Target directory to extract audiobook data to")
    parser.add_argument("--list-name", required=True, help="Filename of the existing playlist to update")
    
    args = parser.parse_args()

    print(f"Importing audio book from {args.zip_file}")
    
    package = book_package.AudioBookPackage(args.zip_file)
    audio_book_info = package.install(args.target_dir)
    audio_book_name = audio_book_info['audio_book_name']
    
    print(f"Audio book '{audio_book_name}' found")

    pl = playlist.PlayList.from_json(args.list_name)
    card_id = pl.card_id
    
    os.remove(args.list_name)
    
    print(f"Updating playlist '{args.list_name}'")

    absolute_dir = os.path.abspath(args.target_dir)
    playlist.create_new_playlist(absolute_dir, args.list_name, card_id, audio_book_name)

    print("all done!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e)