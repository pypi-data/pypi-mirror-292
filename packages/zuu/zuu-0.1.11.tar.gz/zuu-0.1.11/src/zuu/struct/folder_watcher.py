from contextlib import contextmanager
import os


class FolderWatcher:
    """
    A class for watching a folder and its subfolders for changes.

    This class allows you to watch a folder and its subfolders for changes to files.
    It provides a mechanism to detect when a file has been created, modified, or deleted.
    """

    def __init__(self, path: str, deep: bool = False, detailed: bool = False):
        self.path = path
        self.deep = deep
        self.detailed = detailed
        self.watched = {}
        self.changed = {}
        self.snapshot()

    def snapshot(self):
        """
        Snapshot the directory and its subdirectories to keep track of file changes.

        This method takes a snapshot of the directory and its subdirectories, storing
        information about each file's modification date, size, and whether it is a directory.
        It uses the `os.walk` function to recursively traverse the directory tree.

        Parameters:
            None

        Returns:
            None

        Raises:
            OSError: If an error occurs while accessing the file system.

        """
        self.watched = {}
        try:
            if self.deep:
                for root, dirs, files in os.walk(self.path):
                    for name in files + dirs:
                        full_path = os.path.join(root, name)
                        is_dir = os.path.isdir(full_path)
                        try:
                            stats = {
                                "mdate": os.path.getmtime(full_path),
                                "size": os.path.getsize(full_path),
                                "isdir": is_dir,
                            }
                            if self.detailed:
                                # Add detailed stats if required
                                pass
                            self.watched[full_path] = stats
                        except OSError:
                            continue
            else:
                for name in os.listdir(self.path):
                    full_path = os.path.join(self.path, name)
                    is_dir = os.path.isdir(full_path)
                    try:
                        stats = {
                            "mdate": os.path.getmtime(full_path),
                            "size": os.path.getsize(full_path),
                            "isdir": is_dir,
                        }
                        if self.detailed:
                            # Add detailed stats if required
                            pass
                        self.watched[full_path] = stats
                    except OSError:
                        continue

        except Exception as e:
            print(f"Failed to snapshot directory {self.path}: {str(e)}")

    def track_changes(self):
        """
        Tracks changes between the current state of the watched files and the previous state.

        This method clears the `changed` dictionary and creates a copy of the `watched` dictionary.
        It then takes a snapshot of the current state of the files being watched.

        For each file in the `old_watched` dictionary, it checks if the file still exists.
        If the file does not exist, it adds the file path to the `changed` dictionary with the value "deleted".
        If the file exists, it checks if the modification time or size of the file has changed compared to the previous state.
        If either the modification time or size has changed, it adds the file path to the `changed` dictionary with the value "modified".

        After checking all the files in `old_watched`, it finds the files that were created by comparing the set of files in `watched` with the set of files in `old_watched`.
        For each newly created file, it adds the file path to the `changed` dictionary with the value "created".

        This method does not return anything.
        """
        self.changed.clear()
        old_watched = self.watched.copy()

        self.snapshot()
        for k, v in old_watched.items():
            if not os.path.exists(k):
                self.changed[k] = "deleted"
            elif v and (
                os.path.getmtime(k) != v["mdate"] or os.path.getsize(k) != v["size"]
            ):
                self.changed[k] = "modified"

        newlycreated = set(self.watched) - set(old_watched)
        for k in newlycreated:
            self.changed[k] = "created"

    @contextmanager
    def watch(self):
        """
        A context manager that watches for changes and tracks them.
        """
        try:
            yield
        finally:
            self.track_changes()

    @property
    def created(self):
        """
        Returns the list of created files.
        """
        created = []
        for k, v in self.changed.items():
            if v == "created":
                created.append(k)
        return created

    @property
    def deleted(self):
        """
        Returns the list of deleted files.
        """
        deleted = []
        for k, v in self.changed.items():
            if v == "deleted":
                deleted.append(k)
        return deleted

    @property
    def modified(self):
        """
        Returns the list of modified files.
        """
        modified = []
        for k, v in self.changed.items():
            if v == "modified":
                modified.append(k)
        return modified
