
my_file = open('/Users/angeluni/Insync/uni/publicaciones/improving_key/estimations-other/Rekordbox/rekordbox-e925.xml')
text = my_file.read()
str1 = 'Name="'
str2 = 'Tonality="'
str1len = len(str1)
str2len = len(str2)

while len(text) > 1:
    i = text.find(str1)
    text = text[i:]
    filename = text[str1len:text.find('" ')]
    filename = filename[:filename.find('"')] + '.key'
    # filename = text[str1len:text.find('"')] + '.key'
    f = open('/Users/angeluni/Insync/uni/publicaciones/improving_key/estimations-other/Rekordbox/rekordbox-edm925/' + filename, 'w')
    i = text.find(str2)
    text = text[i:]
    key = text[str2len:text.find('" ')]
    if 'm' in key:
        key = key[:-1] + ' minor'
    else:
        key += ' major'
    print filename, key
    f.write(key)
    f.close()
