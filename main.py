import os
import sys
import random
from PIL import Image, ImageDraw, ImageFont

# 获取资源文件的绝对路径(兼容PyInstaller打包)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 配置参数
FONT_PATH = resource_path("fonts/ChillDuanHeiSongPro_Regular.otf")

# 水印颜色选项
COLORS = {
    "红色": "#FF0000",
    "黄色": "#FFFF00",
    "绿色": "#00FF00",
    "橙色": "#FFA500"
}

# 水印位置
POSITION_MAP = {
    '1': '左上角',
    '2': '右上角',
    '3': '左下角',
    '4': '右下角',
    '5': '中央'
}

SUPPORTED_EXT = ('png', 'jpg', 'jpeg', 'webp', 'tiff')

def get_optimal_font_size(img_width, img_height):
    diagonal = (img_width**2 + img_height**2)**0.5
    font_size = int(diagonal * 0.03)
    return max(40, min(font_size, 300))

def calculate_position(position_key, image_width, image_height, text_width, text_height):
    padding = 10
    
    if position_key == '1':  # 左上角
        return padding, padding
    elif position_key == '2':  # 右上角
        return image_width - text_width - padding, padding
    elif position_key == '3':  # 左下角
        return padding, image_height - text_height - padding
    elif position_key == '4':  # 右下角
        return image_width - text_width - padding, image_height - text_height - padding
    elif position_key == '5':  # 中央
        return (image_width - text_width) // 2, (image_height - text_height) // 2
    else:
        return padding, image_height - text_height - padding

def get_random_position():
    """返回随机位置"""
    return random.choice(list(POSITION_MAP.keys()))

def get_random_color():
    """返回随机颜色"""
    return random.choice(list(COLORS.values()))

def process_images(input_dir, output_dir, watermark_text, position, color, same_folder_same_color=True):
    if not os.path.exists(FONT_PATH):
        print(f"错误: 字体文件不存在: {FONT_PATH}")
        return 0, 0
        
    processed = 0
    errors = 0
    
    # 确保字体加载成功
    try:
        font_base = ImageFont.truetype(FONT_PATH, 100)
    except Exception as e:
        print(f"字体加载失败: {e}")
        font_base = ImageFont.load_default()
    
    # 为每个文件夹预先分配颜色
    folder_colors = {}
    
    # 获取所有子文件夹
    for root, _, files in os.walk(input_dir):
        if any(os.path.splitext(f)[1].lower().lstrip('.') in SUPPORTED_EXT for f in files):
            rel_folder = os.path.relpath(root, input_dir)
            folder_colors[rel_folder] = get_random_color()
    
    # 处理所有图片文件
    for root, _, files in os.walk(input_dir):
        # 获取当前文件夹的相对路径
        rel_folder = os.path.relpath(root, input_dir)
        
        # 为当前文件夹选择一个颜色(如果启用了同文件夹同颜色且是随机颜色模式)
        folder_color = folder_colors.get(rel_folder) if same_folder_same_color and color == 'random' else None
        
        # 过滤出支持的图片文件
        image_files = [f for f in files if os.path.splitext(f)[1].lower().lstrip('.') in SUPPORTED_EXT]
        
        if not image_files:
            continue
            
        print(f"\n处理文件夹: {rel_folder}")
        
        # 如果使用同文件夹同颜色，显示该文件夹使用的颜色
        if same_folder_same_color and color == 'random' and folder_color:
            color_name = [k for k, v in COLORS.items() if v == folder_color]
            color_display = color_name[0] if color_name else folder_color
            print(f"文件夹颜色: {color_display}")
        
        for file in image_files:
            src_path = os.path.join(root, file)
            rel_path = os.path.join(rel_folder, file) if rel_folder != '.' else file
            dst_dir = os.path.join(output_dir, os.path.dirname(rel_path))
            dst_path = os.path.join(output_dir, rel_path)
            
            # 创建输出目录
            os.makedirs(dst_dir, exist_ok=True)
            
            try:
                # 打开并处理图片
                with Image.open(src_path) as img:
                    # 创建副本以避免修改原图
                    img_copy = img.copy()
                    draw = ImageDraw.Draw(img_copy)
                    
                    # 计算字体大小
                    font_size = get_optimal_font_size(img.width, img.height)
                    font = ImageFont.truetype(FONT_PATH, font_size)
                    
                    # 获取位置和颜色
                    pos_key = position
                    
                    # 设置文本颜色，优先使用文件夹颜色(如果有的话)
                    if same_folder_same_color and color == 'random' and folder_color:
                        text_color = folder_color
                    else:
                        text_color = color
                        if color == 'random':
                            text_color = get_random_color()
                    
                    # 如果设置为随机位置，则为每张图片生成随机位置
                    if position == 'random':
                        pos_key = get_random_position()
                    
                    # 获取文本大小
                    try:
                        bbox = draw.textbbox((0, 0), watermark_text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                    except:
                        # 兼容旧版PIL
                        text_width, text_height = draw.textsize(watermark_text, font=font)
                    
                    # 计算位置
                    x, y = calculate_position(pos_key, img.width, img.height, 
                                             text_width, text_height)
                    
                    # 绘制水印
                    draw.text((x, y), watermark_text, fill=text_color, font=font)
                    
                    # 保存图片
                    img_copy.save(dst_path)
                    processed += 1
                    
                    # 获取位置和颜色的名称，用于显示
                    pos_name = POSITION_MAP.get(pos_key, '未知')
                    color_name = [k for k, v in COLORS.items() if v == text_color]
                    color_display = color_name[0] if color_name else text_color
                    
                    print(f"完成: {rel_path} (位置: {pos_name}, 颜色: {color_display})")
            except Exception as e:
                print(f"错误: {rel_path} - {str(e)}")
                errors += 1
    
    return processed, errors

def pause():
    """替代input函数，避免stdin错误"""
    try:
        # 检查是否在终端环境
        if sys.stdin and sys.stdin.isatty():
            input("按回车键退出...")
        else:
            import time
            print("\n程序将在5秒后自动关闭...")
            time.sleep(5)
    except:
        import time
        time.sleep(5)

def main():
    # 显示帮助信息
    if len(sys.argv) <= 1 or sys.argv[1] in ['-h', '--help']:
        print("\n图片水印添加工具")
        print("用法: 图片水印工具.exe 输入目录 [水印文字] [位置] [颜色] [同文件夹同颜色]")
        print("位置: 1=左上角, 2=右上角, 3=左下角, 4=右下角, 5=中央, random=随机(默认)")
        print("颜色: red=红色, yellow=黄色, green=绿色, orange=橙色, random=随机(默认)")
        print("同文件夹同颜色: yes=是(默认), no=否")
        pause()
        return
    
    # 获取参数    
    input_dir = sys.argv[1]
    watermark_text = sys.argv[2] if len(sys.argv) > 2 else "默认水印"
    position = sys.argv[3].lower() if len(sys.argv) > 3 else 'random'  # 默认随机位置
    
    # 颜色映射
    color_map = {
        'red': "#FF0000",
        'yellow': "#FFFF00", 
        'green': "#00FF00",
        'orange': "#FFA500",
        'random': 'random'
    }
    
    # 获取颜色参数，默认随机
    color = color_map.get(sys.argv[4].lower() if len(sys.argv) > 4 else 'random', 'random')
    
    # 获取是否同文件夹同颜色参数
    same_folder_same_color = True  # 默认开启
    if len(sys.argv) > 5:
        if sys.argv[5].lower() in ['no', 'false', '0', 'n']:
            same_folder_same_color = False
    
    # 验证参数
    if not os.path.isdir(input_dir):
        print(f"错误: 输入目录 '{input_dir}' 不存在!")
        pause()
        return
    
    # 创建输出目录
    dir_name = os.path.basename(os.path.normpath(input_dir))
    output_dir = os.path.join(os.path.dirname(input_dir), f"{dir_name}_{watermark_text}")
    os.makedirs(output_dir, exist_ok=True)
    
    # 显示设置
    pos_display = "随机" if position == 'random' else POSITION_MAP.get(position, "未知")
    color_display = "随机" if color == 'random' else [k for k, v in COLORS.items() if v == color][0]
    
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"水印文字: {watermark_text}")
    print(f"水印位置: {pos_display}")
    print(f"水印颜色: {color_display}")
    print(f"同文件夹同颜色: {'是' if same_folder_same_color else '否'}")
    
    # 处理图片
    processed, errors = process_images(input_dir, output_dir, watermark_text, position, color, same_folder_same_color)
    
    print(f"\n处理完成: {processed} 个文件已添加水印, {errors} 个文件处理失败")
    pause()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序错误: {str(e)}")
        pause()