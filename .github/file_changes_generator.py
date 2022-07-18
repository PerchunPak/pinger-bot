"""File for generating `FileChanges https://docs.github.com/en/graphql/reference/input-objects#filechanges`_ object.

Using this in CI for committing files with GitHub GraphQL API,
because when you commit with API there will be *verified* label.

.. note:: This will actually run ``git add .``, so consider **do not run** this, if you will not debug it.
"""
import base64
import dataclasses
import json
import os
import typing

import git


def _calculate_file_content(path: str) -> str:
    """Open file and encrypt it content with base64.

    Args:
        path: Path to file.

    Returns:
        Base64 encoded content of file.
    """
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode()


@dataclasses.dataclass
class FileAddition:
    """Represents `FileAddition https://docs.github.com/en/graphql/reference/input-objects#fileaddition`_ object."""

    path: str
    """Path to file."""
    contents: str
    """Base64 encoded content of file."""


@dataclasses.dataclass
class FileDeletion:
    """Represents `FileDeletion https://docs.github.com/en/graphql/reference/input-objects#filedeletion`_ object."""

    path: str
    """Path to file."""


@dataclasses.dataclass
class FileChanges:
    """Represents `FileChanges https://docs.github.com/en/graphql/reference/input-objects#filechanges`_ object."""

    additions: typing.List[FileAddition] = dataclasses.field(default_factory=list)
    """List of additions in future commit."""
    deletions: typing.List[FileDeletion] = dataclasses.field(default_factory=list)
    """List of deletions in future commit."""

    def merge(self, other: "FileChanges") -> "FileChanges":
        """Merge two :class:`.FileChanges` objects.

        Args:
            other: Other :class:`.FileChanges` object.

        Returns:
            New :class:`.FileChanges` object with changes from both previous objects.
        """
        return FileChanges(
            additions=self.additions + other.additions,
            deletions=self.deletions + other.deletions,
        )

    def __str__(self) -> str:
        """Build JSON string representation of :class:`.FileChanges` object.

        Returns:
            JSON string representation of :class:`.FileChanges` object.
        """
        return json.dumps(dataclasses.asdict(self))


@dataclasses.dataclass
class NewFile:
    """Represents new file in future commit."""

    path: str
    """Path to file."""

    def to_file_changes(self) -> FileChanges:
        """Convert :class:`.NewFile` object to :class:`.FileChanges` object.

        Returns:
            :class:`.FileChanges` object.
        """
        return FileChanges(
            additions=[FileAddition(path=self.path, contents=_calculate_file_content(self.path))],
        )


@dataclasses.dataclass
class ModifiedFile(NewFile):
    """Represents modified file in future commit.

    All logic the same as in :class:`.NewFile` class.
    """


@dataclasses.dataclass
class DeletedFile(FileDeletion):
    """Represents deleted file in future commit."""

    def to_file_changes(self) -> FileChanges:
        """Convert :class:`.DeletedFile` object to :class:`.FileChanges` object.

        Returns:
            :class:`.FileChanges` object.
        """
        return FileChanges(deletions=[FileDeletion(path=self.path)])


@dataclasses.dataclass
class RenamedFile:
    """Represents renamed file in future commit."""

    new_path: str
    old_path: str

    def to_file_changes(self) -> FileChanges:
        """Convert :class:`.RenamedFile` object to :class:`.FileChanges` object.

        Returns:
            :class:`.FileChanges` object.
        """
        return FileChanges(
            additions=[FileAddition(path=self.new_path, contents=_calculate_file_content(self.new_path))],
            deletions=[FileDeletion(path=self.old_path)],
        )


def _get_diff() -> git.diff.DiffIndex:
    """Getter for diff.

    Exist for easier mocking in tests.

    .. warn:: It will execute ``git add .`` before actually getting diff.

    Returns:
        Diff object.
    """
    repo = git.Repo(os.getcwd())
    repo.git.add(".")
    return repo.index.diff(None, staged=True)


def main() -> FileChanges:
    """Main function with all logic.

    Returns:
        Generated `FileChanges https://docs.github.com/en/graphql/reference/input-objects#filechanges`_ object.
    """
    diff = _get_diff()
    file_changes = FileChanges()
    for changed in diff:
        if changed.change_type == "A":
            file_changes = file_changes.merge(NewFile(path=changed.a_path).to_file_changes())
        elif changed.change_type == "D":
            file_changes = file_changes.merge(DeletedFile(path=changed.b_path).to_file_changes())
        elif changed.change_type == "R":
            file_changes = file_changes.merge(
                RenamedFile(new_path=changed.b_path, old_path=changed.a_path).to_file_changes()
            )
        elif changed.change_type == "M":
            file_changes = file_changes.merge(ModifiedFile(path=changed.b_path).to_file_changes())
        else:  # pragma: no cover
            # I don't really understand what is undocumented change types here.
            # Will implement it in the future, if I will find what is this.
            raise ValueError(f"Unknown change type: {changed.change_type}")

    return file_changes


if __name__ == "__main__":
    print(main())
