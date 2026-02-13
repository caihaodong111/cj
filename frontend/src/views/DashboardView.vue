<template>
  <div class="dashboard-view">
    <!-- 顶部概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card glass">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <span class="label">总监测数据</span>
          <span class="value">12,458</span>
          <span class="trend up">+15% 较昨日</span>
        </div>
      </div>
      <div class="stat-card glass">
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <span class="label">敏感舆情</span>
          <span class="value warning">126</span>
          <span class="trend down">-2% 较昨日</span>
        </div>
      </div>
      <div class="stat-card glass">
        <div class="stat-icon">❤️</div>
        <div class="stat-info">
          <span class="label">情感指数</span>
          <span class="value positive">8.4</span>
          <span class="trend up">积极向好</span>
        </div>
      </div>
      <div class="stat-card glass">
        <div class="stat-icon">⚡</div>
        <div class="stat-info">
          <span class="label">实时热度</span>
          <span class="value">High</span>
          <span class="trend">监测中</span>
        </div>
      </div>
    </div>

    <!-- 主要图表区域 -->
    <div class="charts-grid">
      <div class="chart-wrapper wide">
        <ChartCard title="7日舆情声量趋势" :options="trendChartOptions" />
      </div>
      <div class="chart-wrapper">
        <ChartCard title="情感分布占比" :options="pieChartOptions" />
      </div>
    </div>

    <!-- 底部列表 -->
    <div class="recent-list glass">
      <h3>Monitor Feed 实时动态</h3>
      <div class="list-wrapper">
        <div class="list-item" v-for="i in 5" :key="i">
          <span class="platform-tag">小红书</span>
          <span class="content">用户 @TechMaster 发布了关于 "新款 AI 芯片评测" 的帖子...</span>
          <span class="time">2分钟前</span>
          <span class="sentiment negative">中性</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ChartCard from '../components/ChartCard.vue'

// Mock Data Options for Charts
const trendChartOptions = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(0,0,0,0.7)',
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
    axisLine: { lineStyle: { color: '#555' } },
    axisLabel: { color: '#aaa' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#aaa' }
  },
  series: [
    {
      name: '声量',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#FFD700' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(255, 215, 0, 0.5)' }, { offset: 1, color: 'rgba(255, 215, 0, 0)' }]
        }
      },
      emphasis: { focus: 'series' },
      data: [120, 132, 101, 134, 90, 230, 210]
    },
    {
      name: '负面',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#FF4500' },
      areaStyle: { opacity: 0 },
      data: [20, 32, 11, 34, 10, 30, 20]
    }
  ]
}))

const pieChartOptions = computed(() => ({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    bottom: '5%',
    left: 'center',
    textStyle: { color: '#aaa' }
  },
  series: [
    {
      name: 'Sentiment',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#050510',
        borderWidth: 2
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' }
      },
      labelLine: { show: false },
      data: [
        { value: 1048, name: '积极', itemStyle: { color: '#91CC75' } },
        { value: 735, name: '中性', itemStyle: { color: '#5470C6' } },
        { value: 580, name: '消极', itemStyle: { color: '#EE6666' } }
      ]
    }
  ]
}))
</script>

<style scoped>
.dashboard-view {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
  overflow-y: auto;
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
  border-radius: 12px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(255, 215, 0, 0.1);
}

.stat-icon {
  font-size: 2.5rem;
  background: rgba(255, 255, 255, 0.05);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-info .label {
  font-size: 0.85rem;
  color: var(--secondary-color);
  text-transform: uppercase;
}

.stat-info .value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0.2rem 0;
}

.stat-info .value.warning { color: #EE6666; }
.stat-info .value.positive { color: #91CC75; }

.stat-info .trend {
  font-size: 0.75rem;
  color: var(--secondary-color);
}
.stat-info .trend.up { color: #91CC75; }
.stat-info .trend.down { color: #EE6666; }

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
  border-radius: 12px;
  flex: 1;
}

.recent-list h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: var(--primary-color);
}

.list-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid transparent;
}

.list-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 215, 0, 0.2);
}

.platform-tag {
  background: rgba(255, 0, 0, 0.2);
  color: #ffcccc;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
}

.content {
  flex: 1;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-color);
}

.time {
  font-size: 0.8rem;
  color: var(--secondary-color);
}

.sentiment {
  font-size: 0.8rem;
}
.sentiment.negative { color: #5470C6; }
</style>
