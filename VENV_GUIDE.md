# Python虚拟环境使用指南

## 虚拟环境已创建

项目已创建专用的Python虚拟环境，位于 `venv/` 目录。

## 激活虚拟环境

### Windows系统

#### 方法1：使用批处理脚本
```bash
activate_venv.bat
```

#### 方法2：手动激活
```bash
venv\Scripts\activate
```

### Linux/macOS系统

#### 方法1：使用Shell脚本
```bash
source activate_venv.sh
```

#### 方法2：手动激活
```bash
source venv/bin/activate
```

## 验证虚拟环境

激活后，命令行提示符前会显示 `(venv)` 标识。

验证命令：
```bash
# 检查Python路径
which python  # Linux/macOS
where python  # Windows

# 检查Python版本
python --version

# 检查pip版本
pip --version
```

## 安装依赖包

虚拟环境激活后，安装项目依赖：
```bash
pip install -r requirements.txt
```

## 退出虚拟环境

```bash
deactivate
```

## 虚拟环境信息

- **Python版本**：3.12.10
- **虚拟环境路径**：`./venv/`
- **pip版本**：26.0.1（已升级到最新）

## 常见问题

### Q1: 激活失败
**原因**：执行策略限制（Windows）
**解决**：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q2: 依赖包安装失败
**原因**：网络问题或包版本冲突
**解决**：
- 使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 逐个安装：`pip install package_name`

### Q3: 虚拟环境损坏
**原因**：文件损坏或路径变更
**解决**：
```bash
# 删除虚拟环境
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# 重新创建
python -m venv v