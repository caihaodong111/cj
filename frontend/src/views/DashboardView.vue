<template>
  <div class="dashboard-wrapper">
    <div class="ambient-background">
      <div class="nebula blue"></div>
      <div class="nebula gold"></div>
      <div class="breathing-line gold-1"></div>
      <div class="breathing-line gold-2"></div>
      <div class="scan-grid"></div>
      <div class="particles">
        <div class="particle" v-for="i in 8" :key="i" :style="{ animationDelay: `${i * 1.5}s` }"></div>
      </div>
    </div>

    <div class="layout-wrapper">
      <header class="page-header entrance-slide-in">
        <div class="title-group">
          <h1 class="ios-title">舆情监测总览<span class="subtitle">Sentiment Dashboard</span></h1>
          <div class="status-tag">
            <span class="dot pulse"></span> 最近更新：{{ lastUpdatedAt ? formatRelativeTime(lastUpdatedAt) : '暂无' }}
          </div>
        </div>
      </header>

      <div class="dashboard-main-grid">
        <aside class="side-panel left">
          <div class="panel-card ios-glass main-card entrance-scale-up">
            <div class="border-glow entrance-border-glow"></div>
            <div class="cell-header">
              <span class="accent-bar"></span>
              各平台敏感数据分布
            </div>
            <div ref="mainChartRef" class="main-chart-box entrance-chart-fade"></div>
          </div>

          <div class="sentiment-grid">
            <div class="platform-card ios-glass entrance-scale-up clickable" style="animation-delay: 0.3s" @click="handlePlatformJump('xhs')">
              <div class="border-glow entrance-border-glow"></div>
              <div class="cell-header compact">
                <span class="accent-bar small"></span>
                小红书
              </div>
              <div class="platform-chart-wrapper">
                <div class="platform-mini-chart" :ref="el => setChartRef('xhs', el)"></div>
              </div>
            </div>
            <div class="platform-card ios-glass entrance-scale-up clickable" style="animation-delay: 0.35s" @click="handlePlatformJump('dy')">
              <div class="border-glow entrance-border-glow"></div>
              <div class="cell-header compact">
                <span class="accent-bar small"></span>
                抖音
              </div>
              <div class="platform-chart-wrapper">
                <div class="platform-mini-chart" :ref="el => setChartRef('dy', el)"></div>
              </div>
            </div>
            <div class="platform-card ios-glass entrance-scale-up clickable" style="animation-delay: 0.4s" @click="handlePlatformJump('ks')">
              <div class="border-glow entrance-border-glow"></div>
              <div class="cell-header compact">
                <span class="accent-bar small"></span>
                快手
              </div>
              <div class="platform-chart-wrapper">
                <div class="platform-mini-chart" :ref="el => setChartRef('ks', el)"></div>
              </div>
            </div>
            <div class="platform-card ios-glass entrance-scale-up clickable" style="animation-delay: 0.45s" @click="handlePlatformJump('bili')">
              <div class="border-glow entrance-border-glow"></div>
              <div class="cell-header compact">
                <span class="accent-bar small"></span>
                B站
              </div>
              <div class="platform-chart-wrapper">
                <div class="platform-mini-chart" :ref="el => setChartRef('bili', el)"></div>
              </div>
            </div>
            <div class="platform-card ios-glass entrance-scale-up clickable" style="animation-delay: 0.5s" @click="handlePlatformJump('wb')">
              <div class="border-glow entrance-border-glow"></div>
              <div class="cell-header compact">
                <span class="accent-bar small"></span>
                微博
              </div>
              <div class="platform-chart-wrapper">
                <div class="platform-mini-chart" :ref="el => setChartRef('wb', el)"></div>
              </div>
            </div>
            <div class="platform-card ios-glass entrance-scale-up clickable" style="animation-delay: 0.55s" @click="handlePlatformJump('tieba')">
              <div class="border-glow entrance-border-glow"></div>
              <div class="cell-header compact">
                <span class="accent-bar small"></span>
                贴吧
              </div>
              <div class="platform-chart-wrapper">
                <div class="platform-mini-chart" :ref="el => setChartRef('tieba', el)"></div>
              </div>
            </div>
            <div class="platform-card ios-glass entrance-scale-up clickable" style="animation-delay: 0.6s" @click="handlePlatformJump('zhihu')">
              <div class="border-glow entrance-border-glow"></div>
              <div class="cell-header compact">
                <span class="accent-bar small"></span>
                知乎
              </div>
              <div class="platform-chart-wrapper">
                <div class="platform-mini-chart" :ref="el => setChartRef('zhihu', el)"></div>
              </div>
            </div>
          </div>
        </aside>

        <section class="center-panel">
          <div class="recent-list ios-glass compact entrance-scale-up-delay-2 feed-panel">
            <div class="border-glow purple-tint entrance-border-glow"></div>
            <div class="cell-header">
              <span class="accent-bar purple"></span>
              Monitor Feed 实时动态
              <button class="refresh-btn header-refresh" :disabled="feedLoading" @click="refreshMonitorFeed">
                <span class="refresh-icon" :class="{ spinning: feedLoading }">⟳</span>
                {{ feedLoading ? '刷新中' : '刷新' }}
              </button>
            </div>

            <div v-if="feedItems && feedItems.length > 0" class="list-wrapper">
              <div class="list-item" v-for="(item, index) in feedItems" :key="item.id" :class="getSentimentClass(item.sentiment)">
                <span class="platform-tag">{{ item.platformLabel }}</span>
                <span class="content">{{ item.content }}</span>
                <span class="sentiment-tag" :class="item.sentiment || 'neutral'">
                  {{ getSentimentLabel(item.sentiment) }}
                </span>
                <span class="time">{{ item.timeLabel }}</span>
                <span class="author" :class="{ muted: !item.authorLabel }">
                  {{ item.authorLabel || '匿名' }}
                </span>
              </div>
            </div>

            <div v-else-if="feedLoading" class="feed-state">
              <div class="loading-spinner"></div>
              <p>正在获取最新动态...</p>
            </div>

            <div v-else class="feed-state">
              <p>暂无数据动态</p>
              <p class="hint">请先在数据采集界面生成数据</p>
            </div>

            <div v-if="feedItems && feedItems.length > 0" class="pagination-wrapper centered">
              <div class="pagination-controls">
                <button
                  class="pagination-btn icon-btn"
                  :disabled="currentPage === 1"
                  @click="goToPage(currentPage - 1)"
                  title="上一页"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="15 18 9 12 15 6"></polyline>
                  </svg>
                </button>
                <select
                  class="page-size-select"
                  :value="pageSize"
                  @change="setPageSize(Number($event.target.value))"
                >
                  <option :value="50">50条/页</option>
                  <option :value="100">100条/页</option>
                </select>
                <div class="pagination-numbers">
                  <button
                    v-for="page in displayedPages"
                    :key="page"
                    class="pagination-number"
                    :class="{ active: page === currentPage, ellipsis: page === '...' }"
                    :disabled="page === '...'"
                    @click="page !== '...' && goToPage(page)"
                  >
                    {{ page }}
                  </button>
                </div>
                <button
                  class="pagination-btn icon-btn"
                  :disabled="currentPage === totalPages"
                  @click="goToPage(currentPage + 1)"
                  title="下一页"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <div v-if="sensitiveModalOpen" class="modal-overlay" @click.self="closeSensitiveModal">
      <div class="modal-card ios-glass">
        <div class="border-glow purple-tint entrance-border-glow"></div>
        <div class="modal-header">
          <div class="modal-title-group">
            <span class="accent-bar purple"></span>
            <div class="modal-title">
              {{ sensitiveModalPlatformLabel }} 敏感数据
              <span class="modal-subtitle">共 {{ sensitiveModalTotalCount }} 条</span>
            </div>
          </div>
          <button class="modal-close" @click="closeSensitiveModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="sensitiveModalLoading" class="modal-loading">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else-if="sensitiveModalItems.length === 0" class="modal-empty">
            暂无敏感数据
          </div>
          <div v-else class="modal-list">
            <div class="modal-item" v-for="item in sensitiveModalItems" :key="item.id">
              <div class="modal-item-header">
                <span class="platform-tag">{{ item.platformLabel }}</span>
                <span class="time">{{ item.timeLabel }}</span>
              </div>
              <div class="modal-content">{{ item.content }}</div>
              <div class="modal-footer">
                <span class="author">{{ item.authorLabel || '匿名' }}</span>
                <a v-if="item.url" :href="item.url" target="_blank" rel="noopener">原文</a>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-pagination" v-if="sensitiveModalTotalPages > 1">
          <button class="pagination-btn" :disabled="sensitiveModalPage === 1" @click="goSensitivePage(sensitiveModalPage - 1)">上一页</button>
          <span class="pagination-text">{{ sensitiveModalPage }} / {{ sensitiveModalTotalPages }}</span>
          <button class="pagination-btn" :disabled="sensitiveModalPage === sensitiveModalTotalPages" @click="goSensitivePage(sensitiveModalPage + 1)">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

// Chart refs
const mainChartRef = ref(null)
const chartInstances = new Map()
const platformChartRefs = new Map()
const router = useRouter()

const setChartRef = (key, el) => {
  if (el) platformChartRefs.set(key, el)
}

// Initialize chart instance
const initChart = (key, el) => {
  if (!el) return null
  const chartKey = `chart-${key}`
  if (!chartInstances.has(chartKey)) {
    chartInstances.set(chartKey, echarts.init(el))
  }
  return chartInstances.get(chartKey)
}

// Render main pie chart
const renderMainPieChart = () => {
  console.log('==== 主饼图渲染开始 ====')
  console.log('1. mainChartRef.value:', mainChartRef.value)
  console.log('2. feedItems总数：', feedItems.value.length)

  if (!mainChartRef.value) {
    console.log('⚠️ 主饼图 DOM 元素不存在，跳过渲染')
    return
  }

  const chart = initChart('main', mainChartRef.value)
  if (!chart) {
    console.log('⚠️ 主饼图 ECharts 实例初始化失败')
    return
  }

  console.log('3. 主饼图 ECharts 实例初始化成功')

  const platforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu']
  const sensitiveCounts = platforms.reduce((acc, platform) => {
    acc[platform] = 0
    return acc
  }, {})

  if (platformStats.value) {
    for (const platform of platforms) {
      sensitiveCounts[platform] = platformStats.value?.[platform]?.sensitive || 0
    }
  } else {
    // 遍历feedItems计算敏感数据
    for (const item of feedItems.value) {
      const platformKey = item?.platformKey
      const isSensitive = item?.isSensitive ?? item?.sentiment === 'sensitive'
      if (platformKey && isSensitive) {
        sensitiveCounts[platformKey]++
      }
    }
  }

  console.log('4. 各平台敏感数据统计：', sensitiveCounts)

  const chartData = platforms.map(platform => ({
    value: sensitiveCounts[platform],
    name: {
      xhs: '小红书',
      dy: '抖音',
      ks: '快手',
      bili: 'B站',
      wb: '微博',
      tieba: '贴吧',
      zhihu: '知乎'
    }[platform]
  }))

  const sensitiveTotal = chartData.reduce((sum, item) => sum + item.value, 0)
  const allTotal = totalCount.value || feedItems.value.length || 0
  console.log('5. 主饼图数据：', chartData)
  console.log('6. 敏感总数：', sensitiveTotal)
  console.log('7. 所有数据总数：', allTotal)

  // 如果没有敏感数据，显示提示
  if (sensitiveTotal === 0) {
    chart.setOption({
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(10, 10, 15, 0.95)',
        borderColor: 'rgba(0, 204, 255, 0.3)',
        textStyle: { color: '#fff' },
        formatter: params => `${params.name}<br/>敏感: ${params.value}`,
        confine: true,
        appendToBody: true
      },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        roseType: 'radius',
        label: {
          show: true,
          position: 'center',
          formatter: '暂无\n敏感数据',
          color: '#8899aa',
          fontSize: 14
        },
        data: platforms.map(platform => ({
          value: 0,
          name: {
            xhs: '小红书',
            dy: '抖音',
            ks: '快手',
            bili: 'B站',
            wb: '微博',
            tieba: '贴吧',
            zhihu: '知乎'
          }[platform],
          itemStyle: {
            color: 'rgba(255, 255, 255, 0.05)',
            borderColor: 'rgba(0, 204, 255, 0.1)',
            borderWidth: 1
          }
        }))
      }, {
        type: 'pie',
        radius: [0, '35%'],
        center: ['50%', '50%'],
        silent: false,
        cursor: 'default',
        label: {
          show: true,
          position: 'center',
          formatter: () => {
            return [`{numerator|0}`, `{line|/}`, `{denominator|${allTotal}}`].join('\n')
          },
          rich: {
            numerator: { fontSize: 32, fontWeight: 900, color: '#8899aa' },
            line: { fontSize: 24, fontWeight: 700, color: '#666666', padding: [0, 0] },
            denominator: { fontSize: 20, fontWeight: 700, color: '#8899aa' }
          }
        },
        data: [{ value: 1, itemStyle: { color: 'transparent' }, name: '总计' }]
      }]
    })
    console.log('主饼图渲染完成：暂无敏感数据')
    return
  }

  // 有敏感数据则正常显示
  // 平台颜色配置（带发光效果）
  const platformColors = {
    xhs: { main: '#00ffa3', glow: 'rgba(0, 255, 163, 0.8)', gradient: ['#00ffa3', '#00cc66'] },
    dy: { main: '#ff6b9e', glow: 'rgba(255, 107, 158, 0.8)', gradient: ['#ff6b9e', '#cc1144'] },
    ks: { main: '#4dc9ff', glow: 'rgba(77, 201, 255, 0.8)', gradient: ['#4dc9ff', '#0099ff'] },
    bili: { main: '#ff89a9', glow: 'rgba(255, 137, 169, 0.8)', gradient: ['#ff89a9', '#ff4488'] },
    wb: { main: '#ffa726', glow: 'rgba(255, 167, 38, 0.8)', gradient: ['#ffa726', '#ff6600'] },
    tieba: { main: '#00ccff', glow: 'rgba(0, 204, 255, 0.8)', gradient: ['#00ccff', '#0066ff'] },
    zhihu: { main: '#a855f7', glow: 'rgba(168, 85, 247, 0.8)', gradient: ['#a855f7', '#7c22c9'] }
  }

  const enhancedChartData = chartData.map((item, index) => {
    const platformKey = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu'][index]
    const colors = platformColors[platformKey] || platformColors.xhs
    return {
      ...item,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 1,
          colorStops: [
            { offset: 0, color: colors.gradient[0] },
            { offset: 1, color: colors.gradient[1] }
          ]
        },
        borderColor: 'rgba(255, 255, 255, 0.3)',
        borderWidth: 2,
        shadowBlur: 20,
        shadowColor: colors.glow
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 35,
          shadowColor: colors.glow,
          borderWidth: 3,
          scale: true,
          scaleSize: 5
        }
      }
    }
  })

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 10, 15, 0.85)',
      borderColor: 'rgba(0, 204, 255, 0.3)',
      borderWidth: 1,
      borderRadius: 12,
      padding: [14, 18],
      textStyle: { color: '#fff' },
      extraCssText: 'box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);',
      appendToBody: true,
      confine: false,
      renderer: true,
      formatter: params => {
        const platformKey = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu'].find(k =>
                          platformNameToKey[params?.name] === k || params?.name === platformNameToKey[k])
                        || Object.keys(platformNameToKey).find(k => platformNameToKey[k] === params?.name)
        const colors = platformColors[platformKey] || platformColors.xhs
                        const percent = params.percent
                        return `<div style="font-size: 14px; font-weight: 600; color: #e6f0ff; margin-bottom: 6px;">${params.name}</div>
                                <div style="display: flex; align-items: center; gap: 12px;">
                                  <span style="font-size: 11px; color: #8899aa;">敏感数据</span>
                                  <span style="font-size: 24px; font-weight: 700; color: ${colors.main};">${params.value}</span>
                                  <span style="font-size: 14px; color: #8899aa;">(${percent}%)</span>
                                </div>`
      }
    },
    series: [{
      type: 'pie',
      radius: ['42%', '72%'],
      center: ['50%', '50%'],
      roseType: 'radius',
      padAngle: 4,
      itemStyle: { borderRadius: 12 },
      label: { show: false },
      data: enhancedChartData,
      emphasis: {
        scale: true,
        scaleSize: 8
      }
    }, {
      type: 'pie',
      radius: [0, '32%'],
      center: ['50%', '50%'],
      silent: false,
      cursor: 'default',
      label: {
        show: true,
        position: 'center',
        formatter: () => {
          return [`{numerator|${sensitiveTotal}}`, `{line|/}`, `{denominator|${allTotal}}`].join('\n')
        },
        rich: {
          numerator: { fontSize: 34, fontWeight: 900, color: '#ff4d4f', textShadow: '0 0 25px rgba(255, 77, 79, 0.9)' },
          line: { fontSize: 26, fontWeight: 700, color: '#8899aa', padding: [0, 0] },
          denominator: { fontSize: 22, fontWeight: 700, color: '#ffcc00', textShadow: '0 0 18px rgba(255, 204, 0, 0.6)' }
        }
      },
      data: [{ value: 1, itemStyle: { color: 'transparent' }, name: '总计' }]
    }]
  })
  chart.off('click')
  chart.on('click', params => {
    const platformKey = platformNameToKey[params?.name]
    if (platformKey) {
      openSensitiveModal(platformKey)
    }
  })
  console.log('==== 主饼图渲染完成 ====')
}

// Render platform charts
const renderPlatformCharts = () => {
  console.log('==== 渲染7个平台小饼图 ====')
  const platforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu']
  platforms.forEach(platform => {
    const el = platformChartRefs.get(platform)
    if (!el) {
      console.log(`⚠️ 平台 ${platform} 的 DOM 元素不存在`)
      return
    }

    const chartInstance = initChart(platform, el)

    // 统计该平台的敏感/非敏感数据
    let sensitive = 0
    let total = 0
    if (platformStats.value?.[platform]) {
      sensitive = platformStats.value?.[platform]?.sensitive || 0
      total = platformStats.value?.[platform]?.total || 0
    } else {
      for (const item of feedItems.value) {
        if (item?.platformKey === platform) {
          total += 1
          if (item?.isSensitive ?? item?.sentiment === 'sensitive') {
            sensitive += 1
          }
        }
      }
    }

    const nonSensitive = total - sensitive
    console.log(`平台 ${platform}: sensitive=${sensitive}, nonSensitive=${nonSensitive}, total=${total}`)

    // 如果没有数据，显示"暂无数据"
    if (total === 0) {
      chartInstance.setOption({
        series: [{
          type: 'pie',
          radius: ['52%', '82%'],
          center: ['50%', '50%'],
          label: {
            show: true,
            position: 'center',
            formatter: '暂无数据',
            color: '#8899aa',
            fontSize: 12
          },
          data: [{ value: 1, name: '暂无数据', itemStyle: { color: 'rgba(255, 255, 255, 0.08)' } }]
        }]
      })
      return
    }

    // 平台颜色配置
    const platformColors = {
      xhs: { main: '#00ffa3', glow: 'rgba(0, 255, 163, 0.8)', gradient: ['#00ffa3', '#00cc66'] },
      dy: { main: '#ff6b9e', glow: 'rgba(255, 107, 158, 0.8)', gradient: ['#ff6b9e', '#cc1144'] },
      ks: { main: '#4dc9ff', glow: 'rgba(77, 201, 255, 0.8)', gradient: ['#4dc9ff', '#0099ff'] },
      bili: { main: '#ff89a9', glow: 'rgba(255, 137, 169, 0.8)', gradient: ['#ff89a9', '#ff4488'] },
      wb: { main: '#ffa726', glow: 'rgba(255, 167, 38, 0.8)', gradient: ['#ffa726', '#ff6600'] },
      tieba: { main: '#00ccff', glow: 'rgba(0, 204, 255, 0.8)', gradient: ['#00ccff', '#0066ff'] },
      zhihu: { main: '#a855f7', glow: 'rgba(168, 85, 247, 0.8)', gradient: ['#a855f7', '#7c22c9'] }
    }

    const colors = platformColors[platform] || platformColors.xhs
    const platformLabel = platform === 'zhihu' ? '知乎' :
                          platform === 'xhs' ? '小红书' :
                          platform === 'dy' ? '抖音' :
                          platform === 'ks' ? '快手' :
                          platform === 'bili' ? 'B站' :
                          platform === 'wb' ? '微博' : '贴吧'

    // 有数据则显示敏感数据饼图
    chartInstance.setOption({
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(10, 10, 15, 0.85)',
        borderColor: 'rgba(0, 204, 255, 0.3)',
        borderWidth: 1,
        borderRadius: 12,
        padding: [12, 16],
        textStyle: { color: '#fff' },
        extraCssText: 'box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);',
        appendToBody: true,
        confine: false,
        renderer: true,
        formatter: params => {
          const percent = params.percent
          return `<div style="font-size: 13px; font-weight: 500; color: #e6f0ff; margin-bottom: 4px;">${platformLabel}</div>
                  <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 10px; color: #8899aa;">敏感数据</span>
                    <span style="font-size: 20px; font-weight: 700; color: #ff4d4f;">${params.value}</span>
                    <span style="font-size: 13px; color: #8899aa;">(${percent}%)</span>
                  </div>`
        }
      },
      series: [
        {
          type: 'pie',
          radius: ['48%', '78%'],
          center: ['50%', '50%'],
          label: { show: false },
          data: [
            {
              value: sensitive,
              name: '敏感',
              itemStyle: {
                color: {
                  type: 'linear',
                  x: 0, y: 0, x2: 1, y2: 1,
                  colorStops: [
                    { offset: 0, color: '#ff6b6b' },
                    { offset: 1, color: '#ff4d4f' }
                  ]
                },
                borderColor: 'rgba(255, 255, 255, 0.25)',
                borderWidth: 1.5,
                shadowBlur: 15,
                shadowColor: 'rgba(255, 77, 79, 0.6)'
              },
              emphasis: {
                itemStyle: {
                  shadowBlur: 25,
                  shadowColor: 'rgba(255, 77, 79, 0.8)',
                  borderWidth: 2
                }
              }
            },
            {
              value: Math.max(0, total - sensitive),
              name: '其他',
              itemStyle: {
                color: 'rgba(255, 255, 255, 0.05)',
                borderColor: 'rgba(255, 255, 255, 0.08)',
                borderWidth: 1,
                shadowBlur: 0
              },
              emphasis: {
                itemStyle: {
                  shadowBlur: 0
                }
              },
              label: { show: false }
            }
          ]
        },
        {
          type: 'pie',
          radius: [0, '32%'],
          center: ['50%', '50%'],
          silent: true,
          label: {
            show: true,
            position: 'center',
            formatter: () => [`{v|${sensitive}}`, `{l|/ ${total}}`].join('\n'),
            rich: {
              v: { fontSize: 20, fontWeight: 800, color: '#ff4d4f', textShadow: '0 0 12px rgba(255, 77, 79, 0.6)' },
              l: { fontSize: 11, color: '#8899aa', paddingTop: 3 }
            }
          },
          data: [{ value: 1, itemStyle: { color: 'transparent' } }]
        }
      ]
    })
  })
  console.log('==== 7个平台小饼图渲染完成 ====')
}

// Mock Data Options for Charts
const trendChartOptions = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(10, 10, 15, 0.95)',
    borderColor: 'rgba(0, 204, 255, 0.3)',
    textStyle: { color: '#fff' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    axisLine: { lineStyle: { color: 'rgba(0, 204, 255, 0.2)' } },
    axisLabel: { color: '#aaaaaa' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(0, 204, 255, 0.1)' } },
    axisLabel: { color: '#aaaaaa' }
  },
  series: [
    {
      name: '积极',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#00ff88' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(0, 255, 136, 0.5)' }, { offset: 1, color: 'rgba(0, 255, 136, 0)' }]
        }
      },
      emphasis: { focus: 'series' },
      data: [120, 132, 101, 134, 90, 230, 210]
    },
    {
      name: '中性',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#00ccff' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(0, 204, 255, 0.5)' }, { offset: 1, color: 'rgba(0, 204, 255, 0)' }]
        }
      },
      emphasis: { focus: 'series' },
      data: [20, 32, 11, 34, 10, 30, 20]
    },
    {
      name: '消极',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#ff6b6b' },
      areaStyle: { opacity: 0 },
      emphasis: { focus: 'series' },
      data: [20, 32, 11, 34, 10, 30, 20]
    },
    {
      name: '敏感',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#ffae00' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(255, 174, 0, 0.5)' }, { offset: 1, color: 'rgba(255, 174, 0, 0)' }]
        }
      },
      emphasis: { focus: 'series' },
      data: [20, 32, 11, 34, 10, 30, 20]
    }
  ]
}))

const pieChartOptions = computed(() => {
  const sensitiveData = platformSensitiveData.value
  const total = sensitiveData.reduce((sum, item) => sum + item.value, 0)
  const colors = [
    { grad: ['#00ffa3', '#008a5c'], glow: 'rgba(0, 255, 163, 0.6)' },    // 小红书 - 绿色
    { grad: ['#ff6b9e', '#cc2343'], glow: 'rgba(255, 107, 158, 0.6)' },    // 抖音 - 粉红
    { grad: ['#4dc9ff', '#2d5fe0'], glow: 'rgba(77, 201, 255, 0.6)' },    // 快手 - 蓝色
    { grad: ['#ff89a9', '#ff4d9a'], glow: 'rgba(255, 137, 169, 0.6)' },    // B站 - 粉红
    { grad: ['#ffa726', '#ff4d6f'], glow: 'rgba(255, 167, 38, 0.6)' },    // 微博 - 橙红
    { grad: ['#00ccff', '#0066ff'], glow: 'rgba(0, 204, 255, 0.6)' },    // 贴吧 - 蓝色
    { grad: ['#a855f7', '#6b21a8'], glow: 'rgba(168, 85, 247, 0.6)' }     // 知乎 - 紫色
  ]

  return {
    tooltip: {
      backgroundColor: 'rgba(10, 20, 35, 0.9)',
      borderColor: '#00c3ff',
      textStyle: { color: '#fff' }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#c0ccda', fontSize: 11 },
      itemGap: 12
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        roseType: 'radius',
        padAngle: 3,
        itemStyle: { borderRadius: 8 },
        label: { show: false },
        data: sensitiveData.map((item, index) => ({
          value: item.value,
          name: item.name,
          itemStyle: {
            color: echarts.graphic.LinearGradient(0, 0, 1, 1, [
              { offset: 0, color: colors[index].grad[0] },
              { offset: 1, color: colors[index].grad[1] }
            ]),
            borderColor: 'rgba(255,255,255,0.2)',
            borderWidth: 1,
            shadowBlur: 12,
            shadowColor: colors[index].glow
          }
        }))
      },
      {
        type: 'pie',
        radius: [0, '35%'],
        center: ['50%', '50%'],
        silent: true,
        label: {
          show: true,
          position: 'center',
          formatter: () => [`{v|${total}}`, `{l|敏感总数}`].join('\n'),
          rich: {
            v: { fontSize: 28, fontWeight: 900, color: '#ff4d4f', textShadow: '0 0 20px rgba(255, 77, 79, 0.8)' },
            l: { fontSize: 11, color: '#8899aa', paddingTop: 4 }
          }
        },
        data: [{ value: 1, itemStyle: { color: 'transparent' } }]
      }
    ]
  }
})

const feedItems = ref([])
const feedLoading = ref(false)
const lastUpdatedAt = ref(null)
const platformStats = ref(null)
const sensitiveModalOpen = ref(false)
const sensitiveModalLoading = ref(false)
const sensitiveModalItems = ref([])
const sensitiveModalPage = ref(1)
const sensitiveModalTotalPages = ref(1)
const sensitiveModalTotalCount = ref(0)
const sensitiveModalPlatform = ref('')
const sensitiveModalPlatformLabel = ref('全部平台')

const sentimentCounts = computed(() => {
  const counts = { positive: 0, negative: 0, neutral: 0, sensitive: 0 }
  for (const item of feedItems.value) {
    const key = (item?.isSensitive ?? item?.sentiment === 'sensitive')
      ? 'sensitive'
      : (item?.sentiment || 'neutral')
    if (counts[key] !== undefined) {
      counts[key] += 1
    } else {
      counts.neutral += 1
    }
  }
  const total = counts.positive + counts.negative + counts.neutral + counts.sensitive
  return { ...counts, total }
})

const platformSentimentCounts = computed(() => {
  if (platformStats.value) {
    return platformStats.value
  }
  const platforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu']
  const base = { positive: 0, negative: 0, neutral: 0, sensitive: 0, total: 0 }
  const result = {}

  platforms.forEach((platform) => {
    result[platform] = { ...base }
  })

  for (const item of feedItems.value) {
    const platformKey = item?.platformKey
    if (!platformKey || !result[platformKey]) continue
    const sentimentKey = (item?.isSensitive ?? item?.sentiment === 'sensitive')
      ? 'sensitive'
      : (item?.sentiment || 'neutral')
    if (result[platformKey][sentimentKey] !== undefined) {
      result[platformKey][sentimentKey] += 1
    } else {
      result[platformKey].neutral += 1
    }
    result[platformKey].total += 1
  }

  return result
})

const fetchPlatformStats = async ({ signal = null } = {}) => {
  if (signal?.aborted) return
  try {
    const res = await axios.get('/api/monitor/platform-sentiment-stats', { signal })
    if (signal?.aborted) return
    const data = res.data || {}
    platformStats.value = data
  } catch (e) {
    if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return
    if (signal?.aborted) return
    platformStats.value = null
  }
}

const openSensitiveModal = async (platformKey) => {
  sensitiveModalPlatform.value = platformKey || ''
  sensitiveModalPlatformLabel.value = getPlatformLabel(platformKey)
  sensitiveModalPage.value = 1
  sensitiveModalOpen.value = true
  await fetchSensitiveModalPage()
}

const closeSensitiveModal = () => {
  sensitiveModalOpen.value = false
  sensitiveModalItems.value = []
  sensitiveModalTotalPages.value = 1
  sensitiveModalTotalCount.value = 0
}

const fetchSensitiveModalPage = async () => {
  sensitiveModalLoading.value = true
  try {
    const res = await axios.get('/api/monitor/feed/sensitive', {
      params: {
        platform: sensitiveModalPlatform.value || undefined,
        page: sensitiveModalPage.value,
        page_size: 20
      }
    })
    const items = Array.isArray(res.data?.items) ? res.data.items : []
    sensitiveModalItems.value = items.map((row, index) => {
      const platformKey = normalizePlatform(row?.platform)
      const recordTime = row?.created_at || getRecordTime(row)
      return {
        id: row?.id || `${platformKey || 'data'}-${index}`,
        platformKey,
        platformLabel: row?.platform_name || getPlatformLabel(platformKey),
        content: row?.content || pickContent(row),
        timeLabel: formatRelativeTime(recordTime),
        authorLabel: row?.author || '',
        url: row?.url || '',
        sortTime: recordTime || 0
      }
    })
    if (res.data?.pagination) {
      sensitiveModalTotalPages.value = res.data.pagination.total_pages || 1
      sensitiveModalTotalCount.value = res.data.pagination.total_count || 0
    }
  } catch (e) {
    sensitiveModalItems.value = []
    sensitiveModalTotalPages.value = 1
    sensitiveModalTotalCount.value = 0
  } finally {
    sensitiveModalLoading.value = false
  }
}

const goSensitivePage = async (page) => {
  if (page < 1 || page > sensitiveModalTotalPages.value) return
  sensitiveModalPage.value = page
  await fetchSensitiveModalPage()
}

const pieTooltip = {
  trigger: 'item',
  backgroundColor: 'rgba(10, 10, 15, 0.95)',
  borderColor: 'rgba(0, 204, 255, 0.3)',
  textStyle: { color: '#fff' },
  appendToBody: true,
  confine: false,
  extraCssText: 'z-index: 9999; max-width: 220px; white-space: normal; pointer-events: none;'
}

const buildPlatformPieOptions = ({ sensitive = 0, total = 0 }) => ({
  tooltip: pieTooltip,
  legend: {
    bottom: '4%',
    left: 'center',
    textStyle: { color: '#aaaaaa', fontSize: 10 }
  },
  series: (() => {
    if (!total) {
      return [
        {
          type: 'pie',
          radius: ['55%', '80%'],
          center: ['50%', '50%'],
          label: {
            show: true,
            position: 'center',
            formatter: () => '暂无数据',
            color: '#8899aa',
            fontSize: 12
          },
          data: [{ value: 1, name: '暂无数据', itemStyle: { color: 'rgba(255, 255, 255, 0.08)' } }]
        }
      ]
    }
    return [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        label: { show: false },
        data: [
          { value: sensitive, name: '敏感', itemStyle: { color: '#ff4d4f' } },
          { value: Math.max(total - sensitive, 0), name: '非敏感', itemStyle: { color: '#3b82f6' } }
        ]
      },
      {
        type: 'pie',
        radius: [0, '35%'],
          center: ['50%', '50%'],
        silent: true,
        label: {
          show: true,
          position: 'center',
          formatter: () => [`{v|${sensitive}}`, `{l|/ ${total}}`].join('\n'),
          rich: {
            v: { fontSize: 18, fontWeight: 800, color: '#ff4d4f' },
            l: { fontSize: 10, color: '#8899aa', paddingTop: 2 }
          }
        },
        data: [{ value: 1, itemStyle: { color: 'transparent' } }]
      }
    ]
  })()
})

const handlePlatformJump = (platformKey) => {
  if (!platformKey) return
  router.push({ path: '/data', query: { platform: platformKey } })
}

const platformPieOptions = computed(() => {
  const counts = platformSentimentCounts.value
  return {
    xhs: buildPlatformPieOptions(counts.xhs || {}),
    dy: buildPlatformPieOptions(counts.dy || {}),
    ks: buildPlatformPieOptions(counts.ks || {}),
    bili: buildPlatformPieOptions(counts.bili || {}),
    wb: buildPlatformPieOptions(counts.wb || {}),
    tieba: buildPlatformPieOptions(counts.tieba || {}),
    zhihu: buildPlatformPieOptions(counts.zhihu || {})
  }
})

// 统计数据
const stats = ref({
  total: 0,
  sensitive: 0,
  sentimentIndex: 0,
  hotScore: 0
})

// 分页状态
const currentPage = ref(1)
const pageSize = ref(100)
const totalCount = ref(0)
const totalPages = ref(1)

// 请求管理：使用 AbortController 控制请求取消
const abortController = ref(null)
const refreshRequestId = ref(0)
const isMounted = ref(true)

const platformLabels = {
  xhs: '小红书',
  dy: '抖音',
  ks: '快手',
  bili: 'B站',
  wb: '微博',
  tieba: '贴吧',
  zhihu: '知乎'
}

const platformAliases = {
  xhs: ['xhs', 'xiaohongshu', 'redbook'],
  dy: ['dy', 'douyin', 'tiktok'],
  ks: ['ks', 'kuaishou'],
  bili: ['bili', 'bilibili'],
  wb: ['wb', 'weibo'],
  tieba: ['tieba', 'baidutieba'],
  zhihu: ['zhihu']
}

const platformNameToKey = {
  '小红书': 'xhs',
  '抖音': 'dy',
  '快手': 'ks',
  'B站': 'bili',
  '微博': 'wb',
  '贴吧': 'tieba',
  '知乎': 'zhihu'
}

const normalizePlatform = (value) => {
  if (!value) return 'data'
  const normalized = String(value).toLowerCase()
  for (const [platform, aliases] of Object.entries(platformAliases)) {
    if (aliases.some(alias => normalized.includes(alias))) {
      return platform
    }
  }
  return normalized
}

const getPlatformLabel = (platformKey) => {
  return platformLabels[platformKey] || platformKey || '数据源'
}

const toMillis = (value) => {
  if (!value) return null
  if (value instanceof Date) return value.getTime()
  if (typeof value === 'number') {
    return value < 1e12 ? value * 1000 : value
  }
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return null
    const numeric = Number(trimmed)
    if (!Number.isNaN(numeric)) {
      return numeric < 1e12 ? numeric * 1000 : numeric
    }
    const parsed = Date.parse(trimmed)
    return Number.isNaN(parsed) ? null : parsed
  }
  return null
}

const formatRelativeTime = (value) => {
  const ts = toMillis(value)
  if (!ts) return '刚刚'
  const diff = Date.now() - ts
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
}

const pickContent = (row) => {
  if (!row) return '暂无内容'
  if (typeof row === 'string') return row
  const candidates = [
    'content',
    'title',
    'desc',
    'content_text',
    'text',
    'note_desc',
    'summary',
    'message',
    'comment'
  ]
  for (const key of candidates) {
    if (row[key]) return String(row[key])
  }
  const firstString = Object.values(row).find(val => typeof val === 'string' && val.trim())
  if (firstString) return firstString
  try {
    return JSON.stringify(row)
  } catch (e) {
    return '暂无内容'
  }
}

const getRecordTime = (row, fallbackSeconds) => {
  const candidates = ['created_time', 'create_time', 'created_at', 'publish_time', 'time', 'timestamp']
  for (const key of candidates) {
    if (row && row[key]) {
      const parsed = toMillis(row[key])
      if (parsed) return parsed
    }
  }
  return toMillis(fallbackSeconds)
}

const buildFeedItems = (rows) => {
  if (!rows || !Array.isArray(rows)) {
    console.log('buildFeedItems: invalid rows', rows)
    return []
  }
  console.log('buildFeedItems: processing', rows.length, 'items')

  // 使用 Map 进行去重，以 id 为唯一标识
  const uniqueItemsMap = new Map()

  rows.forEach((row, index) => {
    const platformKey = normalizePlatform(row?.platform)
    const recordTime = row?.created_at || getRecordTime(row)
    const isSensitive = row?.is_sensitive ?? row?.isSensitive ?? row?.sentiment === 'sensitive'
    const sentiment = isSensitive ? 'sensitive' : (row?.sentiment || 'neutral')

    // 生成唯一标识：优先使用 id，否则用 url+content+platform 组合
    const uniqueKey = row?.id || `${row?.url || ''}-${row?.content || ''}-${platformKey}`

    const item = {
      id: row?.id || `${platformKey || 'data'}-${index}`,
      platformKey,
      platformLabel: row?.platform_name || getPlatformLabel(platformKey),
      content: row?.content || pickContent(row),
      timeLabel: formatRelativeTime(recordTime),
      authorLabel: row?.author || '',
      url: row?.url || '',
      sortTime: recordTime || 0,
      // 情绪分析数据
      sentiment,
      sentimentScore: row?.sentiment_score || 0,
      sentimentLabels: row?.sentiment_labels || {},
      isSensitive
    }

    // 如果该 key 已存在，保留时间较新的数据
    if (!uniqueItemsMap.has(uniqueKey) || item.sortTime > uniqueItemsMap.get(uniqueKey).sortTime) {
      uniqueItemsMap.set(uniqueKey, item)
    }
  })

  const result = Array.from(uniqueItemsMap.values())
  console.log('buildFeedItems: after deduplication', result.length, 'items (removed', rows.length - result.length, 'duplicates)')

  return result
}

// 获取情绪类型显示标签
const getSentimentLabel = (sentiment) => {
  const labels = {
    positive: '积极',
    negative: '消极',
    neutral: '中性',
    sensitive: '敏感'
  }
  return labels[sentiment] || '中性'
}

// 获取情绪类型样式类名
const getSentimentClass = (sentiment) => {
  return `sentiment-${sentiment || 'neutral'}`
}

// 格式化情感指数
const formatSentimentIndex = (index) => {
  if (index > 0.3) return '+' + index.toFixed(1)
  if (index < -0.3) return index.toFixed(1)
  return '0.0'
}

// 获取情感指数样式类名
const getSentimentIndexClass = (index) => {
  if (index > 0.3) return 'positive'
  if (index < -0.3) return 'negative'
  return 'neutral'
}

// 获取情感指数文本
const getSentimentIndexText = (index) => {
  if (index > 0.3) return '积极向好'
  if (index < -0.3) return '需要关注'
  return '情绪平稳'
}

// 获取敏感舆情趋势类名
const getSentimentTrendClass = (sensitive, total) => {
  if (total === 0) return ''
  const ratio = (sensitive / total) * 100
  if (ratio > 10) return 'negative'
  if (ratio > 5) return 'neutral'
  return 'up'
}

// 获取敏感舆情趋势文本
const getSentimentTrendText = (sensitive, total) => {
  if (total === 0) return '暂无数据'
  const ratio = (sensitive / total) * 100
  if (ratio > 10) return `占比 ${ratio.toFixed(1)}% 需警惕`
  if (ratio > 5) return `占比 ${ratio.toFixed(1)}% 需关注`
  return `占比 ${ratio.toFixed(1)}% 正常`
}

// 获取热度分数文本
const getHotScoreText = (score) => {
  if (score > 80) return '非常活跃'
  if (score > 50) return '活跃'
  if (score > 20) return '正常'
  return '平淡'
}

// 分页计算属性 - 显示页码范围（带省略号）
const displayedPages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2 // 当前页前后显示的页数

  // 总是显示第一页
  pages.push(1)

  // 如果第一页不是当前页且距离较远，添加省略号
  if (current > delta + 3) {
    pages.push('...')
  }

  // 当前页附近的页码
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    pages.push(i)
  }

  // 如果最后一页不是当前页且距离较远，添加省略号
  if (current < total - delta - 2) {
    pages.push('...')
  }

  // 总是显示最后一页
  if (total > 1) {
    pages.push(total)
  }

  return pages
})

// 页面跳转函数
const goToPage = async (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  // 滚动到列表顶部
  const listWrapper = document.querySelector('.list-wrapper')
  if (listWrapper) {
    listWrapper.scrollTop = 0
  }
  // 获取该页数据
  await fetchMonitorFeedPage()
}

const setPageSize = async (size) => {
  if (pageSize.value === size) return
  pageSize.value = size
  currentPage.value = 1
  await fetchMonitorFeedPage()
}

// 获取指定页的数据
const fetchMonitorFeedPage = async ({ withLoading = true, signal = null } = {}) => {
  // 如果请求已被取消，直接返回
  if (signal?.aborted) return

  if (withLoading) {
    feedLoading.value = true
  }
  try {
    const [res] = await Promise.all([
      axios.get('/api/monitor/feed', {
        params: {
          page: currentPage.value,
          page_size: pageSize.value
        },
        signal
      }),
      fetchPlatformStats({ signal })
    ])
    // 请求完成后再次检查是否被取消
    if (signal?.aborted) return

    const items = Array.isArray(res.data?.items) ? res.data.items : []
    console.log('API Response success:', items.length, 'items')

    // 更新分页信息
    if (res.data?.pagination) {
      totalCount.value = res.data.pagination.total_count || 0
      totalPages.value = res.data.pagination.total_pages || 1
    }

    // 更新统计数据
    if (res.data?.stats) {
      stats.value = res.data.stats
    }

    const merged = buildFeedItems(items)
    console.log('buildFeedItems result:', merged.length, 'items')

    feedItems.value = merged

    lastUpdatedAt.value = res.data?.fetched_at || new Date()
    console.log('fetchMonitorFeed complete, feedItems.value.length:', feedItems.value.length)
  } catch (e) {
    // 如果是主动取消的错误，不处理
    if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return
    if (signal?.aborted) return

    // 只在组件未卸载时更新状态
    feedItems.value = []
    platformStats.value = null
    totalCount.value = 0
    totalPages.value = 1
    lastUpdatedAt.value = new Date()
    console.log('fetchMonitorFeed error:', e.message)
  } finally {
    if (withLoading && !signal?.aborted) {
      feedLoading.value = false
    }
  }
}

// 刷新数据（重置到第一页）
const fetchMonitorFeed = async ({ withLoading = true, signal = null } = {}) => {
  currentPage.value = 1
  await fetchMonitorFeedPage({ withLoading, signal })
}

const batchPlatforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu']

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const waitForCrawlerIdle = async (timeoutMs = 180000, signal = null) => {
  const startedAt = Date.now()
  while (Date.now() - startedAt < timeoutMs) {
    if (signal?.aborted) return false
    try {
      const res = await axios.get('/api/crawler/status', { signal })
      if (res.data?.status === 'idle') {
        return true
      }
    } catch (e) {
      if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return false
      return false
    }
    await sleep(2000)
  }
  return false
}

const startBatchCrawler = async (signal = null) => {
  await axios.post('/api/crawler/start', {
    platforms: batchPlatforms,
    crawler_type: 'search',
    login_type: 'cookie',
    headless: true
  }, { signal })
}

const refreshMonitorFeed = async () => {
  if (feedLoading.value) return

  // 创建新的 AbortController 和请求 ID
  const controller = new AbortController()
  abortController.value = controller
  const currentRequestId = ++refreshRequestId.value

  feedLoading.value = true
  console.log('refreshMonitorFeed started')

  try {
    // 启动爬虫
    await startBatchCrawler(controller.signal)
    if (controller.signal.aborted) return

    // 等待爬虫完成
    await waitForCrawlerIdle(180000, controller.signal)
    if (controller.signal.aborted) return

    // 获取最新数据
    await fetchMonitorFeed({ withLoading: false, signal: controller.signal })
  } catch (e) {
    // 如果是取消操作，不处理
    if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return
    if (controller.signal.aborted) return

    // 其他错误，仍然尝试获取数据
    await fetchMonitorFeed({ withLoading: false, signal: controller.signal })
  } finally {
    // 只有当前请求且组件仍挂载时才清理状态
    if (currentRequestId === refreshRequestId.value && !controller.signal.aborted && isMounted.value) {
      feedLoading.value = false
      abortController.value = null
      // 只有刷新完成时才清理 localStorage
      localStorage.removeItem('dashboard-refresh-running')
      localStorage.removeItem('dashboard-refresh-start-time')
    }
  }
}

const checkCrawlerAndFetch = async () => {
  try {
    const res = await axios.get('/api/crawler/status')
    if (res.data?.status === 'idle') {
      // 爬虫已完成，获取数据
      await fetchMonitorFeed()
    } else {
      // 爬虫还在运行，继续等待
      feedLoading.value = true
      const controller = new AbortController()
      abortController.value = controller
      const currentRequestId = ++refreshRequestId.value

      try {
        await waitForCrawlerIdle(180000, controller.signal)
        if (!controller.signal.aborted) {
          await fetchMonitorFeed({ withLoading: false, signal: controller.signal })
        }
      } catch (e) {
        // 忽略错误
      } finally {
        if (currentRequestId === refreshRequestId.value && !controller.signal.aborted) {
          feedLoading.value = false
          abortController.value = null
        }
      }
    }
  } catch (e) {
    // 出错则重新获取
    await fetchMonitorFeed()
  }
}

// 自动刷新定时器
let refreshInterval = null
const AUTO_REFRESH_INTERVAL = 30000 // 30秒自动刷新

onMounted(async () => {
  isMounted.value = true
  // 重置加载状态，防止被旧状态阻塞
  feedLoading.value = false
  abortController.value = null

  // 先展示已有 monitor_feed 数据
  await fetchMonitorFeed()

  nextTick(() => {
    renderMainPieChart()
    renderPlatformCharts()
  })

  // 启动自动刷新
  refreshInterval = setInterval(() => {
    if (!feedLoading.value) {
      fetchMonitorFeed({ withLoading: false })
    }
  }, AUTO_REFRESH_INTERVAL)

  window.addEventListener('resize', () => chartInstances.forEach(c => c?.resize()))
})

onBeforeUnmount(() => {
  isMounted.value = false

  // 清理自动刷新定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }

  // 保存当前刷新状态到 localStorage，以便返回时恢复
  if (feedLoading.value) {
    localStorage.setItem('dashboard-refresh-running', 'true')
    localStorage.setItem('dashboard-refresh-start-time', Date.now().toString())
  } else {
    localStorage.removeItem('dashboard-refresh-running')
    localStorage.removeItem('dashboard-refresh-start-time')
  }
  chartInstances.forEach(c => c?.dispose())
})

// 监听数据变化，重新渲染图表
watch(feedItems, () => {
  if (feedItems.value.length > 0) {
    nextTick(() => {
      renderMainPieChart()
      renderPlatformCharts()
    })
  }
}, { deep: true })
</script>

<style scoped>
.layout-wrapper {
  position: relative;
  z-index: 1;
  padding: 24px 32px;
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.dashboard-main-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
  align-items: stretch;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.center-panel {
  min-width: 0;
  display: flex;
  height: 100%;
}

.feed-panel {
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
  max-height: 900px;
}

.feed-panel .list-wrapper {
  flex: 1 1 auto;
  min-height: 0;
  max-height: 680px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 8, 14, 0.7);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-card {
  width: min(900px, 92vw);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-card > :not(.border-glow) {
  position: relative;
  z-index: 1;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-title {
  font-size: 12px;
  font-weight: bold;
  color: #c0ccda;
  letter-spacing: 1px;
}

.modal-subtitle {
  margin-left: 8px;
  font-size: 12px;
  color: var(--text-dim);
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 24px;
  color: #8899aa;
  cursor: pointer;
  transition: all 0.2s;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.modal-close:hover {
  color: var(--cyan-primary);
  background: rgba(0, 204, 255, 0.08);
  transform: none;
}

.modal-body {
  padding: 16px 18px 18px;
  overflow-y: auto;
}

.modal-loading,
.modal-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #9fb2d3;
  min-height: 180px;
}

.modal-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-item {
  background: rgba(0, 204, 255, 0.03);
  border: 1px solid rgba(0, 204, 255, 0.12);
  border-radius: 12px;
  padding: 12px 14px;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-item:hover {
  background: rgba(0, 204, 255, 0.08);
  border-color: var(--border-cyan);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.15);
}

.modal-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.modal-content {
  color: #e1e9ff;
  font-size: 13px;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 12px;
  color: #8fa3c1;
}

.modal-footer a {
  color: #4fd1ff;
  text-decoration: none;
  transition: all 0.2s;
}

.modal-footer a:hover {
  color: #00ccff;
  text-shadow: 0 0 8px rgba(0, 204, 255, 0.5);
}

.modal-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 18px 18px;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-cyan);
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.page-title {
  margin: 0;
  font-size: 28px;
  letter-spacing: 0.5px;
  color: var(--text-white);
  text-transform: uppercase;
}

.page-title .subtitle {
  display: block;
  font-size: 12px;
  letter-spacing: 2px;
  color: var(--orange-gold);
  margin-top: 4px;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  color: var(--text-dim);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 204, 255, 0.2);
}

.dashboard-content {
  flex: 1;
  display: flex;
  gap: 20px;
  min-height: 0;
}

.left-panel {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.panel-card {
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.panel-card:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 0 25px rgba(255, 204, 0, 0.1),
              0 0 50px rgba(255, 204, 0, 0.05);
}

.panel-card.main-card {
  min-height: 300px;
}

.left-panel .chart-card {
  min-height: 240px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.left-panel .chart-card:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 0 20px rgba(255, 204, 0, 0.08),
              0 0 40px rgba(255, 204, 0, 0.04);
}

.chart-row .chart-card {
  min-height: 320px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.chart-row .chart-card:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 0 20px rgba(255, 204, 0, 0.08),
              0 0 40px rgba(255, 204, 0, 0.04);
}

.sentiment-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.sentiment-grid .chart-card {
  min-height: 220px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.sentiment-grid .chart-card:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 0 20px rgba(255, 204, 0, 0.08),
              0 0 40px rgba(255, 204, 0, 0.04);
}

.sentiment-summary {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-header {
  font-size: 12px;
  color: var(--text-light);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(0, 204, 255, 0.05);
  border: 1px solid rgba(0, 204, 255, 0.15);
}

.summary-item .label {
  font-size: 10px;
  color: var(--text-dim);
  letter-spacing: 0.5px;
}

.summary-item .value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-white);
}

.summary-item.positive .value {
  color: var(--green-status);
}

.summary-item.negative .value {
  color: #ff6b6b;
}

.summary-item.neutral .value {
  color: var(--cyan-primary);
}

.summary-item.sensitive .value {
  color: var(--orange-gold);
}

/* Cyberpunk Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--cyan-primary);
  border-radius: 4px;
  box-shadow: 0 0 10px var(--cyan-primary);
  transition: all 0.3s;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--blue-secondary);
  box-shadow: 0 0 15px var(--blue-secondary);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.stat-card {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border-radius: 20px;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--border-cyan);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow:
    0 0 40px rgba(0, 204, 255, 0.1),
    0 4px 24px rgba(0, 0, 0, 0.4);
}

.stat-card:hover {
  transform: translateY(-5px);
  border-color: var(--glow-cyan);
  box-shadow:
    0 0 60px rgba(0, 204, 255, 0.2),
    0 8px 32px rgba(0, 0, 0, 0.6);
}

.stat-icon {
  font-size: 2.5rem;
  background: rgba(0, 204, 255, 0.08);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid rgba(0, 204, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.2);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-info .label {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 500;
}

.stat-info .value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-white);
  margin: 0.2rem 0;
  letter-spacing: 1px;
}

.stat-info .value.sensitive {
  color: var(--orange-gold);
  text-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
  animation: sensitivePulse 2s ease-in-out infinite;
}

.stat-info .value.hot {
  color: var(--cyan-primary);
  text-shadow: 0 0 20px rgba(0, 204, 255, 0.5);
}

.stat-info .trend {
  font-size: 0.75rem;
  color: var(--text-dim);
  letter-spacing: 0.5px;
}

.stat-info .trend.up {
  color: var(--green-status);
}

.stat-info .trend.down {
  color: #ff6b6b;
}

.stat-info .trend.negative {
  color: #ff6b6b;
  font-weight: 600;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  min-height: 400px;
}

/* Recent List */
.recent-list {
  padding: 1.5rem;
  border-radius: 20px;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--border-cyan);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  box-shadow:
    0 0 40px rgba(0, 204, 255, 0.1),
    0 4px 24px rgba(0, 0, 0, 0.4);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.recent-list:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow:
    0 0 45px rgba(0, 204, 255, 0.12),
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 25px rgba(255, 204, 0, 0.08);
}

.recent-list.compact {
  min-height: 0;
  padding: 1.25rem;
}

.recent-list.compact .list-wrapper {
  min-height: 160px;
}

.recent-list h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--cyan-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
  text-shadow: 0 0 20px rgba(0, 204, 255, 0.5);
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.feed-controls {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.feed-updated {
  font-size: 0.75rem;
  color: var(--text-dim);
  letter-spacing: 0.5px;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--border-cyan);
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.3), rgba(0, 204, 255, 0.15));
  color: var(--cyan-primary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-weight: 500;
  letter-spacing: 0.5px;
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.2);
}

.refresh-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.4), rgba(0, 204, 255, 0.25));
  border-color: var(--glow-cyan);
  box-shadow: 0 0 30px rgba(0, 204, 255, 0.4);
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  display: inline-block;
  transition: transform 0.2s;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

.feed-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-dim);
  padding: 1rem 0;
  flex: 1;
}

.feed-state .hint {
  font-size: 0.8rem;
  color: var(--text-dim);
  opacity: 0.7;
}

.list-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding-right: 0.35rem;
  scroll-behavior: smooth;
}

/* 内部滚动条样式 */
.list-wrapper::-webkit-scrollbar {
  width: 6px;
}

.list-wrapper::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
}

.list-wrapper::-webkit-scrollbar-thumb {
  background: rgba(0, 204, 255, 0.3);
  border-radius: 3px;
  transition: all 0.3s;
}

.list-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 204, 255, 0.5);
}

.list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem;
  background: rgba(0, 204, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(0, 204, 255, 0.1);
  opacity: 0;
  transform: translateX(-20px);
  animation: fadeSlideIn 0.4s ease-out forwards;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeSlideIn {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.list-item:hover {
  background: rgba(0, 204, 255, 0.08);
  border-color: var(--border-cyan);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.15);
}

.platform-tag {
  background: rgba(0, 102, 255, 0.2);
  color: var(--cyan-primary);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.5px;
  border: 1px solid rgba(0, 204, 255, 0.2);
  text-transform: uppercase;
}

.content {
  flex: 1;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-light);
}

.time {
  font-size: 0.8rem;
  color: var(--text-dim);
  font-weight: 500;
}

.author {
  font-size: 0.8rem;
  color: var(--text-light);
  font-weight: 500;
}

.author.muted {
  color: var(--text-dim);
}

/* 情绪标签样式 */
.sentiment-tag {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  white-space: nowrap;
}

.sentiment-tag.positive {
  background: rgba(0, 255, 136, 0.15);
  color: var(--green-status);
  border: 1px solid rgba(0, 255, 136, 0.3);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
}

.sentiment-tag.negative {
  background: rgba(255, 107, 107, 0.15);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.3);
  box-shadow: 0 0 10px rgba(255, 107, 107, 0.2);
}

.sentiment-tag.neutral {
  background: rgba(0, 204, 255, 0.08);
  color: var(--cyan-primary);
  border: 1px solid rgba(0, 204, 255, 0.2);
}

.sentiment-tag.sensitive {
  background: rgba(255, 170, 0, 0.15);
  color: var(--orange-gold);
  border: 1px solid rgba(255, 170, 0, 0.3);
  box-shadow: 0 0 15px rgba(255, 170, 0, 0.3);
  animation: sensitivePulse 2s ease-in-out infinite;
}

@keyframes sensitivePulse {
  0%, 100% {
    box-shadow: 0 0 10px rgba(255, 170, 0, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
  }
}

/* 情绪类型列表项样式 */
.list-item.sentiment-positive {
  border-left: 3px solid var(--green-status);
}

.list-item.sentiment-negative {
  border-left: 3px solid #ff6b6b;
}

.list-item.sentiment-neutral {
  border-left: 3px solid var(--cyan-primary);
}

.list-item.sentiment-sensitive {
  border-left: 3px solid var(--orange-gold);
  background: rgba(255, 170, 0, 0.03);
}

/* 加载动画 */
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--cyan-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.5);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Cyberpunk Style - CSS Variables */
:root {
  --cyan-primary: #00ccff;
  --blue-secondary: #0066ff;
  --orange-gold: #ffae00;
  --green-status: #00ff88;
  --text-white: #FFFFFF;
  --text-color: var(--text-white);
  --text-gray: #888888;
  --text-light: #aaaaaa;
  --text-dim: #666666;
  --bg-pure-black: #050510;
  --bg-glass: rgba(255, 255, 255, 0.03);
  --border-cyan: rgba(0, 204, 255, 0.2);
  --glow-cyan: rgba(0, 204, 255, 0.4);
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background: var(--bg-pure-black);
  color: var(--text-white);
}

/* Dashboard Wrapper with Cyberpunk Background */
.dashboard-wrapper {
  min-height: 100vh;
  background: var(--bg-pure-black);
  position: relative;
  overflow: hidden;
}

/* Ambient Background Effects */
.ambient-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* Nebula Effects */
.nebula {
  position: absolute;
  width: 80vw;
  height: 70vh;
  filter: blur(120px);
  opacity: 0.28;
  mix-blend-mode: screen;
}
.nebula.blue {
  background: radial-gradient(circle, #0066ff, transparent 75%);
  top: -10%;
  left: -5%;
}
.nebula.gold {
  background: radial-gradient(circle, #ffaa00, transparent 75%);
  bottom: -10%;
  right: -5%;
}

/* Breathing Line Effects */
.breathing-line {
  position: absolute;
  height: 1px;
  background: linear-gradient(90deg, transparent, #ffaa00, transparent);
  filter: blur(1px);
  opacity: 0.3;
  animation: breathe 8s infinite ease-in-out;
}
.gold-1 {
  width: 100%;
  top: 30%;
  left: -50%;
  transform: rotate(-5deg);
}
.gold-2 {
  width: 100%;
  bottom: 20%;
  right: -50%;
  transform: rotate(3deg);
  animation-delay: -4s;
}

/* Scan Grid Effect */
.scan-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: linear-gradient(to bottom, black, transparent);
  animation: gridMove 25s linear infinite;
}
@keyframes gridMove {
  from { background-position: 0 0; }
  to { background-position: 0 50px; }
}
@keyframes breathe {
  0%, 100% { opacity: 0.1; transform: scaleX(0.8) translateY(0); }
  50% { opacity: 0.5; transform: scaleX(1.2) translateY(-20px); }
}

@keyframes bluePulse {
  0% { opacity: 0.6; transform: scale(1); }
  100% { opacity: 1; transform: scale(1.1); }
}

/* Perspective Grid Background */
.grid-background {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 50%;
  background-image:
    linear-gradient(rgba(0, 204, 255, 0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 204, 255, 0.15) 1px, transparent 1px);
  background-size: 50px 50px;
  transform: perspective(500px) rotateX(60deg);
  transform-origin: bottom center;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 0 50px; }
}

/* Floating Particles */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  bottom: -10px;
  width: 3px;
  height: 3px;
  background: var(--cyan-primary);
  border-radius: 50%;
  opacity: 0;
  animation: particleFloat 15s linear infinite;
}

@keyframes particleFloat {
  0% {
    opacity: 0;
    transform: translateY(0) translateX(0);
  }
  10% {
    opacity: 0.8;
  }
  90% {
    opacity: 0.8;
  }
  100% {
    opacity: 0;
    transform: translateY(-100vh) translateX(50px);
  }
}

/* Distribute particles horizontally */
.particle:nth-child(1) { left: 10%; }
.particle:nth-child(2) { left: 20%; }
.particle:nth-child(3) { left: 30%; }
.particle:nth-child(4) { left: 40%; }
.particle:nth-child(5) { left: 50%; }
.particle:nth-child(6) { left: 60%; }
.particle:nth-child(7) { left: 70%; }
.particle:nth-child(8) { left: 80%; }

.glass {
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--border-cyan);
  border-radius: 20px;
  box-shadow:
    0 0 40px rgba(0, 204, 255, 0.1),
    0 4px 24px rgba(0, 0, 0, 0.4);
}

/* iOS Glass Card Style */
.ios-glass {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(50px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  position: relative;
  overflow: visible;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.ios-glass:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8),
              0 0 30px rgba(255, 204, 0, 0.12),
              0 0 60px rgba(255, 204, 0, 0.06);
}

/* Border Glow Animation */
.border-glow {
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.4), transparent 40%, rgba(255, 170, 0, 0.1));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  animation: borderBreathe 6s infinite ease-in-out;
  pointer-events: none;
}
.border-glow.blue-tint {
  background: linear-gradient(135deg, rgba(0, 195, 255, 0.55), transparent 45%, rgba(0, 195, 255, 0.15));
}
.border-glow.purple-tint {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.55), transparent 45%, rgba(168, 85, 247, 0.15));
}
.border-glow.slow {
  animation-duration: 8s;
}
@keyframes borderBreathe {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; box-shadow: inset 0 0 15px rgba(255, 170, 0, 0.2); }
}

/* Entrance Animations */
.entrance-slide-in {
  animation: slideInFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateX(-40px);
}
@keyframes slideInFade {
  to { opacity: 1; transform: translateX(0); }
}

.entrance-scale-up {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
  opacity: 0;
}
.entrance-scale-up-delay-1 {
  animation-delay: 0.35s;
}
.entrance-scale-up-delay-2 {
  animation-delay: 0.5s;
}
@keyframes scaleUpFade {
  to { opacity: 1; transform: none; }
}

.entrance-border-glow {
  animation: borderBreathe 6s infinite ease-in-out, borderGlowEnter 1.2s ease-out forwards;
  opacity: 0;
}
@keyframes borderGlowEnter {
  0% { opacity: 0; }
  50% { opacity: 0.6; }
  100% { opacity: 0.3; }
}

.entrance-chart-fade {
  animation: chartFadeIn 1s cubic-bezier(0.16, 1, 0.3, 1) 0.6s forwards;
  opacity: 1;
  transform: none;
}
@keyframes chartFadeIn {
  to { opacity: 1; transform: none; }
}

.entrance-content-fade {
  animation: contentFadeIn 0.8s ease-out 0.8s forwards;
  opacity: 0;
}
@keyframes contentFadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Cell Header */
.cell-header {
  padding: 12px 15px;
  font-size: 12px;
  color: #c0ccda;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.cell-header.compact {
  padding: 10px 15px;
  font-size: 12px;
}

/* Accent Bar */
.accent-bar {
  width: 4px;
  height: 16px;
  background: #ffaa00;
  border-radius: 10px;
  box-shadow: 0 0 10px #ffaa00;
}
.accent-bar.small {
  width: 3px;
  height: 12px;
}
.accent-bar.blue {
  background: #00c3ff;
  box-shadow: 0 0 10px #00c3ff;
}
.accent-bar.purple {
  background: #a855f7;
  box-shadow: 0 0 10px #a855f7;
}
.accent-bar.risk {
  background: #ff4d4f;
  box-shadow: 0 0 10px #ff4d4f;
}
.accent-bar.safe {
  background: #00c3ff;
  box-shadow: 0 0 10px #00c3ff;
}

/* iOS Title */
.ios-title {
  font-size: 32px;
  letter-spacing: -0.5px;
  background: linear-gradient(180deg, #fff 40%, rgba(255,255,255,0.6));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}
.ios-title .subtitle {
  font-size: 14px;
  color: #ffaa00;
  margin-left: 10px;
  font-weight: 300;
  letter-spacing: 2px;
  display: inline-block;
  margin-top: 0;
}

/* Status Tag Dot */
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00ffcc;
  box-shadow: 0 0 10px rgba(0, 255, 204, 0.8);
}
.pulse {
  animation: pulseDot 2s ease-in-out infinite;
}
@keyframes pulseDot {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.5); opacity: 1; }
}

/* Platform Cards */
.platform-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.platform-card > :not(.border-glow) {
  position: relative;
  z-index: 1;
}

.platform-card:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow:
    0 0 45px rgba(0, 204, 255, 0.12),
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 25px rgba(255, 204, 0, 0.08);
}

/* 确保 ios-glass 元素也能放大 */
.ios-glass.platform-card:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow:
    0 0 45px rgba(0, 204, 255, 0.12),
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 25px rgba(255, 204, 0, 0.08);
}
.platform-chart-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 6px 16px 16px;
}

.platform-card.clickable {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.platform-card.clickable:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow:
    0 0 45px rgba(0, 204, 255, 0.12),
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 25px rgba(255, 204, 0, 0.08);
}
.platform-mini-chart {
  width: 96px;
  height: 96px;
  flex-shrink: 0;
}
.platform-data-col {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 0;
}
.header-refresh {
  margin-left: auto;
}
.mini-stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  padding: 6px 10px;
  border-radius: 6px;
}
.mini-stat-row label {
  font-size: 10px;
  color: #8899aa;
}
.mini-stat-row .value {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  font-family: 'SF Mono', monospace;
}
.mini-stat-row .value.has-risk {
  color: #ff4d4f;
  text-shadow: 0 0 8px rgba(255, 77, 79, 0.6);
}
.mini-stat-row .value.normal {
  color: #00c3ff;
}

/* Main Chart Box */
.main-chart-box {
  flex: 1;
  width: 100%;
  min-height: 240px;
  height: 240px;
}

/* Sentiment Summary */
.sentiment-summary {
  flex: 0 0 auto;
  min-height: auto;
}
.summary-grid {
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(0, 204, 255, 0.05);
  border: 1px solid rgba(0, 204, 255, 0.15);
}
.summary-item .label {
  font-size: 10px;
  color: #666666;
  letter-spacing: 0.5px;
}
.summary-item .value {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
}

/* Feed Panel */
.recent-list {
  flex: 1 1 auto;
  min-height: 200px;
  display: flex;
  flex-direction: column;
}
.feed-controls {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 12px 16px 8px;
}
.feed-updated {
  font-size: 0.75rem;
  color: #8899aa;
  letter-spacing: 0.5px;
}

/* Pagination Styles */
.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-cyan);
  flex-wrap: wrap;
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.pagination-wrapper.compact {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  gap: 0.75rem;
}

.pagination-wrapper.centered {
  justify-content: center;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-dim);
  font-size: 0.8rem;
  flex-wrap: wrap;
}

.pagination-divider {
  color: var(--border-cyan);
}

.pagination-text {
  color: var(--text-light);
  font-weight: 500;
  font-size: 0.85rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-controls .pagination-text {
  padding: 0 0.5rem;
  font-size: 0.85rem;
  min-width: 50px;
  text-align: center;
}

/* 图标按钮样式 */
.pagination-btn.icon-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: 1px solid var(--border-cyan);
  background: rgba(0, 204, 255, 0.08);
  color: var(--cyan-primary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.pagination-btn.icon-btn svg {
  width: 18px;
  height: 18px;
}

.pagination-btn.icon-btn:hover:not(:disabled) {
  background: rgba(0, 204, 255, 0.2);
  border-color: var(--glow-cyan);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-1px);
}

.pagination-btn.icon-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 下拉选择框样式 */
.page-size-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding: 0.4rem 2rem 0.4rem 0.7rem;
  border-radius: 8px;
  border: 1px solid var(--border-cyan);
  background: rgba(0, 204, 255, 0.08) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2300ccff' stroke-width='3'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") no-repeat right 8px center;
  color: var(--text-light);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  min-width: 80px;
}

.page-size-select:hover {
  background-color: rgba(0, 204, 255, 0.12);
  border-color: var(--glow-cyan);
}

.page-size-select:focus {
  outline: none;
  border-color: var(--glow-cyan);
  box-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
}

.page-size-select option {
  background: rgba(10, 10, 15, 0.98);
  color: var(--text-light);
  padding: 0.4rem 0.7rem;
}

.page-size-toggle {
  display: inline-flex;
  gap: 0.25rem;
  align-items: center;
}

.page-size-btn {
  min-width: 38px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border-cyan);
  background: rgba(0, 204, 255, 0.05);
  color: var(--text-light);
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.page-size-btn.active {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.4), rgba(0, 204, 255, 0.25));
  border-color: var(--glow-cyan);
  color: var(--text-white);
}

.pagination-btn {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  border: 1px solid var(--border-cyan);
  background: rgba(0, 204, 255, 0.05);
  color: var(--cyan-primary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(0, 204, 255, 0.15);
  border-color: var(--glow-cyan);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-1px);
}

.pagination-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pagination-numbers {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.pagination-number {
  min-width: 36px;
  height: 36px;
  padding: 0;
  border-radius: 8px;
  border: 1px solid var(--border-cyan);
  background: rgba(0, 204, 255, 0.05);
  color: var(--text-light);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-number:hover:not(:disabled):not(.ellipsis) {
  background: rgba(0, 204, 255, 0.15);
  border-color: var(--glow-cyan);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-1px);
}

.pagination-number.active {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.4), rgba(0, 204, 255, 0.25));
  border-color: var(--glow-cyan);
  color: var(--text-white);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.4);
}

.pagination-number.ellipsis {
  border: none;
  background: transparent;
  color: var(--text-dim);
  cursor: default;
}

.pagination-number:disabled {
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 1200px) {
  .layout-wrapper {
    height: auto;
    min-height: 100vh;
  }

  .dashboard-content {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
  }

  .sentiment-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .sentiment-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .layout-wrapper {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .pagination-wrapper {
    flex-direction: column;
    gap: 1rem;
  }

  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }

  .pagination-numbers {
    order: -1;
    width: 100%;
    justify-content: center;
  }
}
</style>
