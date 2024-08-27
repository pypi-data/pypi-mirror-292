import sys

from displayhooks import autorestore_displayhook


def test_restore():
    hook_before_declaration = sys.displayhook
    @autorestore_displayhook
    def do_something():
        sys.displayhook = 5

    hook_before_calling = sys.displayhook

    do_something()

    assert hook_before_declaration is sys.displayhook
    assert hook_before_calling is sys.displayhook
