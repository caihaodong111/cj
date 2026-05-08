<template>
  <div class="analysis-wrapper">
    <AmbientBackground />

    <div class="analysis-view">
      <header class="page-header entrance-slide-in">
        <div class="title-area">
          <h1 class="ios-title">深度分析<span class="subtitle">Deep Sentiment Analysis</span></h1>
        </div>
      </header>

      <div class="header-filters ios-glass entrance-scale-up">
        <div class="border-glow gold-tint"></div>
        <div class="section-header">
          <span class="accent-bar"></span>
          分析条件
        </div>
        <div class="filters">
          <el-select v-model="selectedTimeRange" class="dark-select filter-select-item" popper-class="analysis-dropdown">
            <el-option label="过去 7 天" value="7" />
            <el-option label="过去 30 天" value="30" />
            <el-option label="自定义时间" value="custom" />
          </el-select>
          <el-select v-model="selectedPlatform" class="dark-select filter-select-item" popper-class="analysis-dropdown">
            <el-option label="所有平台" value="all" />
            <el-option label="小红书" value="xhs" />
            <el-option label="抖音" value="dy" />
            <el-option label="快手" value="ks" />
            <el-option label="B站" value="bili" />
            <el-option label="微博" value="wb" />
            <el-option label="贴吧" value="tieba" />
            <el-option label="知乎" value="zhihu" />
          </el-select>
          <input
            type="text"
            class="search-input"
            v-model="searchKeyword"
            placeholder="输入分析关键词..."
            @keyup.enter="startAnalysis"
          />
          <button class="btn-primary" @click="startAnalysis" :disabled="isAnalyzing">
            {{ isAnalyzing ? '分析中...' : '开始分析' }}
          </button>
        </div>
      </div>

      <div v-if="analysisError" class="analysis-error-banner ios-glass" role="alert">
        {{ analysisError }}
      </div>

      <!-- Word Cloud Section -->
      <section class="analysis-section ios-glass entrance-scale-up-delay-2">
        <div class="border-glow"></div>
        <div class="section-header">
          <span class="accent-bar"></span>
          核心关键词云 <span class="section-subtitle">Keywords</span>
          <span v-if="platformName" class="platform-tag">{{ platformName }}</span>
        </div>
        <div class="word-cloud-container" :class="{ 'loading': isAnalyzing }">
          <div v-if="isAnalyzing" class="loading-overlay">
            <div class="loading-spinner"></div>
            <p>AI 正在分析中...</p>
          </div>
          <div v-else-if="analysisError" class="empty-state error-state">
            <p>{{ analysisError }}</p>
          </div>
          <div v-else-if="keywords.length === 0" class="empty-state">
            <p>请选择分析条件并输入关键词，点击"开始分析"</p>
          </div>
          <span
            v-for="(word, index) in keywords"
            :key="index"
            class="cloud-word"
            :style="{
              fontSize: word.size + 'px',
              top: word.top + '%',
              left: word.left + '%',
              color: word.color,
              animationDelay: index * 0.1 + 's'
            }"
          >
            {{ word.text }}
          </span>
        </div>
      </section>

      <div class="analysis-grid">
        <section class="analysis-card ios-glass entrance-scale-up-delay-3">
          <div class="border-glow blue-tint"></div>
          <div class="section-header">
            <span class="accent-bar"></span>
            事件摘要 <span class="section-subtitle">Summary</span>
          </div>
          <div v-if="isAnalyzing" class="card-loading">AI 正在提炼观点...</div>
          <div v-else-if="analysisError" class="empty-state small error-state">分析失败，本次未生成摘要内容</div>
          <ul v-else-if="summarySentences.length" class="summary-list">
            <li v-for="(sentence, index) in summarySentences" :key="index">{{ sentence }}</li>
          </ul>
          <div v-else class="empty-state small">暂无摘要内容</div>
        </section>

        <section class="analysis-card ios-glass entrance-scale-up-delay-3">
          <div class="border-glow gold-tint"></div>
          <div class="section-header">
            <span class="accent-bar"></span>
            风险提示 <span class="section-subtitle">Risks</span>
          </div>
          <div v-if="isAnalyzing" class="card-loading">AI 正在识别风险...</div>
          <div v-else-if="analysisError" class="empty-state small error-state">分析失败，本次未生成风险提示</div>
          <ul v-else-if="riskTips.length" class="risk-list">
            <li v-for="(risk, index) in riskTips" :key="index">
              <span class="risk-level" :data-level="risk.level">{{ risk.level }}</span>
              <div class="risk-content">
                <strong>{{ risk.trigger }}</strong>
                <p>{{ risk.reason }}</p>
              </div>
            </li>
          </ul>
          <div v-else class="empty-state small">暂无风险提示</div>
        </section>
      </div>

      <div class="charts-row">
        <div class="chart-wrapper ios-glass entrance-scale-up-delay-3">
          <div class="border-glow purple-tint"></div>
          <ChartCard title="情绪分布（平台）" :options="sentimentPlatformOptions" />
        </div>
        <div class="chart-wrapper ios-glass entrance-scale-up-delay-3">
          <div class="border-glow blue-tint"></div>
          <ChartCard title="情绪分布（时间）" :options="sentimentTimeOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AmbientBackground from '../components/AmbientBackground.vue'
import ChartCard from '../components/ChartCard.vue'

// 平台配置
const platformNames = {
  xhs: '小红书',
  dy: '抖音',
  ks: '快手',
  bili: 'B站',
  wb: '微博',
  tieba: '贴吧',
  zhihu: '知乎'
}

// 分析状态
const selectedTimeRange = ref('7')
const selectedPlatform = ref('all')
const searchKeyword = ref('')
const isAnalyzing = ref(false)
const analysisError = ref('')

// 关键词数据
const keywords = ref([])
const summarySentences = ref([])
const riskTips = ref([])
const sentimentByPlatform = ref({})
const sentimentByDay = ref([])

// 平台名称显示
const platformName = computed(() => {
  return selectedPlatform.value === 'all' ? '' : platformNames[selectedPlatform.value]
})

// 颜色生成器
const colors = ['#FFD700', '#FF4500', '#00BFFF', '#32CD32', '#FF69B4', '#FFA500', '#9370DB', '#00CED1', '#FF1493', '#ADFF2F']

// 随机位置生成
const randomPosition = () => ({
  top: Math.random() * 70 + 15,
  left: Math.random() * 80 + 10
})

function resetAnalysisResults() {
  keywords.value = []
  summarySentences.value = []
  riskTips.value = []
  sentimentByPlatform.value = {}
  sentimentByDay.value = []
}

const sentimentColors = {
  positive: '#91CC75',
  neutral: '#5470C6',
  negative: '#EE6666',
  sensitive: '#FAC858'
}

const sentimentPlatformOptions = computed(() => {
  const platformCodes = Object.keys(sentimentByPlatform.value || {}).filter(code => {
    return (sentimentByPlatform.value?.[code]?.total || 0) > 0
  })
  const labels = platformCodes.map(code => platformNames[code] || code)
  const sentimentKeys = ['positive', 'neutral', 'negative', 'sensitive']
  const series = sentimentKeys.map(key => ({
    name: key === 'positive' ? '积极' : key === 'negative' ? '消极' : key === 'neutral' ? '中性' : '敏感',
    type: 'bar',
    stack: 'total',
    data: platformCodes.map(code => sentimentByPlatform.value?.[code]?.[key] || 0),
    itemStyle: { color: sentimentColors[key] }
  }))

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, textStyle: { color: '#aaa' } },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#555' } },
      axisLabel: { color: '#aaa' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#aaa' }
    },
    series
  }
})

const sentimentTimeOptions = computed(() => {
  const rows = sentimentByDay.value || []
  const labels = rows.map(row => row.date)
  const sentimentKeys = ['positive', 'neutral', 'negative', 'sensitive']
  const series = sentimentKeys.map(key => ({
    name: key === 'positive' ? '积极' : key === 'negative' ? '消极' : key === 'neutral' ? '中性' : '敏感',
    type: 'line',
    smooth: true,
    data: rows.map(row => row[key] || 0),
    itemStyle: { color: sentimentColors[key] },
    areaStyle: { opacity: 0.08 }
  }))

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, textStyle: { color: '#aaa' } },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#555' } },
      axisLabel: { color: '#aaa' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#aaa' }
    },
    series
  }
})

// 开始分析
async function startAnalysis() {
  if (!searchKeyword.value.trim()) {
    alert('请输入分析关键词')
    return
  }

  isAnalyzing.value = true
  analysisError.value = ''
  resetAnalysisResults()

  try {
    // 调用后端 API
    const response = await fetch('/api/ai/analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        keyword: searchKeyword.value,
        platform: selectedPlatform.value,
        time_range: selectedTimeRange.value
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'API 请求失败')
    }

    const data = await response.json()

    if (!data.success) {
      throw new Error('分析失败')
    }

    const keywordList = data.keywords || []
    summarySentences.value = data.summary || []
    riskTips.value = data.risks || []
    sentimentByPlatform.value = data.sentiment_distribution?.by_platform || {}
    sentimentByDay.value = data.sentiment_distribution?.by_day || []

    // 生成词云数据
    keywords.value = keywordList.map((text, index) => {
      const size = Math.max(16, 40 - index * 1.5)
      const pos = randomPosition()
      return {
        text: text,
        size: Math.round(size),
        top: pos.top,
        left: pos.left,
        color: colors[index % colors.length]
      }
    })

    // 过滤掉无效的关键词
    keywords.value = keywords.value.filter(w => w.text.length > 0 && w.text.length < 10)

  } catch (error) {
    console.error('分析失败:', error)
    resetAnalysisResults()
    analysisError.value = '分析失败，本次未生成任何结果，请检查网络连接或稍后重试。'
    alert(error.message || '分析失败，请检查网络连接或稍后重试')
  } finally {
    isAnalyzing.value = false
  }
}
</script>


<style scoped src="../styles/views/analysis-view.css"></style>
<style src="../styles/views/analysis-view-global.css"></style>
