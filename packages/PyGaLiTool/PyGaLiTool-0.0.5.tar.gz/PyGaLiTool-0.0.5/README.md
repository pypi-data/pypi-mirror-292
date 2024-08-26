
```
# 前置安装twine
python -m pip install --upgrade twine
```

```
# 检查
python setup.py check

# 打包
python setup.py sdist bdist_wheel

# 上传
twine upload dist/*
```

```shell
# 安装使用
pip install PyGaLiTool
pip install PyGaLiTool==0.0.3
```

```python
# 使用方式
from pygali.date_utils import cur_date
print(cur_date())
```