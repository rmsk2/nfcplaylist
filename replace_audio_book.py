import sys
import argparse
import os
import zipfile
import playlist


def main():
    parser = argparse.ArgumentParser(description="Update playlist from zip file")
    parser.add_argument("--zip-file", required=True, help="Path to the zip file containing audiobook data")
    parser.add_argument("--target-dir", required=True, help="Target directory to extract audibook data to")
    parser.add_argument("--list-name", required=True, help="Filename of the existing playlist to update")
    
    args = parser.parse_args()

    print(f"Importing audio book from {args.zip_file}")
    
    try:
        os.mkdir(args.target_dir)
    except FileExistsError:
        pass
    
    sys.stdout.write("Unzipping data ... ")
    sys.stdout.flush()

    with zipfile.ZipFile(args.zip_file, 'r') as zip_ref:
        zip_ref.extractall(args.target_dir)
    
    print("done")

    name_path = os.path.join(args.target_dir, "info", "name.txt")
    with open(name_path, "r", encoding="utf-8") as f:
        audio_book_name = f.read().strip()
    
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