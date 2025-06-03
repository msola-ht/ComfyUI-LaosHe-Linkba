import os
import sys
import requests
import json
import re # 导入 re 模块用于正则表达式匹配

# --- 更新配置文件的相关设置 ---
# 远程配置文件的多个备用地址
REMOTE_CONFIG_URLS = [
    "https://raw.githubusercontent.com/msola-ht/ComfyUI-LaosHe-Linkba/main/web/configurable_menu_config.json",
    "https://gitee.com/msolas/ComfyUI-LaosHe-Linkba/raw/main/web/configurable_menu_config.json" # 新增的备用地址
]
LOCAL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "web", "configurable_menu_config.json")
LOCAL_CONFIG_VERSION_PATH = os.path.join(os.path.dirname(__file__), "web", ".config_version")

# --- 更新 update_content.html 的相关设置 ---
# 远程 update_content.html 的多个备用地址
REMOTE_UPDATE_HTML_URLS = [
    "https://raw.githubusercontent.com/msola-ht/ComfyUI-LaosHe-Linkba/main/web/update_content.html",
    "https://gitee.com/msolas/ComfyUI-LaosHe-Linkba/raw/main/web/update_content.html" # 新增的备用地址
]
LOCAL_UPDATE_HTML_PATH = os.path.join(os.path.dirname(__file__), "web", "update_content.html")
LOCAL_UPDATE_HTML_VERSION_PATH = os.path.join(os.path.dirname(__file__), "web", ".update_html_version")

def get_local_version(version_file_path):
    """获取本地版本号"""
    local_version = None
    if os.path.exists(version_file_path):
        try:
            with open(version_file_path, "r", encoding='utf-8') as f:
                local_version = f.read().strip()
        except Exception:
            pass  # 忽略读取错误
    return local_version

def update_file(remote_urls, local_path, local_version_path, file_description):
    """
    通用文件更新函数，支持多个远程地址
    Args:
        remote_urls (list): 远程文件的 URL 列表.
        local_path (str): 本地文件的保存路径.
        local_version_path (str): 存储本地版本号的文件路径.
        file_description (str): 文件的描述，用于日志输出 (例如: "config", "update HTML").
    """
    try:
        # 1. 获取本地版本号
        local_version = get_local_version(local_version_path)

        remote_content = None
        remote_version = None
        fetched_from_url = None

        # 2. 尝试从每个远程地址下载文件
        for url in remote_urls:
            print(f"[ComfyUI-LaosHe-Linkba] Attempting to fetch {file_description} from: {url}")
            try:
                headers = {'User-Agent': 'ComfyUI-Plugin-Updater/1.0'}
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()  # 如果状态码不是 2xx，抛出异常

                remote_content = response.text

                # 3. 尝试从远程内容中提取版本号
                if file_description == "config":
                    try:
                        remote_data = json.loads(remote_content)
                        remote_version = remote_data.get("version")
                        if remote_version is not None:
                             fetched_from_url = url
                             print(f"[ComfyUI-LaosHe-Linkba] Successfully fetched {file_description} from: {url}")
                             break # 成功获取并包含版本信息，停止尝试其他地址
                        else:
                            print(f"[ComfyUI-LaosHe-Linkba] Warning: {file_description} from {url} missing 'version'. Trying next URL.")
                            remote_content = None # 清空数据，继续尝试下一个地址
                    except json.JSONDecodeError:
                        print(f"[ComfyUI-LaosHe-Linkba] Error: Failed to decode JSON from {url} for {file_description}. Trying next URL.")
                        remote_content = None # 清空数据，继续尝试下一个地址

                elif file_description == "update HTML":
                    # 假设版本信息在 HTML 注释中 <!-- version: X.Y.Z -->
                    match = re.search(r"<!--\s*version:\s*([\d\.]+)\s*-->", remote_content)
                    if match:
                        remote_version = match.group(1)
                        fetched_from_url = url
                        print(f"[ComfyUI-LaosHe-Linkba] Successfully fetched {file_description} from: {url}")
                        break # 成功获取并包含版本信息，停止尝试其他地址
                    else:
                         print(f"[ComfyUI-LaosHe-Linkba] Warning: Remote {file_description} from {url} missing version comment (e.g., <!-- version: 1.0.0 -->). Trying next URL.")
                         remote_content = None # 清空数据，继续尝试下一个地址


            except requests.exceptions.Timeout:
                print(f"[ComfyUI-LaosHe-Linkba] Error: Request to {url} timed out for {file_description}. Trying next URL.")
                remote_content = None # 请求超时，继续尝试下一个地址
            except requests.exceptions.RequestException as e:
                print(f"[ComfyUI-LaosHe-Linkba] Error: Failed to fetch from {url} for {file_description} - {e}. Trying next URL.")
                remote_content = None # 请求失败，继续尝试下一个地址
            except Exception as e:
                print(f"[ComfyUI-LaosHe-Linkba] Error: An unexpected error occurred while fetching from {url} for {file_description} - {e}. Trying next URL.")
                remote_content = None # 意外错误，继续尝试下一个地址


        # 4. 检查是否成功获取到有效的远程内容和版本
        if remote_content is None or remote_version is None:
            print(f"[ComfyUI-LaosHe-Linkba] Error: Failed to fetch valid remote {file_description} from all URLs.")
            return # 所有地址都失败，退出更新

        # 5. 检查版本是否更新
        if local_version is not None and str(local_version) == str(remote_version):
            print(f"[ComfyUI-LaosHe-Linkba] {file_description} is up-to-date (v{local_version}).")
            return  # Version is the same, no update needed

        # 6. 执行更新
        print(f"[ComfyUI-LaosHe-Linkba] Updating {file_description} (local v{local_version or 'unknown'} -> remote v{remote_version}) from {fetched_from_url}.")
        web_dir = os.path.dirname(local_path)
        if not os.path.exists(web_dir):
            os.makedirs(web_dir)

        # 保存文件内容
        with open(local_path, "w", encoding='utf-8') as f:
            f.write(remote_content)

        # 保存新的版本号
        with open(local_version_path, "w", encoding='utf-8') as f:
            f.write(str(remote_version))

        print(f"[ComfyUI-LaosHe-Linkba] {file_description} updated successfully to v{remote_version}.")

    except Exception as e:
        print(f"[ComfyUI-LaosHe-Linkba] Error: An unexpected error occurred during {file_description} update process - {e}")

def update_plugin_files():
    """更新插件所需的文件 (配置和HTML)"""
    print("[ComfyUI-LaosHe-Linkba] Checking for updates...")
    # 更新配置文件，使用多个地址
    update_file(REMOTE_CONFIG_URLS, LOCAL_CONFIG_PATH, LOCAL_CONFIG_VERSION_PATH, "config")
    # 更新 update_content.html，使用多个地址
    update_file(REMOTE_UPDATE_HTML_URLS, LOCAL_UPDATE_HTML_PATH, LOCAL_UPDATE_HTML_VERSION_PATH, "update HTML")
    print("[ComfyUI-LaosHe-Linkba] Update check finished.")


# --- ComfyUI 插件注册部分 ---
WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "web")

EXTENSION_WEB_DIRS = {
    "ComfyUI-LaosHe-Linkba": WEB_DIRECTORY
}

# --- 在 ComfyUI 启动时调用更新函数 ---
update_plugin_files()

# --- 其他可能的节点定义 ---
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
