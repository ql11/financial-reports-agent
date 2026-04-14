# Pandoc使用指南

## 什么是Pandoc？

Pandoc是一个通用的文档转换工具，被称为"文档转换界的瑞士军刀"。它可以在多种文档格式之间进行转换，包括PDF、Markdown、HTML、Word等。

本项目使用Pandoc将PDF格式的财务报告转换为Markdown格式，以便进行后续的数据提取和分析。

## 安装Pandoc

### Windows系统

#### 方法1：官方安装包
1. 访问 https://pandoc.org/installing.html
2. 下载Windows安装包
3. 运行安装程序，按提示完成安装

#### 方法2：使用Chocolatey
```bash
choco install pandoc
```

#### 方法3：使用Scoop
```bash
scoop install pandoc
```

### macOS系统

#### 使用Homebrew
```bash
brew install pandoc
```

### Linux系统

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install pandoc
```

#### CentOS/RHEL
```bash
sudo yum install pandoc
```

#### Fedora
```bash
sudo dnf install pandoc
```

## 验证安装

安装完成后，验证Pandoc是否正确安装：

```bash
pandoc --version
```

预期输出：
```
pandoc 3.9.0.2
Features: +server +lua
Scripting engine: Lua 5.4
...
```

## Pandoc基本用法

### PDF转Markdown

#### 基本命令
```bash
pandoc input.pdf -f pdf -t markdown -o output.md
```

#### 参数说明
- `-f pdf`：指定输入格式为PDF
- `-t markdown`：指定输出格式为Markdown
- `-o output.md`：指定输出文件名

#### 高级选项
```bash
pandoc input.pdf \
  -f pdf \
  -t markdown \
  -o output.md \
  --wrap=none \                    # 不自动换行
  --markdown-headings=atx \        # 使用ATX风格标题
  --extract-media=./media          # 提取图片到指定目录
```

### 常用转换命令

#### PDF转Markdown（带图片提取）
```bash
pandoc report.pdf -f pdf -t markdown -o report.md --extract-media=./media
```

#### PDF转HTML
```bash
pandoc report.pdf -f pdf -t html -o report.html
```

#### Markdown转PDF
```bash
pandoc report.md -f markdown -t pdf -o report.pdf
```

## 本项目中的Pandoc配置

### 配置文件位置
`config/config.yaml`

### 配置示例
```yaml
pdf:
  converter: pandoc
  pandoc_path: "C:/Program Files/pandoc/pandoc.exe"
  pandoc_options:
    from_format: pdf
    to_format: markdown
    extract_media: false
    media_dir: media
    wrap: none
    markdown_headings: atx
```

### 配置说明
- `converter`：转换工具类型，设置为pandoc
- `pandoc_path`：Pandoc可执行文件路径（如果不在PATH中需要指定）
- `pandoc_options`：Pandoc转换参数
  - `from_format`：输入格式（pdf）
  - `to_format`：输出格式（markdown）
  - `extract_media`：是否提取图片
  - `media_dir`：图片提取目录
  - `wrap`：换行设置（none表示不自动换行）
  - `markdown_headings`：标题风格（atx或setext）

## Pandoc优势

### 相比pdfplumber的优势
1. **更强大的转换能力**：支持复杂的PDF格式
2. **更好的表格识别**：自动识别和转换表格
3. **图片提取**：可以提取PDF中的图片
4. **格式保留**：更好地保留原文档的格式和结构
5. **跨平台**：在所有操作系统上表现一致

### 适用场景
- 复杂格式的PDF文档
- 包含大量表格的文档
- 需要提取图片的文档
- 需要保留原文档结构的场景

## 常见问题

### Q1: Pandoc找不到
**错误信息**：`pandoc: command not found`

**解决方法**：
1. 确认Pandoc已正确安装
2. 将Pandoc添加到系统PATH环境变量
3. 或在配置文件中指定完整路径：
   ```yaml
   pandoc_path: "C:/Program Files/pandoc/pandoc.exe"
   ```

### Q2: PDF转换失败
**错误信息**：`Error reading PDF file`

**可能原因**：
- PDF文件损坏
- PDF文件加密
- PDF格式不支持

**解决方法**：
- 检查PDF文件是否完整
- 尝试使用其他PDF阅读器打开
- 如果是加密PDF，需要先解密

### Q3: 转换后格式混乱
**原因**：PDF格式复杂，自动识别不准确

**解决方法**：
- 尝试不同的Pandoc参数
- 手动调整生成的Markdown文件
- 使用其他PDF工具预处理

### Q4: 中文乱码
**原因**：编码问题

**解决方法**：
- 确保PDF文件使用UTF-8编码
- 使用`--pdf-engine=xelatex`参数（需要安装LaTeX）

## 性能优化

### 批量转换
```bash
# 使用shell脚本批量转换
for file in *.pdf; do
  pandoc "$file" -f pdf -t markdown -o "${file%.pdf}.md"
done
```

### 并行处理
```bash
# 使用GNU parallel并行处理
find . -name "*.pdf" | parallel pandoc {} -f pdf -t markdown -o {.}.md
```

## 进阶用法

### 自定义模板
```bash
pandoc input.pdf -f pdf -t markdown -o output.md --template=custom.template
```

### 使用过滤器
```bash
pandoc input.pdf -f pdf -t markdown -o output.md --filter=filter.lua
```

### 提取元数据
```bash
pandoc input.pdf -f pdf -t markdown --metadata title="财务报告" -o output.md
```

## 相关资源

- **Pandoc官网**：https://pandoc.org/
- **Pandoc手册**：https://pandoc.org/MANUAL.html
- **Pandoc安装指南**：https://pandoc.org/installing.html
- **Pypandoc文档**：https://pypi.org/project/pypandoc/

## 下一步

1. 确认Pandoc已正确安装
2. 测试PDF转Markdown功能
3. 根据需要调整Pandoc参数
4. 开始使用财报分析系统
