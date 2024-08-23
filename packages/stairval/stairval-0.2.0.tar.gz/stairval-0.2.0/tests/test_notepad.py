import pytest

from stairval.notepad import Notepad, create_notepad


class TestNotepad:

    @pytest.fixture
    def notepad(self) -> Notepad:
        return create_notepad("badumtss")

    def test_add_subsection(
        self,
        notepad: Notepad,
    ):
        sub = notepad.add_subsection("subtss")

        assert sub.label == "subtss"
        assert sub.level == 1

    def test_add_subsections(
        self,
        notepad: Notepad,
    ):
        subs = notepad.add_subsections("foo", "bar", "baz")

        assert len(subs) == 3
        labels = [sub.label for sub in subs]
        assert labels == ["foo", "bar", "baz"]
        levels = [sub.level for sub in subs]
        assert levels == [1, 2, 3]
