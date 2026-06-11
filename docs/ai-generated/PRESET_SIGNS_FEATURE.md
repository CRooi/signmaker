# 预设标牌功能实现说明

## 功能概述

预设标牌功能允许用户快速加载预定义的标牌模板到画布中，无需从头开始设计。

## 文件结构

```
components/
├── presets.json                    # 预设标牌元数据配置
└── presets/                        # 预设标牌数据目录
    ├── station_name_01.json       # 站名标牌示例
    ├── exit_info_01.json          # 出口信息标牌示例
    └── facility_01.json           # 设施导向标牌示例

icon/thumbnail/presets/             # 预设标牌缩略图目录
├── station_name_01.svg            # 站名标牌缩略图
├── exit_info_01.svg               # 出口信息标牌缩略图
└── facility_01.svg                # 设施导向标牌缩略图
```

## 核心实现

### 1. UI 结构

- **面板切换**：复用 `.savedFileTypeSelector` 容器，包含两个按钮
  - "已保存标牌"（默认激活）
  - "预设标牌"
  
- **面板互斥**：
  - `.savedFilePanel` - 显示已保存的标牌
  - `.presetSignsPanel` - 显示预设标牌
  - 点击不同按钮时切换显示，保持互斥状态

### 2. 数据结构

**presets.json 格式：**
```json
[
  {
    "id": "station_name_01",
    "title": "标准站名标牌",
    "type": "enter",
    "author": "Chitose.City",
    "thumbnail": "icon/thumbnail/presets/station_name_01.svg",
    "dataFile": "presets/station_name_01.json"
  }
]
```

**预设数据文件格式：**
与 `deserializeCanvas()` 兼容的 JSON 结构，包含 canvas 配置和 zones 数组。

### 3. 核心函数

#### `loadPresetSignsConfig()`
- 页面初始化时调用
- 从 `./components/presets.json` 加载预设列表
- 存储到全局变量 `presetSignsConfig`

#### `renderPresetSignsList()`
- 渲染预设标牌列表到 `.presetSignsList`
- 为每个预设创建卡片（`.presetCard`）
- 显示预览图、标题、类型、作者和使用按钮

#### `createPresetCard(preset)`
- 创建单个预设卡片 DOM 元素
- 包含：
  - `<img class="presetThumbnail">` - 预览图
  - 标题和元数据
  - "使用"按钮（无删除按钮）

#### `loadPresetToCanvas(preset)`
- 异步加载预设数据文件
- 调用 `deserializeCanvas()` 将预设加载到画布
- 关闭预设面板，显示组件面板
- 错误处理和用户确认

### 4. 样式设计

**预设卡片样式（`.presetCard`）：**
- 参考 `.savedFileCard` 的设计
- 包含 120px 高度的预览图区域
- Hover 效果：背景色变化和边框高亮
- 移除删除按钮，仅保留"使用"按钮

**面板样式（`.presetSignsPanel`）：**
- 与 `.savedFilePanel` 完全一致的结构
- 默认隐藏，通过 `.active` 类控制显示

### 5. 交互流程

1. **打开预设面板**：
   - 点击工具栏的"已保存文件"按钮
   - 默认显示"已保存标牌"面板

2. **切换到预设标牌**：
   - 点击"预设标牌"按钮
   - 按钮状态更新（active 类切换）
   - 面板切换显示
   - 自动渲染预设列表

3. **加载预设到画布**：
   - 点击预设卡片的"使用"按钮
   - 弹出确认对话框
   - 确认后加载预设数据
   - 关闭面板，返回编辑界面

### 6. 扩展预设

**添加新预设的步骤：**

1. 在 `components/presets/` 创建数据文件（如 `my_preset.json`）
2. 准备缩略图并放到 `icon/thumbnail/presets/`
3. 在 `components/presets.json` 中添加元数据条目
4. 刷新页面即可看到新预设

**示例：**
```json
{
  "id": "my_custom_preset",
  "title": "我的自定义标牌",
  "type": "enter",
  "author": "Your Name",
  "thumbnail": "icon/thumbnail/presets/my_custom_preset.svg",
  "dataFile": "presets/my_custom_preset.json"
}
```

## 注意事项

1. **缩略图回退**：如果缩略图加载失败，会自动使用 `icon/thumbnail/default.svg`
2. **错误处理**：预设文件缺失或解析失败时会在控制台报错并提示用户
3. **数据兼容性**：预设数据格式必须与 `deserializeCanvas()` 兼容
4. **面板状态**：切换面板时会正确更新按钮的 active 状态

## 相关文件

- **HTML**: `index.html` (L29-46, L3084-3175)
- **CSS**: `global.css` (L326-340, L450-543)
- **JavaScript**: `index.html` (L2442-2538)
- **配置**: `components/presets.json`
- **数据**: `components/presets/*.json`
