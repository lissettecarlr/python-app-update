import subprocess
import os
import zipfile

# 关闭windows软件
def close_software_windows(name):
    subprocess.call(['taskkill', '/F', '/IM', name])

def start_soft_windows(path):
    os.startfile(path)
    
# 替换软件
def replace_software_windows(old_path, new_path):
    # 判断old_path和new_path是文件夹还是文件
    if os.path.isdir(old_path) and os.path.isdir(new_path):
        # 删除旧文件中所有内容，将新文件夹中的内容复制到旧文件夹中
        for file in os.listdir(old_path):
            os.remove(os.path.join(old_path, file))
        for file in os.listdir(new_path):
            os.rename(os.path.join(new_path, file), os.path.join(old_path, file))
    elif os.path.isfile(old_path) and os.path.isfile(new_path):
        # 删除旧文件，将新文件重命名
        os.remove(old_path)
        os.rename(new_path, old_path)
    else:
        return False
    return True

# 解压缩，解压的文件路径
def unzip_file_windows(file_path):
    # 判断该文件是否存在，且是压缩包的格式
    if os.path.isfile(file_path) and file_path.endswith('.zip'):
        # 上一级路径，也是解压路径
        parent_dir = os.path.dirname(file_path)
        print(parent_dir)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(parent_dir)
    else:
        return None


if __name__ == "__main__":
    # 测试
    #close_software_windows("notepad.exe")
    #start_soft_windows("C:\\Users\\Administrator\\Desktop\\test\\test.exe")
    #replace_software_windows("C:\\Users\\Administrator\\Desktop\\test\\test.exe", "C:\\Users\\Administrator\\Desktop\\test\\test2.exe")
    unzip_file_windows("D:\\code\\ggggg\\python-app-update\\temp\\openai-proxy.zip")
    pass