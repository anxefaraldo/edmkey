# !/usr/local/bin/python
# -*- coding: UTF-8 -*-

from fileutils import *
import essentia.standard as estd


def essentia_key_extractor(soundfile, folder_to_write_results):
    """
    This function estimates the overall key of an audio track.
    :type soundfile: str
    :type folder_to_write_results: str
    """
    loader = estd.MonoLoader(filename=soundfile,
                             sampleRate=44100)
    key = estd.KeyExtractor(frameSize=4096,
                            hopSize=4096,
                            tuningFrequency=440)
    key, scale, strength = key(loader())
    result = key + ' ' + scale
    confidence = strength
    filename = soundfile[soundfile.rfind('/'):soundfile.rfind('.')]
    textfile = open(folder_to_write_results + filename + '.txt', 'w')
    # results_string = result + '\t' + '%.2f' % confidence
    # textfile.write(results_string)
    textfile.write(result)
    textfile.close()
    return result #, confidence


def essentia_key_extractor_batch(directory, folder_to_write_results):
    """
    Estimates the global key of all audio files in a folder
    :type directory: str
    :type folder_to_write_results: str
    """
    list_all_files = os.listdir(directory)
    for item in list_all_files:
        if any(soundfile_type in item for soundfile_type in {'.wav', '.mp3', 'flac', '.aiff'}):
            soundfile = directory + '/' + item
            # result, confidence = essentia_key_extractor(soundfile, folder_to_write_results)
            # print soundfile, '-', result, '(%.2f)' % confidence
            result = essentia_key_extractor(soundfile, folder_to_write_results)
            print soundfile, '-', result


if __name__ == "__main__":
    import sys
    try:
        os.path.isdir(sys.argv[1])
        estimations_folder = make_unique_dir(sys.argv[1], tag='essentia_extractor')
        essentia_key_extractor_batch(sys.argv[1], estimations_folder)
    except NameError:
        print sys.argv[1], 'is not a folder.'
        print 'usage:', sys.argv[0], '<folder_with_audio> <folder_to_write_estimations> <tag>\n'
        sys.exit()

