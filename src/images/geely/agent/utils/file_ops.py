import tarfile
import shutil
import os


def copy(source_path, target_path):
    """
    复制文件/文件夹

    Args:
        source_path: 源路径(文件或目录)
        target_path: 目标路径
    """
    try:
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        if os.path.isfile(source_path):
            shutil.copy2(source_path, target_path, follow_symlinks=False)
        else:
            shutil.copytree(source_path, target_path, symlinks=True, dirs_exist_ok=True)

    except Exception as e:
        print(f"Failed to copy {source_path} to {target_path}, reason: {e}")
        raise


def move(source_path, target_path):
    """
    移动文件/文件夹

    Args:
        source_path: 源路径(文件或目录)
        target_path: 目标路径
    """
    try:
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        if os.path.isfile(source_path):
            shutil.move(source_path, target_path)
        else:
            # 如果目标路径已存在,先删除
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.move(source_path, target_path)

    except Exception as e:
        print(f"Failed to move {source_path} to {target_path}, reason: {e}")
        raise


def remove(path):
    """
    删除文件或目录

    Args:
        path: 要删除的文件或目录的路径
    """
    try:
        if os.path.isfile(path):
            # 删除文件
            os.remove(path)
        elif os.path.isdir(path):
            # 删除目录及其所有内容
            shutil.rmtree(path)
        else:
            print(f"Path does not exist: {path}")

    except Exception as e:
        print(f"Failed to remove {path}, reason: {e}")
        raise


def compress(tar_file_path, source_dir, selected_files=None):
    """
    打包文件/文件夹

    Args:
        tar_file_path: 输出的tar文件路径
        source_dir: 待打包文件所在父目录
        selected_files: 父目录下，待打包文件/文件夹名列表，None表示全部打包
    """

    try:
        with tarfile.open(tar_file_path, "w:") as tar:
            # 保存当前工作目录
            original_dir = os.getcwd()
            try:
                os.chdir(source_dir)

                # 使用os.scandir()遍历一级目录
                with os.scandir('.') as entries:
                    for entry in entries:
                        # 如果指定了目标文件列表，则只处理列表中的文件
                        if selected_files is None or entry.name in selected_files:
                            tar.add(entry.name)
            finally:
                # 恢复原始工作目录
                os.chdir(original_dir)
    except Exception as e:
        print(f"Failed to compress tar, reason: {e}")
        raise


def extract(tar_file_path, output_dir=None):
    """
    解压tar包

    Args:
        tar_file_path: tar文件路径
        output_dir: 解压输出目录，默认为None，表示解压到tar文件所在目录
    """

    # 如果未指定输出目录，使用tar文件所在目录
    if output_dir is None:
        output_dir = os.path.dirname(tar_file_path)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        with tarfile.open(tar_file_path, 'r:*') as tar:
            tar.extractall(path=output_dir)
    except Exception as e:
        print(f"Failed to extract tar, reason: {e}")
        raise


def create_symlink(source_path, link_path, force=False):
    """
    创建符号链接

    Args:
        source_path: 源路径
        link_path: 链接路径
        force: 是否强制创建（如果链接已存在则先删除）
    """
    try:
        # 确保源路径存在
        if not os.path.exists(source_path):
            raise Exception(f"Source path does not exist: {source_path}")
        # 如果链接已存在且force为True，则删除已存在的链接
        if force and os.path.lexists(link_path):
            if os.path.islink(link_path):
                os.unlink(link_path)
            elif os.path.isfile(link_path):
                os.remove(link_path)
            elif os.path.isdir(link_path):
                shutil.rmtree(link_path)

        # 确保链接的父目录存在
        os.makedirs(os.path.dirname(link_path), exist_ok=True)

        # 创建符号链接
        os.symlink(source_path, link_path)

    except Exception as e:
        print(f"Failed to create symlink from {source_path} to {link_path}, reason: {e}")
        raise
