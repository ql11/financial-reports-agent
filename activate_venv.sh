#!/bin/bash
echo "激活Python虚拟环境..."
source venv/Scripts/activate
echo "虚拟环境已激活！"
echo "Python版本："
python --version
echo ""
echo "pip版本："
pip --version
echo ""
echo "如需安装依赖包，请运行："
echo "pip install -r requirements.txt"
echo ""
