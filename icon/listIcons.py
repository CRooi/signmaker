import os
import json

def list_svg_with_prefix():
    current_dir = os.getcwd()
    
    # 在 f 前面加上 "icons/" 拼接
    svg_files = [f"icons/{f}" for f in os.listdir(current_dir) if f.lower().endswith('.svg')]
    
    # 转换为 JSON 
    json_output = json.dumps(svg_files, ensure_ascii=False, indent=2)
    print(json_output)

if __name__ == "__main__":
    list_svg_with_prefix()