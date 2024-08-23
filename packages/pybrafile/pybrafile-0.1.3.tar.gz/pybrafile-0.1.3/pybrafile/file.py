"""

    pybrafile -- Copyright (C) 2024 Brainstorming S.A.
    class to manage texte files
    
"""
import os
import platform
from pathlib import *
from enum import Enum

class TFfileType(Enum):
    TXT = 0
    BASE64 = 1

class TFileError(Enum):
    NONE = 0 #No error
    FOLDERNFOUND = 1 #Foleder not found
    FILENFOUND = 2 #File not fount
    SYSTEM = 3 #System error

class FileUtils:

    def __init__(self, afilename, adeffolder = ''):
        self._filename = afilename
        self._folder = adeffolder
        self._errorlevel = TFileError.NONE #fileerror.NONE  #1 = folder not exist, 2 = file not exist, 3 = System return from system
        self._iserror = False
        self._errortxt = ''
        self._fullpath = ''
        self._errortxt = ''
        platformInfo = platform.system()

        #Get exceution folder if deffolder is empty
        if self._folder == '':
            self._folder = os.getcwd() #Get path terminal when executing script
            #self._folder = os.path.realpath(os.path.dirname(__file__))
        
        if platformInfo == 'Windows':
            self._folder = PureWindowsPath(self._folder)
        else :
            self._folder = PurePath(self._folder)

        #Test if file and folder exist
        if not os.path.isdir(str(self._folder)):
            self._iserror = True
            self._errorlevel = TFileError.FOLDERNFOUND
            exit()
        
        if platformInfo == 'Windows':
            self._fullpath = PureWindowsPath(self._folder, self._filename)
        else :
            self._fullpath = PurePath(self._folder, self._filename)

        self._thefilename = Path(self._fullpath)
        if not os.path.isfile(str(self._thefilename)):
            self._iserror = True
            self._errorlevel = TFileError.FILENFOUND
        
    def createdir(self)->bool:
        """createdir create the folder

        Returns
        -------
        bool
            true if folder created
        """
        self._iserror = False
        try:
            nfolder = Path(str(self._folder))
            nfolder.parent.mkdir(parent=True, exist_ok=True)
        except OSError as e:
            self._iserror = True
            self._errorlevel = 3
            self._errortxt = str(e)
        finally:
            return not(self._iserror)
    
    def createfile(self, aencoding = 'utf-8')->bool:
        """createfile Create the file name

        Parameters
        ----------
        aencoding : str, optional
            file encoding format, by default 'utf-8'

        Returns
        -------
        bool
            True if file created
        """
        self._iserror = False
        try:
            self._file = self._thefilename.open(mode='w', encoding=aencoding)
            self._file.close()
        except OSError as e:
            self._iserror = True
            self._errorlevel = 3
            self._errortxt = str(e)
        finally:
            return not(self._iserror)

    def openfile(self, amode = 'r', aencoding = 'utf-8')->bool:
        """openfile openning the filename
        Parameters
        ----------
        amode : str, optional\n
            openning mode, by default 'r'\n
                r	Opens an existing file as text for reading only\n
                w	Opens a new file or overwrites an existing file as text for writing only\n
                a	Opens a new file or overwrites an existing file as text for writing where new text is added to the end of the file (i.e. append)\n
                r+	Opens an existing file as text for reading and writing\n
                w+	Opens a new file or overwrites an existing file as text for reading and writing\n
                a+	Opens a new file or overwrites an existing file as text for reading and writing where new text is added to the end of the file (i.e. append)\n
                rb	Opens an existing file as binary for reading only\n
                wb	Opens a new file of overwrites an existing file as binary for writing only\n
                ab	Opens a new file or overwrites an existing file as binary for writing where new text is added to the end of the file (i.e. append)\n
                rb+	Opens an existing file as binary for reading and writing\n
                wb+	Opens a new file or overwrites an existing file as binary for reading and writing\n
                ab+	Opens a new file or overwrites an existing file as binary for reading and writing where new binary is added to the end of the file (i.e. append)\n
        aencoding : _type_, optional
            file encoding value, by default 'utf-8'
                'ansi', 'ascii', 'utf-8', ..... si vide par defaut 'ansi'
        Returns
        -------
        bool
            true if open, flase is not open, the error in text is on error property
        """
        try:            
            self._iserror = True
            if (self._errorlevel != TFileError.NONE) and (self._errorlevel != TFileError.FILENFOUND):
                exit()
        
            self._file = self._thefilename.open(mode=amode, encoding=aencoding)
            self._iserror = False

        except IOError as e :
            self._errortxt = e
        except WindowsError as e :
            self._errortxt = str(e)
        finally:
            return not(self._iserror)
    
    def close(self):
        """close Close the file openned
        """
        self._file.close()

    def readfile(self) -> str:
        """readfile Read the file

        Returns
        -------
        str
            all the file in a string
        """
        return self._file.read()
    
    def readlns(self)->list[str]:
        """readln read all lines in the file

        Returns
        -------
        list[str]
            all line in a list of string
        """
        return self._file.readlines()
    
    def writeln(self, aline : str):
        """writeln Write a line in the file

        Parameters
        ----------
        aline : str
            The line to write (The char '\n' must be added in this param)
        """
        self._file.write(aline)
    
    #property function
    def _get_iserror(self)->bool:
        """__get_iserror test if issues during init component 

        Returns
        -------
        bool
            False = error and get the error for description, True non error 
        """
        return self._iserror
    
    def _get_errorcode(self)->int:
        """__get_errorcode return the error code

        Returns
        -------
        TFileError
            list of value : NONE=0, FOLDERNFOUND=1, FILENFOUND=2, SYSTEM=3
        """
        return self._errorlevel.value
    
    def _get_error(self)->str:
        """__get_error get the definition of error code

        Returns
        -------
        str
            the error in texte
        """
        if self._errorlevel == TFileError.FOLDERNFOUND:
            return 'The folder "' + str(self._folder) + '" not exist'
        elif self._errorlevel == TFileError.FILENFOUND:
            return 'The file "' + str(self._thefilename) + '" not exist'
        else:
            return self._errortxt
    
    def _get_filename(self)->str:
        """__get_filename the full file name with path

        Returns
        -------
        str
            The full file name
        """
        return str(self._thefilename)

    # Set property() to use get_name, set_name and del_name methods
    iserror = property(_get_iserror)
    errorcode = property(_get_errorcode)
    error   = property(_get_error)
    filename = property(_get_filename)