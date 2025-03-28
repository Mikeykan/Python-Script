# -*- coding: utf-8 -*-
import subprocess
import os
from datetime import datetime

# 配置参数
INPUT_FILE = 'ip.txt'             # 输入IP文件
OUTPUT_DIR = 'results'            # 输出目录
ERROR_LOG = 'error.log'           # 错误日志文件
KUBECTL_PATH = 'kubectl.exe'      # kubectl路径
TIMEOUT = 15                      # 命令超时时间（秒）

def ensure_dir_exists(directory):
    """确保输出目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def sanitize_filename(ip):
    """将IP:PORT转换为安全文件名"""
    return ip.replace(':', '_').replace('/', '_')

def process_ip(ip):
    """处理单个IP地址"""
    try:
        # 构造命令
        cmd = [KUBECTL_PATH, '-s', ip, 'get', 'nodes', '--output=wide']
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        
        # 处理结果
        if result.returncode == 0:
            # 生成输出文件名
            filename = f"{sanitize_filename(ip)}_nodes.txt"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            # 写入结果文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Scan results for {ip} at {datetime.now()}\n")
                f.write(result.stdout)
            
            print(f"[SUCCESS] {ip} 扫描完成")
            return True
        else:
            error_msg = f"命令执行失败 (code {result.returncode}): {result.stderr.strip()}"
            log_error(ip, error_msg)
            return False
            
    except subprocess.TimeoutExpired:
        error_msg = f"命令执行超时 ({TIMEOUT}s)"
        log_error(ip, error_msg)
        return False
    except Exception as e:
        error_msg = f"意外错误: {str(e)}"
        log_error(ip, error_msg)
        return False

def log_error(ip, message):
    """记录错误信息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {ip} - {message}\n"
    print(f"[ERROR] {log_entry.strip()}")
    
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def main():
    ensure_dir_exists(OUTPUT_DIR)
    
    # 读取IP列表
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            ips = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {INPUT_FILE}")
        return

    print(f"开始扫描，共 {len(ips)} 个IP需要处理...")
    
    # 处理每个IP
    success_count = 0
    for ip in ips:
        if process_ip(ip):
            success_count += 1

    print("\n扫描完成！")
    print(f"成功: {success_count}")
    print(f"失败: {len(ips) - success_count}")
    print(f"详细结果请查看 {OUTPUT_DIR} 目录")
    print(f"错误日志请查看 {ERROR_LOG}")

if __name__ == "__main__":
    main()
