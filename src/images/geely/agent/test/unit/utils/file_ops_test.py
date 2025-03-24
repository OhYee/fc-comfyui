import os
import pytest
import shutil
from utils.file_ops import copy, move, remove, compress, extract, create_symlink


# 创建测试用的临时目录和文件
@pytest.fixture
def setup_test_files(tmp_path):
    # 创建源文件和目录
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # 创建测试文件
    test_file = source_dir / "test.txt"
    test_file.write_text("test content")

    # 创建测试子目录
    test_subdir = source_dir / "subdir"
    test_subdir.mkdir()
    (test_subdir / "subfile.txt").write_text("subfile content")

    return tmp_path


def test_copy_file(setup_test_files):
    source_file = setup_test_files / "source" / "test.txt"
    target_file = setup_test_files / "target" / "test.txt"

    copy(str(source_file), str(target_file))

    assert target_file.exists()
    assert target_file.read_text() == "test content"


def test_copy_directory(setup_test_files):
    source_dir = setup_test_files / "source"
    target_dir = setup_test_files / "target"

    copy(str(source_dir), str(target_dir))

    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()


def test_copy_symlink(setup_test_files):
    source_dir = setup_test_files / "source"
    test_file = source_dir / "test.txt"
    symlink_file = source_dir / "link"
    os.symlink(str(test_file), str(symlink_file))

    target_dir = setup_test_files / "target"

    copy(str(source_dir), str(target_dir))

    target_symlink = target_dir / "link"
    assert os.path.islink(str(target_symlink))
    assert os.path.realpath(str(target_symlink)) == os.path.realpath(str(test_file))


def test_copy_symlink_file(setup_test_files):
    source_dir = setup_test_files / "source"
    test_file = source_dir / "test.txt"
    symlink_file = source_dir / "link"
    os.symlink(str(test_file), str(symlink_file))

    target_symlink = setup_test_files / "target" / "link"

    copy(str(symlink_file), str(target_symlink))

    assert os.path.islink(str(target_symlink))
    assert os.readlink(str(target_symlink)) == str(test_file)


def test_copy_symlink_to_directory(setup_test_files):
    source_dir = setup_test_files / "source"
    subdir = source_dir / "subdir"
    symlink_dir = source_dir / "link_to_subdir"
    os.symlink(str(subdir), str(symlink_dir))

    target_dir = setup_test_files / "target"

    copy(str(source_dir), str(target_dir))

    target_symlink = target_dir / "link_to_subdir"
    assert os.path.islink(str(target_symlink))
    assert os.path.realpath(str(target_symlink)) == os.path.realpath(str(subdir))


def test_move_file(setup_test_files):
    source_file = setup_test_files / "source" / "test.txt"
    target_file = setup_test_files / "target" / "test.txt"

    move(str(source_file), str(target_file))

    assert target_file.exists()
    assert not source_file.exists()
    assert target_file.read_text() == "test content"


def test_move_directory(setup_test_files):
    source_dir = setup_test_files / "source"
    target_dir = setup_test_files / "target"

    move(str(source_dir), str(target_dir))

    assert target_dir.exists()
    assert not source_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()


def test_remove_file(setup_test_files):
    test_file = setup_test_files / "source" / "test.txt"

    assert test_file.exists()
    remove(str(test_file))
    assert not test_file.exists()


def test_remove_directory(setup_test_files):
    source_dir = setup_test_files / "source"

    assert source_dir.exists()
    remove(str(source_dir))
    assert not source_dir.exists()


def test_remove_nonexistent_path(setup_test_files):
    nonexistent_path = setup_test_files / "nonexistent"

    # Should print message but not raise exception
    remove(str(nonexistent_path))


def test_compress_all_files(setup_test_files):
    source_dir = setup_test_files / "source"
    tar_file = setup_test_files / "test.tar"

    compress(str(tar_file), str(source_dir))

    assert tar_file.exists()


def test_compress_selected_files(setup_test_files):
    source_dir = setup_test_files / "source"
    tar_file = setup_test_files / "test.tar"

    compress(str(tar_file), str(source_dir), ["test.txt"])

    assert tar_file.exists()


def test_extract(setup_test_files):
    # 首先创建一个tar文件
    source_dir = setup_test_files / "source"
    tar_file = setup_test_files / "test.tar"
    output_dir = setup_test_files / "extracted"

    compress(str(tar_file), str(source_dir))
    extract(str(tar_file), str(output_dir))

    assert output_dir.exists()
    assert (output_dir / "test.txt").exists()
    assert (output_dir / "subdir" / "subfile.txt").exists()


def test_extract_to_default_location(setup_test_files):
    source_dir = setup_test_files / "source"
    tar_file = setup_test_files / "test.tar"

    compress(str(tar_file), str(source_dir))
    extract(str(tar_file))

    assert tar_file.parent.exists()
    assert (tar_file.parent / "test.txt").exists()
    assert (tar_file.parent / "subdir" / "subfile.txt").exists()


# 错误处理测试
def test_copy_nonexistent_source():
    with pytest.raises(Exception):
        copy("nonexistent_file", "target")


def test_move_nonexistent_source():
    with pytest.raises(Exception):
        move("nonexistent_file", "target")


def test_extract_nonexistent_tar():
    with pytest.raises(Exception):
        extract("nonexistent.tar")


def test_create_symlink(setup_test_files):
    source_file = setup_test_files / "source" / "test.txt"
    link_path = setup_test_files / "link.txt"

    create_symlink(str(source_file), str(link_path))

    assert os.path.islink(str(link_path))
    assert os.readlink(str(link_path)) == str(source_file)
    assert link_path.read_text() == "test content"


def test_create_symlink_force(setup_test_files):
    # 创建一个原始文件
    original_file = setup_test_files / "original.txt"
    original_file.write_text("original content")

    # 创建目标文件
    source_file = setup_test_files / "source" / "test.txt"
    link_path = setup_test_files / "original.txt"

    # 使用force选项创建符号链接
    create_symlink(str(source_file), str(link_path), force=True)

    assert os.path.islink(str(link_path))
    assert os.readlink(str(link_path)) == str(source_file)
    assert link_path.read_text() == "test content"


def test_create_symlink_force_existing_symlink(setup_test_files):
    # 创建源文件
    source_file1 = setup_test_files / "source1.txt"
    source_file1.write_text("source1 content")

    source_file2 = setup_test_files / "source2.txt"
    source_file2.write_text("source2 content")

    # 先创建指向source1的软链接
    link_path = setup_test_files / "link.txt"
    os.symlink(str(source_file1), str(link_path))

    # 验证初始软链接
    assert os.path.islink(str(link_path))
    assert os.readlink(str(link_path)) == str(source_file1)
    assert link_path.read_text() == "source1 content"

    # 使用force选项创建指向source2的新软链接
    create_symlink(str(source_file2), str(link_path), force=True)

    # 验证软链接已更新
    assert os.path.islink(str(link_path))
    assert os.readlink(str(link_path)) == str(source_file2)
    assert link_path.read_text() == "source2 content"


def test_create_symlink_force_existing_broken_symlink(setup_test_files):
    # 创建新的源文件
    source_file = setup_test_files / "source.txt"
    source_file.write_text("source content")

    # 创建一个指向不存在文件的损坏软链接
    link_path = setup_test_files / "broken_link.txt"
    nonexistent_path = setup_test_files / "nonexistent.txt"
    os.symlink(str(nonexistent_path), str(link_path))

    # 验证初始软链接状态
    assert os.path.islink(str(link_path))
    assert os.readlink(str(link_path)) == str(nonexistent_path)
    assert not os.path.exists(str(link_path))  # 验证链接是损坏的
    assert os.path.lexists(str(link_path))     # 但链接本身存在

    # 使用force选项创建新的软链接
    create_symlink(str(source_file), str(link_path), force=True)

    # 验证软链接已更新
    assert os.path.islink(str(link_path))
    assert os.readlink(str(link_path)) == str(source_file)
    assert os.path.exists(str(link_path))      # 现在链接是有效的
    assert link_path.read_text() == "source content"


def test_create_symlink_force_existing_directory(setup_test_files):
    # 创建源目录
    source_dir = setup_test_files / "source_dir"
    source_dir.mkdir()
    (source_dir / "test.txt").write_text("source content")

    # 创建目标目录并添加一些内容
    target_dir = setup_test_files / "target_dir"
    target_dir.mkdir()
    (target_dir / "existing.txt").write_text("existing content")

    # 使用force选项创建软链接
    create_symlink(str(source_dir), str(target_dir), force=True)

    # 验证目录已被软链接替换
    assert os.path.islink(str(target_dir))
    assert os.readlink(str(target_dir)) == str(source_dir)
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "test.txt").read_text() == "source content"
    # 验证原目录内容已被删除
    assert not os.path.exists(str(target_dir / "existing.txt"))


def test_create_symlink_directory(setup_test_files):
    source_dir = setup_test_files / "source"
    link_path = setup_test_files / "link_dir"

    create_symlink(str(source_dir), str(link_path))

    assert os.path.islink(str(link_path))
    assert os.readlink(str(link_path)) == str(source_dir)
    assert (link_path / "test.txt").exists()


def test_create_symlink_nonexistent_source():
    with pytest.raises(Exception):
        create_symlink("nonexistent_file", "link_path")


def test_create_symlink_existing_without_force(setup_test_files):
    source_file = setup_test_files / "source" / "test.txt"
    link_path = setup_test_files / "link.txt"

    # 首先创建一个文件
    link_path.write_text("existing content")

    # 尝试创建符号链接但不使用force选项
    with pytest.raises(Exception):
        create_symlink(str(source_file), str(link_path), force=False)


def test_create_symlink_existing_directory_force(setup_test_files):
    source_dir = setup_test_files / "source"
    existing_dir = setup_test_files / "existing_dir"

    # 创建一个已存在的目录
    existing_dir.mkdir()
    (existing_dir / "existing_file.txt").write_text("existing content")

    # 使用force选项创建符号链接
    create_symlink(str(source_dir), str(existing_dir), force=True)

    assert os.path.islink(str(existing_dir))
    assert os.readlink(str(existing_dir)) == str(source_dir)
    assert (existing_dir / "test.txt").exists()


# 清理函数
@pytest.fixture(autouse=True)
def cleanup(setup_test_files):
    yield
    # 测试后清理临时文件
    shutil.rmtree(setup_test_files)
