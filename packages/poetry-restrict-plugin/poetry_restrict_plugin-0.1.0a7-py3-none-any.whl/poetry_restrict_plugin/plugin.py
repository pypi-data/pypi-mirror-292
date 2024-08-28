import os.path
import pathlib
import sys
import traceback

import poetry as poetry_package
from cleo.io.io import IO
from landlock import FSAccess, Ruleset
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry


def existing_paths(paths):
    assert isinstance(paths, (list, tuple))
    for path in paths:
        if os.path.exists(path):
            yield path


def ensure_paths(paths):
    assert isinstance(paths, (list, tuple))
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
        yield path


class RestrictPlugin(Plugin):
    def landlock(self, poetry: Poetry):
        # /home/user/.local/pipx/venvs/poetry/lib/python3.11/site-packages
        poetry_libs_path = pathlib.Path(poetry_package.__path__._path[0]).parent
        # Needed, otherwise raises:
        #   Fatal Python error: init_import_site: Failed to import the site module
        # /home/user/.local/pipx/venvs/poetry/pyvenv.cfg
        poetry_pyvenv_cfg = poetry_libs_path.parent.parent.parent / "pyvenv.cfg"

        ruleset = Ruleset()

        # Rules for Poetry's virtual environment management
        ruleset.allow(
            *ensure_paths(
                (
                    # Storing the virtual environment
                    poetry.config.virtualenvs_path,
                    # Cached dependencies
                    poetry.config.artifacts_cache_directory,
                    poetry.config.repository_cache_directory
                ),
            ),
            rules=FSAccess.all(),
        )
        #   Temporary storage
        ruleset.allow("/tmp", rules=FSAccess.all() & ~FSAccess.EXECUTE)
        # Poetry may also want to late-import some of its dependencies, or built-in modules
        ruleset.allow(*existing_paths(sys.path), rules=FSAccess.READ_FILE | FSAccess.READ_DIR)

        # Finally, the Python executable may need to import some of its shared libraries
        ruleset.allow(
            *existing_paths(("/lib", "/lib64")),
            rules=FSAccess.READ_FILE | FSAccess.READ_DIR | FSAccess.EXECUTE,
        )
        # and in poetry shell, we might want to run some system executables, too
        ruleset.allow("/usr/bin", rules=FSAccess.READ_FILE | FSAccess.READ_DIR | FSAccess.EXECUTE)

        # For compilation of C dependencies, we need to be able to find headers
        ruleset.allow(*existing_paths(("/usr/include",)), rules=FSAccess.READ_FILE | FSAccess.READ_DIR)

        # We allow read access here, later we might want to restrict the pid namespace though
        ruleset.allow("/proc", rules=FSAccess.READ_FILE | FSAccess.READ_DIR)
        # needed for /dev/tty and /dev/pty devices, see /usr/lib/python3.11/pty.py
        ruleset.allow("/dev", rules=FSAccess.READ_FILE | FSAccess.READ_DIR | FSAccess.WRITE_FILE)

        # Python's `zoneinfo` module
        ruleset.allow("/usr/share/zoneinfo/", rules=FSAccess.READ_FILE | FSAccess.READ_DIR)

        ruleset.allow(
            # We need to know which DNS resolver to use, and any custom hosts
            *existing_paths(("/etc/resolv.conf", "/etc/hosts")),
            # pip reads this file in _vendor/distro/distro.py
            *existing_paths(("/etc/debian_version",)),
            # I'm not opposed to including things like this because I don't want to annoy people
            # when their tooling doesn't work. But we have to be conservative. I think shells
            # are fine, but if there was some further tooling (e.g. shell tools run at startup)
            # I don't think those should be included.
            *existing_paths(("/etc/bash.bashrc", os.path.expanduser("~/.bashrc"))),
            rules=FSAccess.READ_FILE,
        )
        ruleset.allow("/etc/ssl/certs", "/usr/local/share/ca-certificates", rules=FSAccess.READ_FILE | FSAccess.READ_DIR)

        # Allow determining mime types. Used for ruamel.yaml installation.
        ruleset.allow("/etc/mime.types", rules=FSAccess.READ_FILE)

        # Allow working with shared memory
        ruleset.allow("/dev/shm")

        # Black cache access
        ruleset.allow(
            *existing_paths((os.path.expanduser("~/.cache/black"),)),
            rules=FSAccess.READ_FILE | FSAccess.WRITE_FILE | FSAccess.READ_DIR,
        )

        pre_commit_cache = os.path.expanduser("~/.cache/pre-commit")
        if os.path.exists(pre_commit_cache):
            ruleset.allow(pre_commit_cache)
            # pre-commit runs git to figure out the diff to lint, which will
            # be pretty noisy if we do not whitelist the gitconfig.
            ruleset.allow(
                *existing_paths(
                    (
                        os.path.expanduser("~/.gitconfig"),
                        os.path.expanduser("~/.config/git/config")
                    )
                ),
                rules=FSAccess.READ_FILE,
            )

        # # Usage of Ansible with DEFAULT_LOCAL_TMP
        # ruleset.allow(*existing_paths((os.path.expanduser("~/.ansible/tmp"),)))
        # ruleset.allow("/etc/passwd", rules=FSAccess.READ_FILE)
        # ruleset.allow(*existing_paths((os.path.expanduser("~/.ssh/known_hosts"),)), rules=FSAccess.READ_FILE)

        # Allow manipulation of files in our projects, e.g. for linters.
        # We might need to check this more thoroughly. For instance, configuring custom
        # filter programs in gitattributes might allow a sandbox escape.
        ruleset.allow(os.path.dirname(poetry.pyproject_path))

        # => Rules for poetry-in-poetry
        #
        # This is suboptimal. It is needed for nested invocations of poetry, which
        # sometimes happen through a combination of tooling (e.g. script calling
        # command through poetry being run in poetry shell). However, the
        # poetry configuration directory contains a file named `auth.toml`, which
        # sounds it makes sense to restrict. The cleaner solution here would be
        # to mount a tmpfs over here so it appears empty.
        ruleset.allow(
            *existing_paths((os.path.expanduser("~/.config/pypoetry"),)),
            rules=FSAccess.READ_FILE | FSAccess.READ_DIR,
        )
        # Python may need to read pyvenv.cfg
        ruleset.allow(poetry_pyvenv_cfg, rules=FSAccess.READ_FILE)

        ruleset.apply()

    def activate(self, poetry: Poetry, io: IO):
        if os.getenv("POETRY_NO_RESTRICT") == "1":
            io.write_line(
                "<info>poetry-restrict-plugin</info>: "
                "<comment>Disabled via POETRY_NO_RESTRICT environment variable!</comment>"
            )
            return

        try:
            self.landlock(poetry)
            io.write_line("<info>poetry-restrict-plugin</info>: Landlock engaged.")
        except Exception as err:
            io.write_line("<error>Fatal error trying to enforce Landlock rules:</error>")
            traceback.print_exception(err)
            io.write_line("<error>This is an issue of the Poetry restrict plugin, not of Poetry itself.</error>")
            raise
