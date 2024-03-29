# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import getpass
import pathlib
import configparser

import invoke
import parver

from . import docs, package
from .utils import (
    report,
    get_tag_content,
    get_artifact_paths,
    get_previous_version,
    get_username_password,
)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

# parse setup.cfg to gather metadata info (reduce redundancy of static info)
config = configparser.ConfigParser()
config.read(BASE_DIR.joinpath("setup.cfg").as_posix())

try:
    metadata = config["metadata"]
except KeyError:
    raise KeyError(
        f"cannot run invoke tasks if setup.cfg is missing [metadata] section"
    )


@invoke.task()
def profile(ctx, filepath, calltree=False):
    """ Run and profile a given Python script.

    :param str filepath: The filepath of the script to profile
    """

    filepath = pathlib.Path(filepath)
    if not filepath.is_file():
        report.error(ctx, "profile", f"no such script {filepath!s}")
    else:
        if calltree:
            report.info(ctx, "profile", f"profiling script {filepath!s} calltree")
            ctx.run(
                (
                    f"python -m cProfile -o .profile.cprof {filepath!s}"
                    " && pyprof2calltree -k -i .profile.cprof"
                    " && rm -rf .profile.cprof"
                )
            )
        else:
            report.info(ctx, "profile", f"profiling script {filepath!s}")
            ctx.run(f"vprof -c cmhp {filepath!s}")


@invoke.task(post=[docs.build, package.build, package.check])
def build(ctx):
    """ Build the project.
    """

    report.success(ctx, "build", f"building project {ctx.metadata['name']!r}")


@invoke.task(post=[package.clean, docs.clean])
def clean(ctx):
    """ Clean the project.
    """

    report.success(ctx, "clean", f"cleaning project {ctx.metadata['name']!r}")


@invoke.task(pre=[clean, docs.build_news, build])  # noqa
def publish(ctx, test=False, force=False, draft=False):
    """ Publish the project.

    :param bool test: Publishes to PyPi test server (defaults to False)
    :param bool force: Skip version check (defaults to False)
    :param bool draft: Sample publish (has no effect) (defaults to False)
    """

    previous_version = get_previous_version(ctx)
    current_version = parver.Version.parse(metadata["version"])

    if current_version <= previous_version and not force:
        error_message = (
            f"current version ({current_version!s}) is <= to previous version "
            f"({previous_version!s}), use 'package.version' to update current version"
        )
        report.error(ctx, "publish", error_message)
        raise ValueError(error_message)

    report.info(ctx, "publish", f"publishing project {ctx.metadata['name']!r}")
    report.warning(
        ctx,
        "publish",
        f"drafting publish for project {ctx.metadata['name']!r} (has no effect)",
    )

    commit_message = f"Release {current_version!s}"
    report.info(ctx, "publish", f"git commiting release {commit_message!r}")
    git_commit_command = f"git commit -asm {commit_message!r}"
    if not draft:
        ctx.run(git_commit_command)

    tag_content = get_tag_content(ctx).replace('"', '\\"')
    git_tag_command = (
        f'git tag -a "v{current_version!s}" -m '
        f'"Version {current_version!s}\n\n{tag_content}"'
    )
    report.info(
        ctx, "publish", f"git tagging commit as release for version {current_version!s}"
    )
    if not draft:
        ctx.run(git_tag_command)

    artifact_paths = [f"{_.as_posix()!r}" for _ in get_artifact_paths(ctx)]
    for artifact_path in artifact_paths:
        report.debug(ctx, "publish", f"publishing artifact {artifact_path}")
    publish_command = f"twine upload {' '.join(artifact_paths)}"
    if test:
        publish_command += " --repository 'https://test.pypi.org/legacy/'"

    # get user to confirm publish
    try:
        input(
            report._get_text(
                ctx,
                "success",
                "publish",
                "about to publish, [Enter] to continue, [Ctrl-C] to abort: ",
            )
        )

        while True:
            (username, password) = get_username_password(
                ctx, "PyPi Username: ", "PyPi Password: "
            )
            # TODO: check if username and password are valid before tyring to post
            report.info(ctx, "publish", f"publishing project {ctx.metadata['name']!s}")
            if not draft:
                publish_command += f" -u {username!r} -p {password!r}"
                publish_result = ctx.run(publish_command, warn=True)
                if publish_result.exited:
                    report.error(
                        ctx,
                        "publish",
                        f"failed to publish {ctx.metadata['name']!s} (retrying)",
                    )
                    continue
            break

        git_push_command = "git push --tags"
        report.info(ctx, "publish", f"pushing git tags")
        if not draft:
            ctx.run(git_push_command)
    except KeyboardInterrupt:
        print()
        report.error(ctx, "publish", "aborting publish!")
        git_remove_tag_command = f"git tag -d {current_version!s}"
        report.warn(ctx, "publish", "removing git tags")
        if not draft:
            ctx.run(git_remove_tag_command)
        git_reset_command = f"git reset --soft HEAD^"
        report.warn(ctx, "publish", "softly reseting commit")
        if not draft:
            ctx.run(git_reset_command)


namespace = invoke.Collection(build, clean, publish, docs, package, profile)
namespace.configure(
    {
        "metadata": metadata,
        "directory": BASE_DIR,
        "package": {"directory": BASE_DIR / "src" / metadata["package_name"]},
        "docs": {"directory": BASE_DIR / "docs"},
    }
)
