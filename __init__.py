import os
import sys
import requests
import json

# --- 更新配置文件的相关设置 ---
REMOTE_CONFIG_URL = "https://raw.githubusercontent.com/msola-ht/ComfyUI-LaosHe-Linkba/main/web/configurable_menu_config.json"
NODE_PATH = os.path.join(os.path.dirname(__file__))
LOCAL_CONFIG_PATH = os.path.join(NODE_PATH, "web", "configurable_menu_config.json")
LOCAL_VERSION_PATH = os.path.join(NODE_PATH, "web", ".config_version")

def update_config_file():
    try:
        # 1. 获取本地版本号
        local_version = None
        if os.path.exists(LOCAL_VERSION_PATH):
            try:
                with open(LOCAL_VERSION_PATH, "r", encoding='utf-8') as f:
                    local_version = f.read().strip()
            except Exception:
                pass # Ignore read errors silently

        # 2. 从远程下载配置文件
        headers = {'User-Agent': 'ComfyUI-Plugin-Updater/1.0'}
        response = requests.get(REMOTE_CONFIG_URL, headers=headers, timeout=15)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        try:
            remote_config_data = response.json()
        except json.JSONDecodeError:
            print(f"[ComfyUI-LaosHe-Linkba] Error: Failed to decode remote config JSON.")
            return

        # 3. 获取远程版本号
        remote_version = remote_config_data.get("version")
        if remote_version is None:
            print(f"[ComfyUI-LaosHe-Linkba] Warning: Remote config file missing 'version'.")
            return # Skip update if remote version is missing

        # 4. 检查版本是否更新
        if local_version is not None and str(local_version) == str(remote_version): # 确保比较类型一致
            print(f"[ComfyUI-LaosHe-Linkba] Config is up-to-date (v{local_version}).") # 打印当前版本信息
            return # Version is the same, no update needed

        # 5. 执行更新
        print(f"[ComfyUI-LaosHe-Linkba] Updating config (local v{local_version or 'unknown'} -> remote v{remote_version}).") # 打印更新信息
        web_dir = os.path.dirname(LOCAL_CONFIG_PATH)
        if not os.path.exists(web_dir):
            os.makedirs(web_dir)

        with open(LOCAL_CONFIG_PATH, "w", encoding='utf-8') as f:
            json.dump(remote_config_data, f, indent=4)

        with open(LOCAL_VERSION_PATH, "w", encoding='utf-8') as f:
            f.write(str(remote_version))

        print(f"[ComfyUI-LaosHe-Linkba] Config updated successfully to v{remote_version}.") # 打印更新成功信息

    except requests.exceptions.Timeout:
        print(f"[ComfyUI-LaosHe-Linkba] Error: Request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"[ComfyUI-LaosHe-Linkba] Error: Failed to fetch remote config - {e}")
    except Exception as e:
        print(f"[ComfyUI-LaosHe-Linkba] Error: An unexpected error occurred - {e}")


# --- ComfyUI 插件注册部分 ---
WEB_DIRECTORY = os.path.join(NODE_PATH, "web")

EXTENSION_WEB_DIRS = {
    "ComfyUI-LaosHe-Linkba": WEB_DIRECTORY
}

# --- 在 ComfyUI 启动时调用更新函数 ---
update_config_file()

# --- 其他可能的节点定义 ---
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
