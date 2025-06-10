"""Tests for the GitignoreParser class."""

import pathlib
from unittest.mock import Mock

from codebase_examiner.core.gitignore_parser import GitignoreParser


class DescribeGitignoreParser:
    """Tests for the GitignoreParser class."""

    def it_should_be_instantiated_with_fs_gateway(self):
        mock_fs_gateway = Mock()

        parser = GitignoreParser(mock_fs_gateway)

        assert isinstance(parser, GitignoreParser)
        assert parser._fs_gateway == mock_fs_gateway

    def it_should_create_fs_gateway_if_none_provided(self):
        parser = GitignoreParser()

        assert isinstance(parser, GitignoreParser)
        assert parser._fs_gateway is not None

    def it_should_parse_gitignore_file(self, mocker):
        mock_fs_gateway = Mock()
        mock_fs_gateway.path_exists.return_value = True
        mock_fs_gateway.read_file.return_value = """
# Comment
*.py[cod]
__pycache__/
.env
!important.pyc
"""
        parser = GitignoreParser(mock_fs_gateway)
        directory = pathlib.Path("/test/dir")

        patterns = parser.parse_gitignore(directory)

        mock_fs_gateway.path_exists.assert_called_once_with(directory / ".gitignore")
        mock_fs_gateway.read_file.assert_called_once_with(directory / ".gitignore")
        assert patterns == ["*.py[cod]", "__pycache__/", ".env", "!important.pyc"]

    def it_should_return_empty_list_if_gitignore_not_found(self, mocker):
        mock_fs_gateway = Mock()
        mock_fs_gateway.path_exists.return_value = False
        parser = GitignoreParser(mock_fs_gateway)
        directory = pathlib.Path("/test/dir")

        patterns = parser.parse_gitignore(directory)

        mock_fs_gateway.path_exists.assert_called_once_with(directory / ".gitignore")
        mock_fs_gateway.read_file.assert_not_called()
        assert patterns == []

    def it_should_check_if_path_is_ignored(self, mocker):
        mock_fs_gateway = Mock()
        parser = GitignoreParser(mock_fs_gateway)
        path = pathlib.Path("/test/dir/file.py")
        base_dir = pathlib.Path("/test")

        # Set up a mock for path.relative_to to return a predictable result
        rel_path = pathlib.Path("dir/file.py")

        # Use mocker.patch to mock the relative_to method on any Path instance
        mocker.patch("pathlib.Path.relative_to", return_value=rel_path)

        # Test with no patterns
        assert not parser.is_path_ignored(path, [], base_dir, is_directory=False)

        # Test with non-matching pattern
        assert not parser.is_path_ignored(path, ["*.txt"], base_dir, is_directory=False)

        # Test with matching pattern
        assert parser.is_path_ignored(path, ["*.py"], base_dir, is_directory=False)

        # Test with negated pattern
        assert not parser.is_path_ignored(path, ["!*.py"], base_dir, is_directory=False)

        # Test with directory-specific pattern
        assert not parser.is_path_ignored(path, ["dir/"], base_dir, is_directory=False)

        # Test with root-level pattern
        assert parser.is_path_ignored(
            path, ["/dir/file.py"], base_dir, is_directory=False
        )

        # Test with pattern starting with **/
        assert parser.is_path_ignored(
            path, ["**/file.py"], base_dir, is_directory=False
        )

        # Test with pattern containing /
        assert parser.is_path_ignored(
            path, ["dir/file.py"], base_dir, is_directory=False
        )

    def it_should_handle_relative_paths_correctly(self, mocker):
        mock_fs_gateway = Mock()
        parser = GitignoreParser(mock_fs_gateway)
        path = pathlib.Path("/test/dir/subdir/file.py")
        base_dir = pathlib.Path("/test")

        # Set up a mock for path.relative_to to return a predictable result
        rel_path = pathlib.Path("dir/subdir/file.py")

        # Use mocker.patch to mock the relative_to method on any Path instance
        mocker.patch("pathlib.Path.relative_to", return_value=rel_path)

        # Test with pattern matching any part of the path
        assert parser.is_path_ignored(path, ["subdir"], base_dir, is_directory=False)

        # Test with pattern matching the full relative path
        assert parser.is_path_ignored(
            path, ["dir/subdir/file.py"], base_dir, is_directory=False
        )

        # Test with pattern not matching the full relative path
        assert not parser.is_path_ignored(
            path, ["other/file.py"], base_dir, is_directory=False
        )

    def it_should_handle_path_not_relative_to_base_dir(self, mocker):
        mock_fs_gateway = Mock()
        parser = GitignoreParser(mock_fs_gateway)
        path = pathlib.Path("/other/dir/file.py")
        base_dir = pathlib.Path("/test")

        # Use the rel_path_str parameter to simulate a path not relative to base_dir
        path_str = "/other/dir/file.py"

        # Test with pattern matching the full path
        assert parser.is_path_ignored(
            path, ["**/file.py"], base_dir, is_directory=False, rel_path_str=path_str
        )

        # Test with pattern not matching the full path
        assert not parser.is_path_ignored(
            path, ["test/**"], base_dir, is_directory=False, rel_path_str=path_str
        )
