*************
文档
*************

.. contents:: 文档:
   :local:

关于文档
-------------------
* yfinance文档是用reStructuredText (rst)编写的，并使用Sphinx构建。
* 文档文件位于 ``doc/source/..``。
* API参考下的大多数注释都是从类和方法的文档字符串中读取的。这些位于 ``doc/source/reference/api`` 的文档是由Sphinx自动生成的，不包含在git中。

在本地构建文档
-------------------------------
要在本地构建文档，请按照以下步骤操作：

1. **安装所需依赖**:

   * 确保已安装 ``Sphinx`` 和任何其他依赖项。如果提供了 ``requirements.txt`` 文件，您可以通过运行以下命令来安装依赖项：

   .. code-block:: bash

      pip install -r requirements.txt
      pip install Sphinx==8.0.2 pydata-sphinx-theme==0.15.4 Jinja2==3.1.4 sphinx-copybutton==0.5.2
  

2. **使用Sphinx构建**:
    
   * 安装依赖项后，使用sphinx-build命令生成HTML文档。
   * 转到 ``doc/`` 目录并运行：

   .. code-block:: bash

      sphinx-build -b html doc/source doc/_build/html

3. **在本地查看文档**:

   .. code-block:: bash

      python -m http.server -d ./doc/_build/html

   然后在浏览器中打开 "localhost:8000"


发布文档
------------------------

合并到 ``main`` 分支会通过 ``.github/workflows/deploy_doc.yml`` 操作自动生成文档。
这将生成的HTML发布到 ``documentation`` 分支。

1. 在本地查看更改并推送到 ``dev``。

2. 当 ``dev`` 合并到 ``main`` 时，GitHub Actions工作流会自动构建文档。
