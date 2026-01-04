# General overview

The main idea behind this software is to allow the user to control playback of tracks on a playlist via
NFC capable smartcards or other NFC capable devices like for instance security sticks or a plethora of tags in various
shapes and sizes. I.e. the user can start playback of a playlist by putting a corresponding smartcard  
(called a `playlist card`) on the reader and pausing playback by removing the card from the reader again. The playlist
which is played back depends on the identity of the smartcard which is placed on the reader. I.e. different playlist
cards cause different playlists to be played. In addition to that the user can control the following aspects via another
set of smartcards called `function cards`.

- Restart the selected playlist
- Restart the current track
- Go to the next track
- Go to the previous track
- End the program

For instance one would restart a playlist by first placing the `rewind function card` on the reader and removing it
again. The UI then shows a text that says that the playlist which is selected by the next `playlist card` is 
restarted. This command is executed as soon as the next `playlist card` is put on the RFID reader. Restarting a track
would be achieved by first placing the `restart function card` on the reader followed by the corresponding `playlist card`.

The whole purpose behind all this is to increase the accessibility of audio books for persons who are impaired in such ways
that make using the UI of modern computers difficult or impractical. This is (hopefully) achieved by transforming the task 
of using a piece of software via a mouse or touch controlled GUI into a series of simple manual interactions which require 
the user to place easy to handle physical objects (smartcards, tags, ...) at a certain location (the reader).

This software is written in Python and depends on [`pygame`](https://www.pygame.org/docs/) for implemeting the UI and 
`pyscard` for handling card access. [`pyscard`](https://github.com/LudovicRousseau/pyscard) in turn relies on the `pcscd` 
daemon which abstracts away access to smartcard readers on Linux and macOS. On Windows `PCSC` is part of the operating 
system. This software can use any card and reader combination which is supported by `pyscard`. I developed this software
under Linux and I have successfully installed it on an older MacBook. I see no principal reason why it should not work 
under Windows but I have not tested this, yet.

# Supported cards and readers

Cards are identified by this software primarily by their Answer To Reset or ATR, which is a sequence of bytes that is 
automatically sent by a smartcard as soon as it is powered on. Different types of cards have different ATRs but two cards 
of the same type have identical ATRs. You can use `id_gen.py`, which is part of this repo, to read the ATR of RFID capable 
smartcards you may have lying around. If you manage to find at least six different cards with different ATRs you can use them
to control the five functions mentioned above and one playlist. I have tested the following cards or RFID capable devices

- The German national ID card (ePA)
- The German health insurance card (eGK)
- Bank cards
- Credit cards
- Different company badges
- Yubikeys and other security sticks
- Fido tokens
- Company loyalty cards

## Using DESFire cards

Hunting for a usable set of cards or other RFID enabled devices seemed to be impractical in the long run, so another solution was 
needed. Different smartcard families allow to identify cards which are part of this family by a unique card serial number and offer
commands to read this serial number from the card. As I had some preexisting knowledge with respect to DESFire cards and as blank
DESFire cards are sold for instance on Amazon I decided to implement reading the serial number of DESFire cards as
an alternative to the ATR for identifying individual cards. 

It also seemed to be impractical to use the full seven byte serial number in the various config files and so the program
`id_gen.py` calculates and prints a simplified card id for each recognized type of card which is placed on the reader

```
Put a card on the reader to get its id
Press Enter to stop

DESFire card. Card id: 51918
Ntag215 card. Card id: 63840
Card type unknown. ATR 3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A
German national ID card. Card id: 0
```

or the full ATR for unknown cards. You might say that using a smartcard intended for security purposes in a scenario like this is 
totally overblown and you are right. But that is what seemed to work with my reader and the software stack immediately available to me. 

## Using simpler NFC tags

In a second step and after purchasing an additional reader (an ACS ACR122U) I also implemented reading serial numbers from ISO 14443 Type A
NFC tags like for instance various types of Mifare cards. Take a look at `uidfactory.py`, `nfcplaylistconsts.IUidReader`, `DESFireUidReader`
and `Ntag215UidReader` in order to get an idea of how to add more card types. I then discovered that the DESFire cards can also be 
treated as simple ISO 14443 Type A tags, but I left the DESFire specific code in place.

## Speaking of the ACS ACR122U

It is a versatile device which has read all RFID capable devices I have thrown at it. It worked out of the box on macOS. Unfortunately
`pyscard` support for this (CCID compliant) device on Linux, which is my preferred development platform, is rough. Even after installing
`libacsccid1`, which is part of the Universe repository on Ubuntu 24.04, manual intervention is required each time the reader is plugged
into a USB port or after each reboot. You have to manually unload the kernel module `pn533_usb` via the command `sudo modprobe -r pn533_usb`
(see [here](https://ludovicrousseau.blogspot.com/2013/11/linux-nfc-driver-conflicts-with-ccid.html) and 
[here](https://superuser.com/questions/1477349/acr122-nfc-reader-does-not-work-with-libnfc-ubuntu)) to make it work with `pyscard`. 
I know I could blacklist the module but I did not want to tweak my system too much.

Another annoying factor is the buzzer built into the device which beeps each time a card is recognized. You can use the program 
`acr122_buzzer_off.py` to switch off the buzzer manually but this is unfortunately not permanent. It has to be repeated each time the 
reader is powered on and so you will hear the buzzer at least once after each power up. People seemed to be so annoyed by this that
they have written blog posts on how to desolder the buzzer from the reader's PCB. This software turns the buzzer off automatically 
after the first card has been successfully read if an ACR122U is detected to be in use.

## A note about card ids

As `id_gen.py` simply calculates a hash over the serial number read from the card and uses the first two bytes of this
hash as an id (see method `uid_to_card_id()` of class `DESFireUidReader` in `desfire.py` or `Ntag215UidReader` in `ntag21x.py`) 
it is not that unlikely that two of your cards are assigned the same id. In that case you could use some other bytes from the hash, 
hash some additional data or use more hash bytes to make sure all of your cards end up having a different id. If you run into such
problems you could adapt the static method `determine_id()` of class `IUidReader` (defined in `nfcplaylistsconsts.py`) accorddingly.
`determine_id()` is called by `uid_to_card_id()` as implemented by `DESFireUidReader` and `Ntag215UidReader`.

# Running the software and configuration

You can run this software through the command `python3 nfcplaylist.py <config_dir>`. Maybe you have to replace `python3` by `python`
depending on your system. The config dir is optional. If it is mssing the current directory is used. When started the program
reads the file `ui_config` in the config dir and interprets any `.json` file in this directory as a playlist. When an error
reading a card is encountered the background of the UI flashes red once. An error reading a file is signalled by a single flashing
of the background in blue.

## Config of program

The overall config of this software is split between two files: `ui_config` and `nfcplaylistconsts.py`. In the JSON file `ui_config`
under `sounds` you can  configure the sounds which are played when for instance an error occurs or a card is successfully read
by referencing a corresponding file. Any file format supported by [`pygame`](https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound) 
can be used here. According to the documentation currently OGG and WAV are supported for this purpose. Please note that this limitation 
does not apply to the music files on the playlist. These can be [MP3 or OGG](https://www.pygame.org/docs/ref/music.html#pygame.mixer.music).

In the `ids` "section" you can configure which cards are used as `function cards` as specified by their id. As written above the
card ids of DESFire and other cards known to this software can de determined using `id_gen.py`. The ids of cards which are identified 
by their ATR only is determined by their position in the list `ALL_ATRS` contained in the module `nfcplaylistconsts.py`. You can
automate the assignment of function cards by using the tool `func_cards.py`.

The "section" `size` specifies the size of the UI in pixels as well as the font sizes used for displaying text. Finally the "key" 
`wait_reader_sec` determines how long the software waits for the reader to become ready. The messages displayed on the UI can
be customized in the file `nfcplaylistconsts.py` as can be the command which is used to clear the console after program start. Please
change the constant `CLEAR_COMMAND` to `cls` under Windows.

Via the entry `activate_close_button` (allowed values are `true` and `false`) you can control whether the program can be stopped
by clicking the window's close button. This is useful during development but not neccessarily when the program is used for the
intended purpose. In addition you can switch all text messages shown to german when setting the key `lang` to the value `"ger"`. If either
of the previously mentioned keys are missing then default values are used. The default is to deactivate the close button and to show
messages in english.

If the key `shutdown_command` is present its value will be used as a command to execute when `nfcplaylist` is stopped
(see [below](#other-considerations) for the reasons why this is desireable and useful).

If a key `msgs` is present its subvalues will be used to override the messages defined in `nfcplaylistconsts.py`. This can be used to
change some or even all of the messages which are presented to the user. Here an example of these two keys in action.

```
    "shutdown_command": "sudo shutdown -h now",
    "msgs": {
        "std_msg": "Hallo Bernd",
        "msg_shutdown": "Tschüss Bernd!"
    }
```

## Config of playlists

Any `.json` file in the config dir is interpreted as a playlist. playlists have to have the following structure.

```
{
    "play_list": "Test playlist",
    "file_name": "./test_play_list.json",
    "current_title": 0,
    "play_time": 0.0,
    "card_id": 28435,
    "data_dir": "/user/test/testdata",
    "titles": [
        "track1.mp3",
        "track2.mp3",
        "track3.mp3"
    ]
}

```

The "key" `play_list` can be used to set the name of the playlist. This will also occur in the title bar of the window in which the UI will
be displayed. `file_name` is set to the file name under which the playlist was read upon program start. It can be set to the empty string if 
you create a new playlist by hand. This information is used when a playlist needs to be updated on disk by the program. `current_title` holds the 
zero based index of the track which would be played and `play_time` is used to determine the offset in seconds into this file. This is used to restart 
playback on the same spot where it was stopped. For this to work 100% reliably, MP3 and OGG files should not be encoded with a variable bit rate. This is 
[a limitation](https://www.pygame.org/docs/ref/music.html#pygame.mixer.music.play) of `pygame`. If you are able or forced to encode the audio files
yourself, you can use `oggenc -m 160 -M 160 ...` to create 160 kBit non VBR OGG-Files. The value `card_id` determines the id of the
card which is used as the `playlist card` for this playlist. As described above these ids can be determined by `id_gen.py` for DESFire and
ISO 14443 Type A cards and by the position of the ATR in `ALL_ATRS` for all other cards. `data_dir` specifies the directory in which the actual sound
files are stored. The list `titles` specifies the names and positions of the individual tracks on this playlist, i.e. the sequence in this list
determines the sequence in which these tracks are played back.

## Audio book packages and their installation

There is some tooling to automate the installation of new audio books on the target system which is based on the notion of an audio book package.
Such a package is a ZIP file which contains the audio data in the ZIP's "root" directory and a single subdir called `info`. In this directory there
has to be a text file called `name.txt` which is intended to hold the title of the audio book.

You can use the programs `create_list.py` and `replace_audio_book.py` from this repo to create a new playlist or to replace the contents of an
existing playlist. Both programs accept the following parameters:

- `--zip-file` which has to reference the ZIP file containing the audio book package
- `--target-dir` which has to reference a directory into which the audio book package is to be extracted
- `--list-name` which has to specify the name of a new or an exisiting playlist file

Here an example which illustrates the usage of `create_list.py` and `replace_audio_book.py`:

```
python3 create_list.py --zip-file ../audio_book/example.zip --target-dir /home/user/audio_books/example/ --list-name example_new.json
python3 replace_audio_book.py --zip-file ../audio_book/example.zip --target-dir /home/user/audio_books/example/ --list-name example_existing.json
```

`create_list.py` lets the user select a corresponding playlist card by determining the id of a card which is placed on the reader, whereas 
`replace_audio_book.py` reads the corresponding card id from the existing playlist. Both programs read `name.txt` of the audio book package to set the
title of the playlist. They also perform the unzip operation. It is possible to extract the contents of a ZIP file several times into the same target
directory without any adverse effects.

# Installation on macOS

I installed `pcscd` and Python 3.12 via `brew` which both worked without a problem. Unfortunatley this has precluded me
from installing `pyscard` and `pygame` via `pip3` as global modules. The workaround is to install them in a Python virtual
environment and run this software also from the venv.

# Other considerations

This chapter mentions some other aspects which can be important when putting this software to use for its intended purpose of supporting impaired
persons. In my specific case I wanted to make sure that the user is never forced to interact with the operating system of the machine on which
this software runs. My ideal scenario was that the user simply opens a Laptop, the machine boots, the user is automatically logged in and the 
program is started automatically without additional intervention. On top of that the machine should never go into sleep mode and the whole setup 
should not be adversely affected if the user closes the laptop and reopens it. Finally shutting down the system should also be possible without
interacting with the operating system. 

I solved the last problem by allowing to run a command after nfcplaylist was stopped, for instance by placing the corresponding function card on
the reader or by clicking the close button of the main window. This command can be set by changing the value of `SHUTDOWN_COMMAND` in the module
`nfcplaylistconsts.py`. I use the software on macOS and I tweaked the system in such a way that the logged on user can utilize `sudo` without
entering a password. After that setting `SHUTDOWN_COMMAND` to `sudo shutdown -h now` did the trick. You can prevent the shutdown command from
being executed by creating a file called `maintenance` in the same directory where `ui_config` resides. When nfcplaylist detects the presence of this
file it not only skips the execution of the shutdown command but also deletes the file. This makes sure that deleting the `maintenance` file after
performing maintenance operations is not forgotten.

The other problems (auto logon after reboot, autostart of a program after logon, preventing sleep mode (even when lid is closed)) were also overcome
by configuring macOS correspondingly.

Another potential problem was created by the power management functions of some PC speakers which turn themselves off when no sound is played 
but fail to turn themselves back on again when playing back the audio book is resumed. I solved this problem by playing a "beep" sound each time 
a card was successfully read which not only provides feedback to the user that the card was read but also wakes up the speakers much more realiably
than playing back the contents of an audio book.