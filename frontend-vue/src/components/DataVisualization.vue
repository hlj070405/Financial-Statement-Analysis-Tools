<template>
  <div class="h-full flex flex-col gap-4">
    <div class="grid grid-cols-4 gap-4">
      <div v-for="metric in metrics" :key="metric.title" class="glass-panel p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-600">{{ metric.title }}</span>
          <div :class="['w-8 h-8 rounded-lg flex items-center justify-center', metric.bgColor]">
            <component :is="metric.icon" class="w-4 h-4 text-white" />
          </div>
        </div>
        <div class="text-2xl font-bold text-gray-800">{{ metric.value }}</div>
        <div class="flex items-center mt-2 text-xs">
          <span :class="metric.trend === 'up' ? 'text-green-600' : 'text-red-600'" class="flex items-center">
            <svg v-if="metric.trend === 'up'" class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
            </svg>
            <svg v-else class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
            </svg>
            {{ metric.change }}
          </span>
          <span class="text-gray-500 ml-2">vs 去年同期</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4 flex-1">
      <div class="glass-panel p-4 flex flex-col">
        <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
          </svg>
          营收与利润趋势
        </h3>
        <div ref="revenueChart" class="flex-1"></div>
      </div>

      <div class="glass-panel p-4 flex flex-col">
        <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/>
          </svg>
          业务结构分析
        </h3>
        <div ref="pieChart" class="flex-1"></div>
      </div>

      <div class="glass-panel p-4 flex flex-col">
        <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          财务指标对比
        </h3>
        <div ref="barChart" class="flex-1"></div>
      </div>

      <div class="glass-panel p-4 flex flex-col">
        <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
          </svg>
          风险评估雷达图
        </h3>
        <div ref="radarChart" class="flex-1"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const revenueChart = ref(null)
const pieChart = ref(null)
const barChart = ref(null)
const radarChart = ref(null)

const metrics = ref([
  {
    title: '总营收',
    value: '¥602.3亿',
    change: '+23.5%',
    trend: 'up',
    bgColor: 'bg-blue-500',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      `
    }
  },
  {
    title: '净利润',
    value: '¥166.2亿',
    change: '+81.4%',
    trend: 'up',
    bgColor: 'bg-green-500',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
        </svg>
      `
    }
  },
  {
    title: 'ROE',
    value: '27.6%',
    change: '+5.2%',
    trend: 'up',
    bgColor: 'bg-purple-500',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
      `
    }
  },
  {
    title: '资产负债率',
    value: '58.3%',
    change: '-2.1%',
    trend: 'down',
    bgColor: 'bg-orange-500',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"/>
        </svg>
      `
    }
  }
])

onMounted(() => {
  initRevenueChart()
  initPieChart()
  initBarChart()
  initRadarChart()
})

const initRevenueChart = () => {
  const chart = echarts.init(revenueChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#374151' }
    },
    legend: {
      data: ['营收', '净利润'],
      bottom: 0,
      textStyle: { fontSize: 11 }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['2019', '2020', '2021', '2022', '2023'],
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    series: [
      {
        name: '营收',
        type: 'line',
        data: [277, 156, 216, 424, 602],
        smooth: true,
        lineStyle: { width: 3, color: '#3b82f6' },
        itemStyle: { color: '#3b82f6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
          ])
        }
      },
      {
        name: '净利润',
        type: 'line',
        data: [16, 42, 30, 92, 166],
        smooth: true,
        lineStyle: { width: 3, color: '#10b981' },
        itemStyle: { color: '#10b981' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
          ])
        }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initPieChart = () => {
  const chart = echarts.init(pieChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#374151' }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { fontSize: 11 }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: 335, name: '新能源汽车', itemStyle: { color: '#3b82f6' } },
          { value: 234, name: '电池业务', itemStyle: { color: '#8b5cf6' } },
          { value: 154, name: '电子产品', itemStyle: { color: '#10b981' } },
          { value: 135, name: '其他业务', itemStyle: { color: '#f59e0b' } }
        ]
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initBarChart = () => {
  const chart = echarts.init(barChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#374151' }
    },
    legend: {
      data: ['比亚迪', '特斯拉', '宁德时代'],
      bottom: 0,
      textStyle: { fontSize: 11 }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['ROE', '毛利率', '净利率', '资产周转率'],
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    series: [
      {
        name: '比亚迪',
        type: 'bar',
        data: [27.6, 21.9, 27.6, 1.42],
        itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '特斯拉',
        type: 'bar',
        data: [23.1, 25.6, 15.5, 0.89],
        itemStyle: { color: '#8b5cf6', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '宁德时代',
        type: 'bar',
        data: [19.8, 22.4, 16.8, 1.12],
        itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initRadarChart = () => {
  const chart = echarts.init(radarChart.value)
  const option = {
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#e5e7eb',
      textStyle: { color: '#374151' }
    },
    legend: {
      data: ['当前评分', '行业平均'],
      bottom: 0,
      textStyle: { fontSize: 11 }
    },
    radar: {
      indicator: [
        { name: '盈利能力', max: 100 },
        { name: '偿债能力', max: 100 },
        { name: '运营能力', max: 100 },
        { name: '成长能力', max: 100 },
        { name: '市场地位', max: 100 }
      ],
      splitArea: {
        areaStyle: {
          color: ['rgba(59, 130, 246, 0.05)', 'rgba(139, 92, 246, 0.05)']
        }
      },
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      splitLine: { lineStyle: { color: '#e5e7eb' } }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [85, 72, 88, 92, 78],
            name: '当前评分',
            areaStyle: { color: 'rgba(59, 130, 246, 0.3)' },
            lineStyle: { color: '#3b82f6', width: 2 },
            itemStyle: { color: '#3b82f6' }
          },
          {
            value: [70, 65, 75, 68, 72],
            name: '行业平均',
            areaStyle: { color: 'rgba(139, 92, 246, 0.2)' },
            lineStyle: { color: '#8b5cf6', width: 2 },
            itemStyle: { color: '#8b5cf6' }
          }
        ]
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}
</script>
