from __future__ import annotations
import fnmatch
from pathlib import Path
import re
import zipfile

class ZipReplace:
    def __init__(self, archive:Path, pattern:str, find:str, replace:str) -> None:
            """EX: ZipReplace(Path("sample.zip"), "*.md", "xyzzy", "xyzzy")"""
            self.archive_path = archive
            self.pattern = pattern
            self.find = find
            self.replace = replace

    def find_and_replace(self) -> None:
          """Manager object"""
          input_path, output_path = self.make_backup() #renames the original zip to a backup version

          with zipfile.ZipFile(output_path, 'w') as output: #opens the new (empty) file for writing
                with zipfile.ZipFile(input_path) as input:  #opens the backup file for reading
                      self.copy_and_transform(input, output)

    def make_backup(self) -> tuple[Path, Path]:
          """Renames the old zip file so it's the untouched backup copy. 
          This backup copy is input to copy_and_transform(). The original name will be the final output.
           THe original file is renamed, and a new file is created that will have the original file's name """
          input_path = self.archive_path.with_suffix(f"{self.archive_path.suffix}.old") #renames original filepath to be sample.zip.old
          output_path = self.archive_path #names the to-be-written-to file with the original filename
          self.archive_path.rename(input_path) #renames the original file to the new backup name
          return input_path, output_path
    
    def copy_and_transform(self, input:zipfile.ZipFile, output:zipfile.ZipFile) -> None:
          """Builds the output file from the backup file. Examines each member, expands the compressed data, 
          transforms, compresses to write the output file, then cleans up the temporary file."""
          for item in input.infolist(): #iterates over every file or dir
                extracted = Path(input.extract(item)) #extracts the file's path and stores in temp location
                if (not item.is_dir() and fnmatch.fnmatch(item.filename, self.pattern)): #if not a directory and name matches wildcard pattern
                      print(f"Transform {item}")
                      input_text = extracted.read_text() #read
                      output_text = re.sub(self.find, self.replace, input_text) #find and replace
                      extracted.write_text(output_text) #writes the modified content back to the file
                else:
                      print(f"Ignore    {item}")

                output.write(extracted, item.filename) #adds the file to the new zip archive, preservint the original name
                extracted.unlink()  #unlink the temporary copy, which will cause the os to delete any unlinked files. 
                for parent in extracted.parents: #clean up any temp dirs created by the extraction process. 
                    if parent == Path.cwd():
                            break
                    parent.rmdir()

if __name__ == "__main__":
      sample_zip = Path("sample.zip")
      zr = ZipReplace(sample_zip, "*.md", "xyzzy", "plover's egg")
      zr.find_and_replace()




##############################################3
##############################################
################################################
#Refactored code for more modularity:
from abc import ABC, abstractmethod

class ZipProcessor(ABC):
    def __init__(self, archive:Path) -> None:
            self.archive_path = archive
            self._pattern:str

    def process_files(self, pattern:str) -> None:
        self._pattern = pattern
        input_path, output_path = self.make_backup()
        with zipfile.ZipFile(output_path, 'w') as output: 
            with zipfile.ZipFile(input_path) as input:  
                self.copy_and_transform(input, output)

    def _make_backup(self) -> tuple[Path, Path]:
        input_path = self.archive_path.with_suffix(f"{self.archive_path.suffix}.old")
        output_path = self.archive_path
        self.archive_path.rename(input_path)
        return input_path, output_path
    
    def _copy_and_transform(self, input:zipfile.ZipFile, output:zipfile.ZipFile) -> None:
        for item in input.infolist():
            extracted = Path(input.extract(item))
            if self.matches(item):
                print(f"Transform {item}")
                self.transform(extracted)
            else:
                print(f"Ignore    {item}")
            output.write(extracted, item.filename)
            self.remove_under_cwd(extracted)

    def _matches(self, item:zipfile.ZipInfo) -> bool:
        return (not item.is_dir() and fnmatch.fnmatch(item.filename, self._pattern))
    
    def _remove_under_cwd(self, extracted:Path) -> None:
        extracted.unlink()
        for parent in extracted.parents:
            if parent in extracted.parents:
                if parent == Path.cwd():
                    break
                parent.rmdir()

    @abstractmethod
    def transform(self, extracted:Path) -> None:
         ...


class TextTweaker(ZipProcessor):
    """EX: TextTweaker(zip_data).find_and_replace("xyzzy", "plover's egg").process_files("*.md")"""
    def __init__(self, archive:Path) -> None:
        super().__init__(archive)
        self.find: str
        self.replace: str

    def find_and_replace(self, find:str, replace:str) -> "TextTweaker":
        """updates the state of the object"""
        self.find = find
        self.replace = replace
        return self
    
    def _transform(self, extracted:Path) -> None:
        input_text = extracted.read_text()
        output_text = re.sub(self.find, self.replace, input_text)
        extracted.write_text(output_text)

from PIL import Image
class ImgTweaker(ZipProcessor):
    """EX: ImgTweaker(zip_data).process_files("*.jpg")"""
    def _transform(self, extracted:Path) -> None:
         image = Image.open(extracted)
         scaled = image.resize(size=(640, 960))
         scaled.save(extracted)

#######################################################
#######################################################
#######################################################
## Refactored to use composition instead of inheritance

from pathlib import Path
import zipfile
import fnmatch
import re
from abc import ABC, abstractmethod
from PIL import Image

# Define a transformer interface that declares a transform method.
class Transformer(ABC):
    @abstractmethod
    def transform(self, extracted: Path) -> None:
        pass

# Concrete transformer for text files.
class TextTransformer(Transformer):
    def __init__(self, find: str, replace: str) -> None:
        self.find = find
        self.replace = replace

    def _transform(self, extracted: Path) -> None:
        input_text = extracted.read_text()
        output_text = re.sub(self.find, self.replace, input_text)
        extracted.write_text(output_text)

# Concrete transformer for images.
class ImageTransformer(Transformer):
    def _transform(self, extracted: Path) -> None:
        image = Image.open(extracted)
        scaled = image.resize((640, 960))
        scaled.save(extracted)

# The ZipProcessor now uses composition: it receives a transformer
# to handle file-specific modifications.
class ZipProcessor:
    def __init__(self, archive: Path, transformer: Transformer, pattern: str) -> None:
        self.archive_path = archive
        self.transformer = transformer
        self.pattern = pattern

    def process_files(self) -> None:
        input_path, output_path = self.make_backup()
        with zipfile.ZipFile(output_path, 'w') as output_zip:
            with zipfile.ZipFile(input_path) as input_zip:
                self.copy_and_transform(input_zip, output_zip)

    def _make_backup(self) -> tuple[Path, Path]:
        backup_path = self.archive_path.with_suffix(f"{self.archive_path.suffix}.old")
        output_path = self.archive_path
        self.archive_path.rename(backup_path)
        return backup_path, output_path

    def _copy_and_transform(self, input_zip: zipfile.ZipFile, output_zip: zipfile.ZipFile) -> None:
        for item in input_zip.infolist():
            extracted = Path(input_zip.extract(item))
            if self.matches(item):
                print(f"Transform {item}")
                self.transformer.transform(extracted)
            else:
                print(f"Ignore    {item}")
            output_zip.write(extracted, item.filename)
            self.remove_under_cwd(extracted)

    def _matches(self, item: zipfile.ZipInfo) -> bool:
        return not item.is_dir() and fnmatch.fnmatch(item.filename, self.pattern)

    def _remove_under_cwd(self, extracted: Path) -> None:
        extracted.unlink()
        for parent in extracted.parents:
            if parent == Path.cwd():
                break
            try:
                parent.rmdir()
            except Exception:
                # Directory might not be empty or removable; just skip.
                pass

# Usage examples:
# For text files:
# transformer = TextTransformer("xyzzy", "plover's egg")
# processor = ZipProcessor(Path("archive.zip"), transformer, "*.md")
# processor.process_files()

# For images:
# transformer = ImageTransformer()
# processor = ZipProcessor(Path("archive.zip"), transformer, "*.png")
# processor.process_files()
