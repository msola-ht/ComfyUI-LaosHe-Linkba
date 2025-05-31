import os
import sys

# 获取当前文件所在的目录路径
NODE_PATH = os.path.join(os.path.dirname(__file__))
# 获取 web 目录的路径
WEB_DIRECTORY = os.path.join(NODE_PATH, "web")

print(f"\n[ComfyUI-LaosHe-Linkba] Loading web files from: {WEB_DIRECTORY}")

# 设置 EXTENSION_WEB_DIRS 字典，将插件的名称映射到 web 目录路径
EXTENSION_WEB_DIRS = {
    "ComfyUI-LaosHe-Linkba": WEB_DIRECTORY  # <-- 确保这里是您的插件文件夹名称
}

# ... 其他可能的节点定义（如果需要）
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

print("[ComfyUI-LaosHe-Linkba] Plugin loaded successfully.")
