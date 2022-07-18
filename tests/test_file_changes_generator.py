"""Tests for ``.github/file_changes_generator.py``."""
import base64
import json
import pathlib
import sys

import faker as faker_package
import pytest
import pytest_mock

sys.path.append(".github")
import file_changes_generator as fcg


def test_calculate_file_content(tmp_path: pathlib.Path, faker: faker_package.Faker) -> None:
    """Tests that ``_calculate_file_content`` function really return base64 encrypted file."""
    file_content = faker.paragraph()
    with (tmp_path / "file.txt").open("w") as file:
        file.write(file_content)

    assert fcg._calculate_file_content(str(tmp_path / "file.txt")) == base64.b64encode(file_content.encode()).decode()


def test_file_changes_merge(faker: faker_package.Faker) -> None:
    """Tests that ``FileChanges.merge`` function really merge two :class:`.FileChanges` objects."""
    list_1, list_2, list_3, list_4 = [faker.pylist() for _ in range(4)]
    assert fcg.FileChanges(additions=list_1, deletions=list_2).merge(
        fcg.FileChanges(additions=list_3, deletions=list_4)
    ) == fcg.FileChanges(additions=list_1 + list_3, deletions=list_2 + list_4)


def test_str_file_changes_returns_json() -> None:
    """Tests that ``str(FileChanges)`` returns JSON."""
    json.loads(str(fcg.FileChanges(additions=[], deletions=[])))


@pytest.mark.parametrize("cls", (fcg.NewFile("abc.txt"), fcg.DeletedFile("abc.txt"), fcg.RenamedFile("a.txt", "b.txt")))
def test_to_file_changes(cls: fcg.NewFile, faker: faker_package.Faker, mocker: pytest_mock.MockerFixture) -> None:
    """Tests that ``to_file_changes`` function really return :class:`.FileChanges` object."""
    mocker.patch("file_changes_generator._calculate_file_content", return_value=faker.text())
    assert isinstance(cls.to_file_changes(), fcg.FileChanges)


def test_main_return_file_changes(mocker: pytest_mock.MockerFixture) -> None:
    """Tests that ``main`` function really return :class:`.FileChanges` object."""
    repo = mocker.patch("git.Repo")
    repo.git = mocker.stub()
    repo.git.add = mocker.stub()
    repo.index = mocker.stub()
    mocker.patch.object(repo.index, "diff", return_value=[], create=True)

    assert isinstance(fcg.main(), fcg.FileChanges)


@pytest.mark.parametrize(
    "cls",
    (
        "file_changes_generator.NewFile",
        "file_changes_generator.DeletedFile",
        "file_changes_generator.RenamedFile",
        "file_changes_generator.ModifiedFile",
    ),
)
def test_main_modes(cls: str, mocker: pytest_mock.MockerFixture) -> None:
    """Tests that ``main`` function really return :class:`.FileChanges` object."""

    class DiffItem:
        change_type = {
            "file_changes_generator.NewFile": "A",
            "file_changes_generator.DeletedFile": "D",
            "file_changes_generator.RenamedFile": "R",
            "file_changes_generator.ModifiedFile": "M",
        }[cls]

        a_path = "a_path"
        b_path = "b_path"

    mocker.patch("file_changes_generator._get_diff", return_value=[DiffItem()])
    to_file_changes = mocker.patch(cls + ".to_file_changes")

    fcg.main()

    to_file_changes.assert_called_once_with()
