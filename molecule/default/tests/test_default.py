import os

TEST_ROOT = os.path.join(os.environ["MOLECULE_EPHEMERAL_DIRECTORY"], "test-root")


def _path(*parts: str) -> str:
    return os.path.join(TEST_ROOT, *parts)


def test_basic_tree_copy(host):
    root = os.path.join(TEST_ROOT, "basic")
    assert host.file(os.path.join(root, "top.txt")).exists
    assert host.file(os.path.join(root, "sub", "inner.txt")).exists
    assert host.file(os.path.join(root, "sub", "nested", "deep.txt")).exists
    assert host.file(os.path.join(root, "config.ini")).exists
    assert not host.file(os.path.join(root, "config.ini.j2")).exists

    assert (
        host.file(os.path.join(root, "top.txt")).content_string == "top file content\n"
    )
    assert (
        host.file(os.path.join(root, "config.ini")).content_string
        == "port=8080\nhost=example.internal\n"
    )
    assert (
        host.file(os.path.join(root, "sub", "nested", "deep.txt")).content_string
        == "deep file content\n"
    )


def test_modes(host):
    assert host.file(os.path.join(TEST_ROOT, "basic", "top.txt")).mode == 0o644
    assert host.file(os.path.join(TEST_ROOT, "basic", "sub")).mode == 0o755
    assert host.file(os.path.join(TEST_ROOT, "basic", "sub", "nested")).mode == 0o755
    assert host.file(os.path.join(TEST_ROOT, "basic")).mode == 0o755


def test_merge_multiple_sources(host):
    root = os.path.join(TEST_ROOT, "merged")
    for rel in (
        "top.txt",
        "sub/inner.txt",
        "sub/nested/deep.txt",
        "config.ini",
        "bfile.txt",
        "sub/from_b.txt",
        "single.txt",
    ):
        assert host.file(os.path.join(root, rel)).exists, f"missing {rel}"


def test_single_file_source(host):
    f = host.file(os.path.join(TEST_ROOT, "single", "single.txt"))
    assert f.exists
    assert f.content_string == "single file content\n"


def test_directory_without_trailing_slash(host):
    root = os.path.join(TEST_ROOT, "withdir")
    assert host.file(os.path.join(root, "tree_b", "bfile.txt")).exists
    assert host.file(os.path.join(root, "tree_b", "sub", "from_b.txt")).exists
    assert not host.file(os.path.join(root, "bfile.txt")).exists


def test_exclusive_removes_stray_entries(host):
    root = os.path.join(TEST_ROOT, "exclusive")
    assert host.file(os.path.join(root, "top.txt")).exists
    assert not host.file(os.path.join(root, "stray.txt")).exists
    assert not host.file(os.path.join(root, "stray_dir")).exists
    assert not host.file(os.path.join(root, "stray_dir", "deep_stray.txt")).exists


def test_exclusive_ignore(host):
    root = os.path.join(TEST_ROOT, "exclusive_ignore")
    assert not host.file(os.path.join(root, "stray.txt")).exists
    assert host.file(os.path.join(root, "keep_dir", "keep.txt")).exists
    assert host.file(os.path.join(root, "abs_keep", "abs.txt")).exists
    assert host.file(os.path.join(root, "top.txt")).exists
