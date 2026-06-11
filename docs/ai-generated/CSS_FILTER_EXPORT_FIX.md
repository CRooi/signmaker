# CSS Filter 导出修复说明（v2）

## 问题描述

在导出 PNG / SVG 图片时，应用在图标上的 CSS `filter` 属性（例如用于反白效果的 `brightness(0) invert(1)`）会失效，导致导出的图标恢复为原始的黑色而非预期的白色。

## 根本原因分析

### 1. html2canvas 库的限制
- `html2canvas` 不支持 CSS `filter` 属性，渲染时直接忽略

### 2. 第一版修复为何失败
第一版方案试图模拟 CSS filter 的像素运算（grayscale → invert），但存在以下问题：

1. **Alpha 通道处理错误**：CSS `brightness(0) invert(1)` 不仅反转 RGB，还会反转 Alpha 通道（transparent → opaque），导致透明背景变为不透明白色。在导出场景中（图标叠加在 zone 深色背景上），这会产生一个白色矩形覆盖 zone 背景
2. **Canvas 污染风险**：从 Blob URL 加载的 SVG 绘制到 Canvas 后，`getImageData()` 可能在部分浏览器中触发 SecurityError，被 try-catch 静默吞掉，图标保持原样
3. **灰度计算公式冗余**：对已经是黑色的图标做灰度→反转运算，等价于直接设为白色，但增加了不必要的计算和潜在精度损失

### 3. SVG 导出中 fill 覆盖问题
即使设置了 `<g fill="#ffffff">`，SVG 内联内容中每个 `<path fill="#000000">` 的**显式 fill 属性会覆盖父 `<g>` 的 fill**（SVG 规范：后代元素的属性优先于祖先继承），导致形状仍为黑色

## 修复方案（v2）

### 核心思路
**不再模拟 CSS filter 的亮度/反转运算，而是直接将图标的非透明像素设为白色，保留原始 alpha 通道。**

### PNG 导出修复

新增 `_createWhiteIconDataURL(src, displayW, displayH)` 辅助函数，采用两层策略：

#### 策略 A：SVG 源码直接操作（优先，最可靠）
```javascript
// 解析 SVG，将所有非透明 fill 改为白色
svgEl.querySelectorAll('*').forEach(el => {
    const fillAttr = el.getAttribute('fill');
    if (fillAttr && fillAttr !== 'none') {
        el.setAttribute('fill', '#ffffff');
    }
    if (el.style.fill && el.style.fill !== 'none') el.style.fill = '#ffffff';
    if (el.style.color) el.style.color = '#ffffff';
});
svgEl.setAttribute('fill', '#ffffff'); // 根级默认 fill
```
- 直接修改 SVG 的 fill 属性，不依赖 Canvas
- 生成的 data URL 是纯 SVG，html2canvas 能正确渲染
- 保留 `fill="none"`（用于透明镂空区域）

#### 策略 B：Canvas 像素白化（回退方案）
```javascript
// 将所有非透明像素的 RGB 强制设为白色
for (let i = 0; i < data.length; i += 4) {
    if (data[i + 3] > 0) {  // alpha > 0
        data[i] = 255;     // R
        data[i + 1] = 255; // G
        data[i + 2] = 255; // B
        // alpha 保持不变
    }
}
```
- 适用于位图图标或 SVG 操作失败的情况
- 设置 `crossOrigin = 'anonymous'` 避免 Canvas 污染
- 使用高分辨率（scale ≥ 2）确保导出质量

### SVG 导出修复

在检测到 `brightness(0) invert(1)` 滤镜时，**剥离内联 fill 属性**：
```javascript
if (filterValue.includes('brightness(0)') && filterValue.includes('invert(1)')) {
    iconFill = '#ffffff';
    // 剥离子元素的显式 fill（保留 fill="none"）
    innerContent = innerContent.replace(/\sfill="(?!none")[^"]*"/gi, '');
    // 剥离 inline style 中的 fill 和 color
    innerContent = innerContent.replace(/style="([^"]*)"/gi, (match, styleContent) => {
        const cleaned = styleContent
            .replace(/fill\s*:\s*[^;]+;?\s*/gi, '')
            .replace(/color\s*:\s*[^;]+;?\s*/gi, '')
            .trim();
        return cleaned ? `style="${cleaned}"` : '';
    });
}
```
- 确保 `<g fill="#ffffff">` 能正确继承到所有子元素
- 保留 `fill="none"` 以维持镂空/透明区域

## 修改文件清单

| 文件 | 行号范围 | 修改内容 |
|------|---------|---------|
| index.html | ~2735-2821 | 新增 `_createWhiteIconDataURL` 辅助函数 |
| index.html | ~2842 | `iconRestoreData` 声明移到 try/catch 外层 |
| index.html | ~2884-2910 | PNG 导出图标处理循环（精简版） |
| index.html | ~2944-2948 | 正常流程恢复图标状态 |
| index.html | ~3073-3077 | 异常流程恢复图标状态 |
| index.html | ~3189-3202 | SVG 导出：剥离内联 fill + 设置白色 |

## 与 v1 方案的关键区别

| 维度 | v1（失败） | v2（当前） |
|------|-----------|-----------|
| SVG 图标处理 | fetch → Blob → Canvas → 像素操作 | fetch → DOMParser → 修改 fill → data URL |
| 像素算法 | grayscale + invert（模拟 CSS filter） | 直接设为白色（`RGB = 255,255,255`） |
| Alpha 处理 | 保留原始 alpha（但 filter 会反转 alpha） | 保留原始 alpha（导出需要透明背景） |
| Canvas 污染 | 可能被 tainted（Blob URL） | SVG 路径不经过 Canvas；位图用 crossOrigin |
| SVG 导出 | 仅设 `<g fill="white">`，未剥离子元素 fill | 同时剥离子元素 fill 属性 |
| 错误恢复 | iconRestoreData 在 try 内声明，catch 无法访问 | 声明移到 try/catch 外层 |
