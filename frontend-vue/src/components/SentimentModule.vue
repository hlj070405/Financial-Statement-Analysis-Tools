<template>
  <div class="h-full flex gap-4">
    <div class="flex-1 flex flex-col gap-4">
      <div class="glass-panel p-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
          <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          幻感·舆情溯源引擎
        </h2>
        <p class="text-sm text-gray-500">实时监测市场舆情与热点事件</p>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div class="glass-panel p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">舆情热度</span>
            <div class="w-8 h-8 rounded-lg bg-red-500 flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"/>
              </svg>
            </div>
          </div>
          <div class="text-2xl font-bold text-gray-800">8.7</div>
          <div class="text-xs text-gray-500 mt-1">热度指数</div>
        </div>

        <div class="glass-panel p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">正面情绪</span>
            <div class="w-8 h-8 rounded-lg bg-green-500 flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
          <div class="text-2xl font-bold text-gray-800">72%</div>
          <div class="text-xs text-gray-500 mt-1">情感占比</div>
        </div>

        <div class="glass-panel p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">关联事件</span>
            <div class="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/>
              </svg>
            </div>
          </div>
          <div class="text-2xl font-bold text-gray-800">156</div>
          <div class="text-xs text-gray-500 mt-1">24小时内</div>
        </div>
      </div>

      <div class="flex-1 glass-panel p-4 flex flex-col">
        <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          热点事件时间线
        </h3>
        <div class="flex-1 overflow-y-auto space-y-3">
          <div v-for="event in events" :key="event.id" class="relative pl-6 pb-3 border-l-2 border-gray-200 last:border-0">
            <div class="absolute -left-2 top-0 w-4 h-4 rounded-full" :class="event.levelColor"></div>
            <div class="bg-white/50 p-3 rounded-lg border border-gray-200">
              <div class="flex items-start justify-between mb-1">
                <span class="text-sm font-medium text-gray-800">{{ event.title }}</span>
                <span :class="['text-xs px-2 py-0.5 rounded', event.sentimentClass]">
                  {{ event.sentiment }}
                </span>
              </div>
              <p class="text-xs text-gray-600 mb-2">{{ event.description }}</p>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>{{ event.source }}</span>
                <span>{{ event.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="w-96 flex flex-col gap-4">
      <div class="glass-panel p-4">
        <h3 class="text-sm font-semibold text-gray-800 mb-3">热词云</h3>
        <div class="flex flex-wrap gap-2">
          <span v-for="word in hotWords" :key="word.text" 
            :class="['px-3 py-1 rounded-full text-white cursor-pointer hover:opacity-80 transition', word.color]"
            :style="{ fontSize: word.size + 'px' }"
          >
            {{ word.text }}
          </span>
        </div>
      </div>

      <div class="glass-panel p-4 flex-1 flex flex-col">
        <h3 class="text-sm font-semibold text-gray-800 mb-3">舆情来源分布</h3>
        <div ref="sourceChart" class="flex-1"></div>
      </div>

      <div class="glass-panel p-4">
        <h3 class="text-sm font-semibold text-gray-800 mb-3">风险预警</h3>
        <div class="space-y-2">
          <div v-for="warning in warnings" :key="warning.id" 
            :class="['p-3 rounded-lg border-l-4', warning.levelClass]"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-800">{{ warning.title }}</span>
              <span :class="['text-xs px-2 py-0.5 rounded', warning.badgeClass]">
                {{ warning.level }}
              </span>
            </div>
            <p class="text-xs text-gray-600">{{ warning.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const sourceChart = ref(null)

const events = ref([
  {
    id: 1,
    title: '比亚迪发布2023年财报',
    description: '净利润同比增长81.4%，营收突破600亿元大关',
    source: '财经网',
    time: '2小时前',
    sentiment: '正面',
    sentimentClass: 'bg-green-100 text-green-700',
    levelColor: 'bg-green-500'
  },
  {
    id: 2,
    title: '固态电池技术突破引发关注',
    description: '多家新能源车企宣布固态电池研发进展，市场反应积极',
    source: '新浪财经',
    time: '5小时前',
    sentiment: '正面',
    sentimentClass: 'bg-green-100 text-green-700',
    levelColor: 'bg-blue-500'
  },
  {
    id: 3,
    title: '原材料价格波动预警',
    description: '锂矿价格出现较大波动，可能影响电池成本',
    source: '第一财经',
    time: '8小时前',
    sentiment: '负面',
    sentimentClass: 'bg-red-100 text-red-700',
    levelColor: 'bg-orange-500'
  },
  {
    id: 4,
    title: '新能源汽车销量创新高',
    description: '1月份新能源汽车销量同比增长35%',
    source: '证券时报',
    time: '12小时前',
    sentiment: '正面',
    sentimentClass: 'bg-green-100 text-green-700',
    levelColor: 'bg-green-500'
  },
  {
    id: 5,
    title: '行业政策调整讨论',
    description: '补贴政策可能进一步调整，行业关注度提升',
    source: '经济观察报',
    time: '1天前',
    sentiment: '中性',
    sentimentClass: 'bg-gray-100 text-gray-700',
    levelColor: 'bg-gray-400'
  }
])

const hotWords = ref([
  { text: '新能源', size: 16, color: 'bg-blue-500' },
  { text: '固态电池', size: 14, color: 'bg-purple-500' },
  { text: '财报', size: 13, color: 'bg-green-500' },
  { text: '销量', size: 12, color: 'bg-orange-500' },
  { text: '技术突破', size: 11, color: 'bg-pink-500' },
  { text: '市场份额', size: 11, color: 'bg-indigo-500' },
  { text: '智能驾驶', size: 10, color: 'bg-teal-500' },
  { text: '产能', size: 10, color: 'bg-cyan-500' }
])

const warnings = ref([
  {
    id: 1,
    title: '原材料价格风险',
    description: '锂矿价格波动可能影响利润率',
    level: '中风险',
    levelClass: 'border-orange-500 bg-orange-50',
    badgeClass: 'bg-orange-100 text-orange-700'
  },
  {
    id: 2,
    title: '市场竞争加剧',
    description: '多家车企推出新车型，竞争压力增大',
    level: '低风险',
    levelClass: 'border-yellow-500 bg-yellow-50',
    badgeClass: 'bg-yellow-100 text-yellow-700'
  }
])

onMounted(() => {
  initSourceChart()
})

const initSourceChart = () => {
  const chart = echarts.init(sourceChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#374151' }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          fontSize: 11,
          formatter: '{b}: {d}%'
        },
        data: [
          { value: 335, name: '社交媒体', itemStyle: { color: '#3b82f6' } },
          { value: 234, name: '财经媒体', itemStyle: { color: '#8b5cf6' } },
          { value: 154, name: '行业报告', itemStyle: { color: '#10b981' } },
          { value: 135, name: '官方公告', itemStyle: { color: '#f59e0b' } }
        ]
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}
</script>
