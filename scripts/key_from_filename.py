import os

AUDIO_FILE_TYPES = {'.wav', '.mp3', 'flac', '.aiff'}


def key_from_filename(input_folder, output_folder):
    list_of_files = os.listdir(input_folder)
    for item in list_of_files:
        if any(soundfile_type in item for soundfile_type in AUDIO_FILE_TYPES):
            f = open(output_folder + '/' + item[:item.rfind(' - ')] + '.key', 'w')
            key = item[item.rfind(' - ') + 3:-4]
            if 'm' in key:
                f.write(key[:key.find('m')] + ' minor\n')
            else:
                f.write(key + ' major\n')
            f.close()
