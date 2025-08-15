****
代码
****

为了支持快速开发而不破坏稳定版本，本项目使用双层分支模型：

.. image:: assets/branches.png
   :alt: 分支模型

`灵感来源 <https://miro.medium.com/max/700/1*2YagIpX6LuauC3ASpwHekg.png>`_

- **dev**: 新功能和一些错误修复在此处合并。此分支允许在合并到稳定分支之前进行集体测试、解决冲突和进一步稳定。
- **main**: 创建PIP版本的稳定分支。

默认情况下，分支目标为 **main**，但大多数贡献应针对 **dev**。

**例外**:
如果满足以下条件，则允许直接合并到 **main**：

- `yfinance` 严重损坏
- `yfinance` 的一部分损坏，且修复简单且隔离
- 不更新代码（例如文档）

创建您的分支
--------------------

1. 在GitHub上Fork本仓库。如果已经Fork，请记得 ``Sync fork``

2. 克隆您Fork的仓库：

   .. code-block:: bash

      git clone https://github.com/{user}/{repo}.git

3. 从适当的基础分支为您的功能或错误修复创建一个新分支：

   .. code-block:: bash

      git checkout {base e.g. dev}
      git pull
      git checkout -b {your branch}

4. 进行更改，提交它们，然后将您的分支推送到GitHub。为了保持提交历史和`网络图 <https://github.com/ranaroussi/yfinance/network>`_ 的紧凑，请为您的提交提供非常简短的摘要和描述：

   .. code-block:: bash

      git commit -m "简短的句子摘要" -m "完整的提交信息"
      # 长消息可以有多行（提示：复制粘贴）

6. `在Github上打开一个拉取请求 <https://github.com/ranaroussi/yfinance/pulls>`_.

运行一个分支
----------------

请参阅 `此页面 </development/running>`_.

Git相关
---------

- 您可能会被要求将您的分支从 ``main`` 移动到 ``dev``。这是一个 ``git rebase``。请记住更新**所有**涉及的分支。

  .. code-block:: bash

     # 更新所有分支:
     git checkout main
     git pull
     git checkout dev
     git pull
     # 从main rebase到dev:
     git checkout {your branch}
     git pull
     git rebase --onto dev main {your branch}
     git push --force-with-lease origin {your branch}

- ``git rebase`` 也可用于使用基础分支的新提交来更新您的分支，但不会像git merge那样向您的分支历史记录中添加提交。这可以保持历史记录的整洁并避免未来的合并问题。

  .. code-block:: bash

     git checkout {base branch e.g. dev}
     git pull
     git checkout {your branch}
     git rebase {base}
     git push --force-with-lease origin {your branch}

- ``git squash`` 将微小或可忽略的提交与有意义的提交合并，或将连续相关的提交合并。`git squash指南 <https://docs.gitlab.com/ee/topics/git/git_rebase.html#interactive-rebase>`_

  .. code-block:: bash

     git rebase -i HEAD~2
     git push --force-with-lease origin {your branch}
