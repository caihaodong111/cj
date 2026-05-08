<template>
  <div class="dashboard-wrapper">
    <AmbientBackground />

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
import AmbientBackground from '../components/AmbientBackground.vue'
import { echarts, graphic } from '../utils/echarts'

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

  if (!mainChartRef.value) {
    return
  }

  const chart = initChart('main', mainChartRef.value)
  if (!chart) {
    return
  }


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
}

// Render platform charts
const renderPlatformCharts = () => {
  const platforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu']
  platforms.forEach(platform => {
    const el = platformChartRefs.get(platform)
    if (!el) {
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
            color: graphic.LinearGradient(0, 0, 1, 1, [
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
    return []
  }

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

  return result
}

// 获取情绪类型显示标签（简化为敏感/正常）
const getSentimentLabel = (sentiment) => {
  // sensitive 显示为"敏感"，其他都显示为"正常"
  return sentiment === 'sensitive' ? '敏感' : '正常'
}

// 获取情绪类型样式类名（简化为敏感/正常）
const getSentimentClass = (sentiment) => {
  return sentiment === 'sensitive' ? 'sentiment-sensitive' : 'sentiment-normal'
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

    feedItems.value = merged

    lastUpdatedAt.value = res.data?.fetched_at || new Date()
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


<style scoped src="../styles/views/dashboard-view.css"></style>
