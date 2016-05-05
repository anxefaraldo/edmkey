
my_file = open('/Users/angel/Desktop/estimations-other/rekordbox/rekordbox-e925.xml')
text = my_file.read()
str1 = 'Name="'
str2 = 'Tonality="'
str1len = len(str1)
str2len = len(str2)

while len(text) > 1:
    i = text.find(str1)
    text = text[i:]
    filename = text[str1len:text.find('Artist')]
    filename = filename[:filename.rfind(' - ')] + '.key'
    f = open('/Users/angel/Desktop/estimations-other/' + filename, 'w')
    i = text.find(str2)
    text = text[i:]
    key = text[str2len:text.find('" ')]
    if 'm' in key:
        key = key[:-1] + ' minor\t'
    else:
        key += ' major\t'
    print filename, key
    f.write(key)
    f.close()

