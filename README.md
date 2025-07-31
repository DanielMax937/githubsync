## resource
https://github.com/google-gemini/cookbook/tree/main/examples
https://colab.research.google.com/drive/1hE6_jS3sji1X7NblKRkwwznl8Qw8zsoI#scrollTo=lSkx3VHr3WYb
https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Browser_as_a_tool.ipynb
https://github.com/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb

## 清理git下的磁盘文件
find /Volumes/SE/git -type d -name .git -exec sh -c 'echo "--- Deleting ._ files in repo: $(dirname {}) ---"; find {} -name "._*" -type f -delete' {} \;

## 子目录数量
ls -F | grep / | wc -l

