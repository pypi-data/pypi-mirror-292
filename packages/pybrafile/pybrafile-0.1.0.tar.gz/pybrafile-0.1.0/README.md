# pybrafile Readme 📜
Brainstorming package to manage texte files

# Installation ⚡
Opérating system :  Windows, MacOS & Linux :

# Available function/class 📑
### to create => FileUtils(afilename, adeffolder)
    adeffolder : folder to read/write file. if not exist it will created (optionnal).
    afilename  : the file name to read/write
### to open file => openfile(self, amode = 'r', aencoding = 'utf-8')->bool:
    amode : mode to open file (a = append, w = overrite file, see doc for more) 
            by default r = read
    aencoding : encoding file by default utf-8
### to write line => writeln(aline)
    aline : a line to add in file. you need to add \n at the end to CRLF.
### to read all file to a string => readfile()
    read all file and return the file in a string.
### to read all line of file to a list => readlns()
    read all line of file and return a list of string.
### to close line => close()
    read all line of file and return a list of string.

# Howto use 📰
    import pybrafile

    file = pybrafile.FileUtils('testlog.txt')
    file.openfile('w')
    file.writeln('fist line\r')
    file.writeln('second line\r')
    file.close()

    file.openfile('r')
    txt = file.readfile()
    file.close()

    print(txt)
    print(pybrafile.version())

## Meta 💬
Brainstorming – Support.erp@brainstorming.eu

Distributed under the MIT license. See ``LICENSE`` for more information.