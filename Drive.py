'''
Drive.py is a single-class module. the Drive class
allows simple manipulation of files. Designed to work
with a single file locally which will be constantly
backed up on Google Drive.
'''

"""
    DEVELOPMENT NOTES :
    vnd in mimeTypes means "vendor-specific".
    These are probably the type of files that cannot be downloaded.

"""
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from typing import List,Dict,NoReturn,Any,Callable,Optional,Union

from customobjs import objdict

class Drive(object):
    ''' A simple, single-purpose-specific, wrapper
    for PyDrive.
    '''

    _query_kw = {
       "directory": ""
    }

    def __init__(
        self,
        path_to_creds: str = '.',
        secrets_file: str = 'client_secrets.json',
        credentials_file: str = 'mycreds.txt'
    ):
        ''' Initialize the drive object with a default credentials_file,
        which should be in the same directory as the script. A file can be
        specified providing the relative or absolute path.
        'client_secrets.json' MUST BE ON THE SAME DIRECTORY, OTHERWISE
        AN EXCEPTION WILL BE THROWN.
        '''

        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = os.path.join(path_to_creds, secrets_file)
        if secrets_file not in os.listdir(path_to_creds):
            raise Exception(f"{secrets_file} not found in {path_to_creds}")
        self.__gauth = GoogleAuth()
        try:
            self.__gauth.LoadCredentialsFile(os.path.join(path_to_creds, credentials_file))
        except Exception:
            pass
        if self.__gauth.credentials is None:
            # Platform-specific handling of missing credentials.
            if os.uname().sysname == 'Linux':
                self.__gauth.LocalWebserverAuth()
            elif (os.uname().sysname == 'Darwin' and 'iPhone' in os.uname().machine):
                import console
                console.alert('ERROR: Manual authentication needed.')
                self.__gauth.LocalWebserverAuth()
            else:
                raise Exception
        elif self.__gauth.access_token_expired:
            self.__gauth.Refresh()
        else:
            self.__gauth.Authorize()
        self.__gauth.SaveCredentialsFile(os.path.join(path_to_creds, credentials_file))
        self.__drive = GoogleDrive(self.__gauth)
    # END __init__

    def recursive_query(self, file_name: str):
        """
            Won't work if path begins with /
        parent = os.path.split(file_name)[0]
        if parent:
            recursive_query(parent)
        dirs = os.path.normpath(file_name).split(os.sep)

        idirs = iter(dirs)

        file_list = self.__drive.ListFile(_query).GetList()
        if next(idirs) in self.files:
        # Try thinking of a way to reduce the complexity of this !

        while True:
            current = next(idirs)

            _query = {"q": f""}
            next(idirs)
            in map(lambda x: x['title'], self.__query_drive()):
        """
        pass


    def ez_query(
        self,
        file_name: Optional[str] = None,
        directory: Optional[str] = None,
        include_trashed: bool = False
    ) -> List[Any]:
        """
           Construct a query and execute it

           parameters:
                file_name: The name of a file, or directory.

                directory: Can be many things...
                            1. The name of a directory located at root (/)
                            2. A directory id
                            3. root (default if not provided)
        """
        if directory in self.folders.keys():
            folder_id = self.folders[directory]
        elif directory:
            folder_id = directory
        else:
            folder_id = 'root'

        secondary = f"and title = '{file_name}'" if file_name else ""
        tertiary  = "and trashed=true" if include_trashed else "and trashed=false"

        _query = {
            'q': f"'{folder_id}' in parents {secondary} {tertiary}"
        }
        return self.__drive.ListFile(_query).GetList()
    ##


    @property
    def drive(self):
        return self.__drive

    def get_file_id(self, file_name: str = '') -> Union[str,bool]:
        '''
        ROOTFUNC : to be modified
        Get the file id of the desired file, if it exists.
        Return False upon failure i.e. file not specified, file doesn't
        exist, etc.
        '''
        if not file_name:
            return False
        file_list = self.__query_drive()
        names = [_file['title'] for _file in file_list]
        ids = [_file['id'] for _file in file_list]
        if file_name in names:
            return ids[names.index(file_name)]
        else:
            return False

    def get_file_by_name(self, file_name: str = ''):
        '''
        ROOTFUNC : to be modified
        Get a GoogleDriveFile instance corresponding to the
        specified file_name, if it exists.
        Return False upon failure i.e. file doesn't exist, etc.
        '''
        if not file_name:
            raise Exception('file_name parameter missing.')
        file_list = self.__query_drive()
        names = [_file['title'] for _file in file_list]
        if file_name in names:
            return file_list[names.index(file_name)]
        else:
            return False
    ##

    def upload_simple(
        self,
        source: str,
        title: str,
        id: Optional[str] = None,
        parent_id: Optional[str] = None,
        verbose: bool = True
    ) -> NoReturn:
        """
        """
        parent_id = parent_id or 'root'

        _file = self.drive.CreateFile({
            'title': title,
            'parents': [{
                "kind": "drive#parentReference",
                "id": parent_id,
                "isRoot": (lambda x: True if x == "root" else False)(parent_id)
            }]
        })
        if id:  _file.update({"id": id})
        try:
            if verbose: print(f"Uploading `{source}` as `{title}` ...", end="\t")
            _file.SetContentFile(source)
            _file.Upload()
            if verbose: print("Done")
        except Exception as e:
            print(f"\n\n ERROR: File `{source}` could not be uploaded.")
            print(f"Error details : {e}\n")
    ##

    def __upload_recursive(
        self,
        source: str,
        title: str,
        id: Optional[str] = None,
        parent_id: Optional[str] = None,
        verbose: bool = True
    ) -> NoReturn:
        """
            DO NOT USE YET !
            Like upload or update, but for a directory.
        file_list = self.__query_drive()
        titles = [_file['title'] for _file in file_list]
        if path:
            path_to_file = os.path.join(path, file_name)
        else:
            path_to_file = file_name
        if file_name in titles:
            _index = titles.index(file_name)
            _gdrive_file = file_list[_index]
        else:
            _gdrive_file = self.__drive.CreateFile({
                'title': file_name
            })
        try:
            _gdrive_file.SetContentFile(path_to_file)
            _gdrive_file.Upload()
            return True
        except (BaseException, FileNotFoundError):
            return False

        """

        if not os.path.exists(source):
            print(f"Error: '{source}' no such file or directory")
            exit()

        parent_id = parent_id or 'root'
        if os.path.isfile(source):
            # This block maybe should be a function.
            upload_simple(source, title, id=id, parent_id=parent_id)

        elif os.path.isdir(source):
            children = os.listdir(source)
            files = [ child for child in children if os.path.isfile(child) ]
            dirs  = [ child for child in children if os.path.isdir(child)  ]
        else:
            print("COULD NOT UPLOAD:")
            print(f" File `{source}` is neither a directory or regular file.")

    ##

    def download_directory(
        self,
        target: str,
        name: Optional[str] = None,
        id: Optional[str] = None,
        verbose: bool = True,
        safe: bool = True,
    ) -> NoReturn:
        """
        """
        if not name or id:
            raise Exception('Specify a directory name (if located at root), or id')

        _dir = id or name
        file_list = self.ez_query(directory=_dir)
        if safe: # Prevent trying to download files whose mimeType won't allow it.
            file_list = list(filter(
                lambda x: False if "vnd" in x["mimeType"] else x, file_list
            ))

        if not os.path.exists(target):
            try:
                if verbose: print(f"\nCreating target directory `{target}` ...", end="\t")
                os.makedirs(target)
                if verbose: print("Done")
            except Exception as e:
                print(f"Could not create target directory. Error details : {e}\n")
                exit()

        if verbose: print(f"\nFiles will be stored in `{target}`\n")
        for file in file_list:
            try:
                if verbose: print(f"Downloading `{file['title']}` ...", end="\t")
                file.GetContentFile(os.path.join(target, file['title']))
                if verbose: print("Done")
            except Exception as e:
                print(f"\n\n ERROR: File `{file['title']}` could not be downloaded.")
                print(f"Error details : {e}\n")
    ##

    def download_by_id(self, id: str, target: str) -> NoReturn:
        """
        """
        try:
            _file = self.drive.CreateFile({"id": id})
            _file.GetContentFile(target)
        except:
            print(f"Downloading file with id {id} to target {target} failed.")
    ##

    def download_file(self, file_name: str = '', target_name: str = ''):
        ''' Download file from drive.
        Query GoogleDrive for file_name.
        Save file to targe_name, if specified.
        target_name defaults to file_name (used to query).

        Returns:
            True, upon success
            False, upon failure
        '''
        if not file_name:
            raise Exception('file_name parameter missing.')
        else:
            _file = self.get_file_by_name(file_name)
        if not target_name:
            target_name = file_name

        if _file:
            _file.GetContentFile(target_name)
            return True
        else:
            return False

    def file_exists(self, some_file: str, query: str = '') -> bool:
        ''' Query Drive to verify the existence of a given file.
        The provided string 'some_file' should correpond EXACTLY
        to the name that appears on GoogleDrive.
        If no query is provided, the default _query will yield
        all files in the root folder.
        Useful links on query syntax:
            https://pythonhosted.org/PyDrive/filelist.html
            https://developers.google.com/drive/api/v2/search-parameters
        '''
        file_list = self.__query_drive(query)
        if some_file in [_file['title'] for _file in file_list]:
            return True
        else:
            return False

    def update(self, file_name: str, path: str = '') -> bool:
        ''' Update a file stored on Google Drive, using a
        local file. If the file does not exist on Google Drive,
        a new Google Drive file is created and its content is
        set to the specified local file's content.
        This method UPLOADS the file, with all of its content.
        Appending one line to a 7GiB file will result in the
        uploading of 7GiB + sizeof(one line).

        Returns:
                True    (successful uploading)
                False   (if any error occurs)
        '''
        file_list = self.__query_drive()
        titles = [_file['title'] for _file in file_list]
        if path:
            path_to_file = os.path.join(path, file_name)
        else:
            path_to_file = file_name
        if file_name in titles:
            _index = titles.index(file_name)
            _gdrive_file = file_list[_index]
        else:
            _gdrive_file = self.__drive.CreateFile({
                'title': file_name
            })
        try:
            _gdrive_file.SetContentFile(path_to_file)
            _gdrive_file.Upload()
            return True
        except (BaseException, FileNotFoundError):
            return False

    @property
    def files(self):
        """
            List of regular files found at the account's root '/', i.e.
            not inside any other folder.
            These are just names or 'titles' in Google Drive API's
            terminology, that can be used to download the file.
        """
        return [ entry['title'] for entry in self.__query_drive() ]

    @property
    def folders(self):
        """
            A dictionary containing all folders found at the account's root.
            The pairs are
            {
                title: id
            }
        """
        return {
            entry['title']: entry['id']
            for entry in self.__query_drive({
                'q': "'root' in parents and mimeType = 'application/vnd.google-apps.folder'"
            })
        }

    def __query_drive(self, query: Optional[Dict[str,str]] = None) -> list:
        ''' Helper method returning a list of files.
        A wrapper for the call:
            self.__drive.ListFile(_query).GetList()
        Default query:
            {'q': "'root' in parents and trashed=false"}
        '''
        _query = query or {'q': "'root' in parents and trashed=false"}
        file_list = self.__drive.ListFile(_query).GetList()
        return file_list
# END Drive
