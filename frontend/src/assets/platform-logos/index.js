/**
 * 各平台官方Logo配置
 *
 * 使用本地SVG logo文件
 */

// 平台logo文件路径（Vite会自动处理这些导入）
const logoUrls = {
  xhs: new URL('./xiao-hong-shu.svg', import.meta.url).href,
  dy: new URL('./tiktok-1.svg', import.meta.url).href,
  ks: new URL('./kwai-video-platform.svg', import.meta.url).href,
  bili: new URL('./bilibili.svg', import.meta.url).href,
  wb: new URL('./sina-weibo-1.svg', import.meta.url).href,
  tieba: new URL('./baidu-tieba.svg', import.meta.url).href,
  zhihu: new URL('./zhihu-1.svg', import.meta.url).href,
}

/**
 * 获取平台logo URL
 * @param {string} platform - 平台代码
 * @returns {string} logo URL
 */
export function getPlatformLogo(platform) {
  return logoUrls[platform] || ''
}

/**
 * 获取平台品牌颜色
 * @param {string} platform - 平台代码
 * @returns {string} 品牌颜色
 */
export function getPlatformColor(platform) {
  const colors = {
    xhs: '#ff2442',
    dy: '#000000',
    ks: '#ff6600',
    bili: '#fb7299',
    wb: '#e6162d',
    tieba: '#3385ff',
    zhihu: '#0084ff'
  }
  return colors[platform] || '#888888'
}

// 平台名称映射
export const platformNames = {
  xhs: '小红书',
  dy: '抖音',
  ks: '快手',
  bili: 'B站',
  wb: '微博',
  tieba: '贴吧',
  zhihu: '知乎'
}
