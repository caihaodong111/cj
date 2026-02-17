<template>
  <div class="analysis-wrapper">
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
  summarySentences.value = []
  riskTips.value = []
  sentimentByPlatform.value = {}
  sentimentByDay.value = []

  try {
    // 调用后端 API
    const response = await fetch('http://localhost:8000/api/ai/analysis', {
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
    alert(error.message || '分析失败，请检查网络连接或稍后重试')
    // 失败时使用模拟数据
    generateMockAnalysis()
  } finally {
    isAnalyzing.value = false
  }
}

// 生成模拟分析结果（当 API 调用失败时使用）
function generateMockAnalysis() {
  const mockKeywords = [
    { text: searchKeyword.value + '热度', size: 40 },
    { text: '用户讨论', size: 35 },
    { text: '情感倾向', size: 32 },
    { text: '话题趋势', size: 30 },
    { text: '关注度', size: 28 },
    { text: '传播效果', size: 26 },
    { text: '互动数据', size: 24 },
    { text: '用户反馈', size: 22 },
    { text: '内容分析', size: 20 },
    { text: '影响力', size: 18 }
  ]

  keywords.value = mockKeywords.map((kw, index) => {
    const pos = randomPosition()
    return {
      ...kw,
      top: pos.top,
      left: pos.left,
      color: colors[index % colors.length]
    }
  })

  summarySentences.value = [
    '当前关键词讨论集中在用户体验与产品口碑。',
    '正向评价略占优势，但仍存在部分质疑声音。',
    '建议持续关注高热话题与关键平台反馈。'
  ]

  riskTips.value = [
    { level: 'low', trigger: '风险信号较弱', reason: '未出现明显的负面聚集趋势。' }
  ]

  sentimentByPlatform.value = {}
  sentimentByDay.value = []
}
</script>

<style scoped>
.analysis-wrapper {
  min-height: 100vh;
  background: #050510;
  position: relative;
  overflow: hidden;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
}

.ambient-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

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

.breathing-line {
  position: absolute;
  height: 1px;
  background: linear-gradient(90deg, transparent, #ffaa00, transparent);
  filter: blur(1px);
  opacity: 0.3;
  animation: breathe 8s infinite ease-in-out;
}

.gold-1 { width: 100%; top: 30%; left: -50%; transform: rotate(-5deg); }
.gold-2 { width: 100%; bottom: 20%; right: -50%; transform: rotate(3deg); animation-delay: -4s; }

@keyframes breathe {
  0%, 100% { opacity: 0.1; transform: scaleX(0.8) translateY(0); }
  50% { opacity: 0.5; transform: scaleX(1.2) translateY(-20px); }
}

.scan-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: linear-gradient(to bottom, black, transparent);
  animation: gridMove 25s linear infinite;
}

@keyframes gridMove {
  from { background-position: 0 0; }
  to { background-position: 0 50px; }
}

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
  background: #00ccff;
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

.particle:nth-child(1) { left: 10%; }
.particle:nth-child(2) { left: 20%; }
.particle:nth-child(3) { left: 30%; }
.particle:nth-child(4) { left: 40%; }
.particle:nth-child(5) { left: 50%; }
.particle:nth-child(6) { left: 60%; }
.particle:nth-child(7) { left: 70%; }
.particle:nth-child(8) { left: 80%; }

.analysis-view {
  position: relative;
  z-index: 1;
  padding: 32px 40px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  position: relative;
  z-index: 3;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 204, 255, 0.2);
}

.title-area {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ios-title {
  font-size: 32px;
  letter-spacing: -0.5px;
  background: linear-gradient(180deg, #fff 40%, rgba(255, 255, 255, 0.6));
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

.ios-glass {
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(50px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  position: relative;
  overflow: visible;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.ios-glass > :not(.border-glow) {
  position: relative;
  z-index: 1;
}

.ios-glass:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8),
              0 0 30px rgba(255, 204, 0, 0.12),
              0 0 60px rgba(255, 204, 0, 0.06);
}

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

.border-glow.gold-tint {
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.55), transparent 45%, rgba(255, 170, 0, 0.15));
}

@keyframes borderBreathe {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; box-shadow: inset 0 0 15px rgba(255, 170, 0, 0.2); }
}

.entrance-slide-in {
  animation: slideInFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateX(-40px);
}

.entrance-scale-up {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.entrance-scale-up-delay-2 {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.4s forwards;
  opacity: 0;
  transform: scale(0.95) translateY(24px);
}

.entrance-scale-up-delay-3 {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.6s forwards;
  opacity: 0;
  transform: scale(0.92) translateY(30px);
}

@keyframes slideInFade {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleUpFade {
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.header-filters {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.75);
}

.section-subtitle {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.45);
  margin-left: 8px;
  letter-spacing: 1px;
}

.accent-bar {
  width: 4px;
  height: 18px;
  border-radius: 999px;
  background: linear-gradient(180deg, #ffaa00, #ff6a00);
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-select-item {
  width: 140px;
}

/* === Dark Select Styles === */
:deep(.dark-select .el-select__wrapper) {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  box-shadow: none;
  padding: 4px 12px;
  min-height: 36px;
  transition: all 0.2s ease;
}

:deep(.dark-select .el-select__wrapper:hover) {
  border-color: rgba(255, 170, 0, 0.3);
}

:deep(.dark-select .el-select__wrapper.is-focus) {
  border-color: #ffaa00;
}

:deep(.dark-select .el-select__selected-item) {
  color: #fff;
  font-size: 0.85rem;
  line-height: 1.5;
}

:deep(.dark-select .el-select__placeholder) {
  color: #8899aa;
  font-size: 0.85rem;
}

:deep(.dark-select .el-select__suffix) {
  color: #8899aa;
}

:deep(.dark-select.is-focus .el-select__suffix) {
  color: #ffaa00;
}

.search-input {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
  padding: 0.6rem 1rem;
  border-radius: 999px;
  outline: none;
  min-width: 200px;
  transition: all 0.3s ease;
}

.search-input:hover {
  border-color: rgba(255, 170, 0, 0.3);
}

.search-input:focus {
  border-color: rgba(255, 170, 0, 0.5);
  background: rgba(0, 0, 0, 0.45);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.btn-primary {
  background: linear-gradient(135deg, #ffaa00, #ff6a00);
  border: none;
  color: #000;
  padding: 0.6rem 1.5rem;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(255, 170, 0, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.platform-tag {
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  background: rgba(255, 170, 0, 0.2);
  border: 1px solid rgba(255, 170, 0, 0.4);
  border-radius: 999px;
  font-size: 0.75rem;
  color: #ffaa00;
}

.word-cloud-container.loading {
  position: relative;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  z-index: 10;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 170, 0, 0.2);
  border-top-color: #ffaa00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  margin-top: 16px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.9rem;
}

.analysis-section {
  padding: 20px 24px;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.analysis-card {
  padding: 20px 24px;
  min-height: 240px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.summary-list {
  margin: 0;
  padding-left: 18px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
}

.summary-list li + li {
  margin-top: 8px;
}

.risk-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.risk-list li {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.risk-level {
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 1px;
  padding: 4px 8px;
  border-radius: 10px;
  height: fit-content;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.85);
}

.risk-level[data-level="high"] {
  background: rgba(238, 102, 102, 0.2);
  color: #ff8b8b;
}

.risk-level[data-level="medium"] {
  background: rgba(250, 200, 88, 0.2);
  color: #fbd38d;
}

.risk-level[data-level="low"] {
  background: rgba(145, 204, 117, 0.18);
  color: #b7f0a3;
}

.risk-content strong {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.risk-content p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  line-height: 1.4;
}

.card-loading {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.empty-state.small {
  font-size: 0.85rem;
  height: auto;
  padding: 12px 0;
}

.word-cloud-container {
  flex: 1;
  position: relative;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.cloud-word {
  position: absolute;
  transform: translate(-50%, -50%);
  font-weight: bold;
  opacity: 0;
  animation: fadeIn 0.5s ease-out forwards;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
  cursor: default;
  transition: transform 0.3s;
}

.cloud-word:hover {
  transform: translate(-50%, -50%) scale(1.2);
  z-index: 10;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  min-height: 360px;
}

.chart-wrapper {
  padding: 12px;
}

</style>

<style>
/* ==========================================================================
   Element Plus 下拉菜单全局样式 - 透明玻璃质感（非 scoped）
   ========================================================================== */

/* --- 1. Popper 容器覆盖 --- */
.analysis-dropdown.el-popper {
  background-color: rgba(20, 25, 35, 0.75) !important;
  backdrop-filter: blur(40px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 20px !important;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
  z-index: 9999 !important;
}

/* --- 2. 下拉菜单容器 --- */
.analysis-dropdown .el-select-dropdown {
  background-color: transparent !important;
  backdrop-filter: none !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  padding: 0 !important;
  margin-top: 0 !important;
}

.analysis-dropdown .el-select-dropdown__wrap {
  background-color: transparent !important;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

.analysis-dropdown .el-select-dropdown__wrap::-webkit-scrollbar {
  width: 4px;
}

.analysis-dropdown .el-select-dropdown__wrap::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.analysis-dropdown .el-select-dropdown__wrap::-webkit-scrollbar-track {
  background: transparent;
}

.analysis-dropdown .el-popper__arrow {
  display: none !important;
}

/* --- 3. 选项列表项 --- */
.analysis-dropdown .el-select-dropdown__list {
  background-color: transparent !important;
  padding: 6px 8px !important;
}

.analysis-dropdown .el-select-dropdown__item {
  color: #8da0b7 !important;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
  font-size: 13px !important;
  height: 36px !important;
  line-height: 36px !important;
  margin: 1px 4px !important;
  border-radius: 8px !important;
  padding: 0 12px !important;
  transition: all 0.15s ease !important;
  font-weight: 400 !important;
}

.analysis-dropdown .el-select-dropdown__item.hover,
.analysis-dropdown .el-select-dropdown__item:hover {
  background-color: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff !important;
}

.analysis-dropdown .el-select-dropdown__item.is-selected {
  background: rgba(255, 170, 0, 0.15) !important;
  color: #ffaa00 !important;
  font-weight: 500 !important;
}

.analysis-dropdown .el-select-dropdown__item.is-disabled {
  color: rgba(255, 255, 255, 0.2) !important;
  pointer-events: none;
}
</style>
