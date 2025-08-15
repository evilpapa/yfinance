# 贡献

yfinance依靠社区来调查错误和贡献代码。

这是一个快速简短的指南，完整指南请访问 https://ranaroussi.github.io/yfinance/development/index.html

## 分支

YFinance使用双层分支模型：

* **dev**: 新功能和大多数错误修复在此合并，一起测试，解决冲突等。
* **main**: 创建PIP版本的稳定分支。

## 运行分支

```bash
pip install git+ranaroussi/yfinance.git@dev  # <- dev 分支
```

https://ranaroussi.github.io/yfinance/development/running.html

### 我是GitHub新手，如何贡献代码？

1. Fork本项目。如果已经fork，请记得 `Sync fork`

2. 在你的fork中实现你的更改，最好在一个特定的分支中

3. 从你的fork创建一个到本项目的[Pull Request](https://github.com/ranaroussi/yfinance/pulls)。如果解决一个Issue，请链接到它

https://ranaroussi.github.io/yfinance/development/code.html

## 文档网站

新的文档网站是根据代码自动生成的。https://ranaroussi.github.io/yfinance/index.html

当您更改代码时，请记住更新文档，并在本地检查文档。

https://ranaroussi.github.io/yfinance/development/documentation.html

## Git技巧

帮助保持Git提交历史和[网络图](https://github.com/ranaroussi/yfinance/network)的紧凑：

* 有一个长的描述性提交信息？`git commit -m "简短的句子摘要" -m "完整的提交信息"`

* 使用 `git squash` 将多个提交合并为1个

* `git rebase` 是你的朋友：更改基础分支，或“合并”更新

https://ranaroussi.github.io/yfinance/development/code.html#git-stuff

## 单元测试

测试是使用内置的Python模块 `unittest` 编写的。例子：

* 运行所有测试：`python -m unittest discover -s tests`

https://ranaroussi.github.io/yfinance/development/testing.html

> 更多信息请参阅[开发者指南](https://ranaroussi.github.io/yfinance/development/contributing.html#GIT-STUFF)。
