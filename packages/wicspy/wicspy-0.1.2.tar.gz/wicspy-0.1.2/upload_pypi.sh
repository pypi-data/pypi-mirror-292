#!/bin/zsh
###
 # @Author: wicsp wicspa@gmail.com
 # @Date: 2024-06-05 17:38:35
 # @LastEditors: wicsp wicspa@gmail.com
 # @LastEditTime: 2024-08-26 18:03:00
 # @FilePath: /wicspy/upload_pypi.sh
 # @Description: 
 # 
 # Copyright (c) 2024 by wicsp, All Rights Reserved. 
### 

# 检查是否提供了 commit message
if [ -z "$1" ]; then
  echo "Missing Commit Message!"
  exit 1
fi

COMMIT_MESSAGE=$1

# 删除旧的构建文件
rm -rf ./dist

# 创建新的构建文件
# 上传到 PyPI
rye publish

# 提交到 git
git add .
git commit -m "$COMMIT_MESSAGE"
git push