import os
import subprocess
import datetime

# 设置包含 Git 仓库的主文件夹路径
base_dir = '/Volumes/SE/git'  # The directory to cd into before cloning
log_file = "failed_repos.log"

# 遍历 base_dir 中的所有子文件夹
for folder in os.listdir(base_dir):
    repo_path = os.path.join(base_dir, folder)

    # 检查是否是文件夹，并且包含 .git 目录（说明是一个 git 仓库）
    if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, '.git')):
        print(f"\n📁 正在更新仓库: {folder}")
        try:
            # 执行 git pull 命令
            # result = subprocess.run(["git", "pull"], cwd=repo_path, capture_output=True, text=True)
            # print(result.stdout)
            clean_command = 'find .git -name "._*" -type f -delete'
            clean_result = subprocess.run(
                clean_command,
                cwd=repo_path,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            # find -delete 命令成功时通常没有输出到 stdout
            # 但如果出现警告或信息，可能会输出到 stderr
            if clean_result.stderr:
                print(f"清理命令输出 (stderr):\n{clean_result.stderr}")
            print(f"清理成功: {repo_path}，开始更新")
            subprocess.run(['git', 'pull'], cwd=repo_path, check=True)
            print(f"✅ Done: {folder}")
            # if result.stderr:
            #     print("⚠️ 错误信息:", result.stderr)
        except Exception as e:
            print(f"❌ 更新失败: {e}")
            with open(log_file, "a", encoding="utf-8") as f:
                now = datetime.datetime.now()
                current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_time_str}] [{folder}] 执行异常:\n{str(e)}\n\n")
