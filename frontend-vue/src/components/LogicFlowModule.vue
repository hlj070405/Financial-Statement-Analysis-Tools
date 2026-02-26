<template>
  <div class="h-full flex flex-col glass-panel">
    <div class="p-4 border-b border-gray-200/50">
      <h2 class="text-lg font-semibold text-gray-800 flex items-center">
        <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
        幻化·逻辑流可视化
      </h2>
      <p class="text-sm text-gray-500 mt-1">AI决策推理链路的可视化展示</p>
    </div>

    <div class="flex-1 relative bg-gradient-to-br from-slate-50 to-blue-50">
      <VueFlow
        v-model="elements"
        :default-zoom="1"
        :min-zoom="0.2"
        :max-zoom="4"
        class="vue-flow-custom"
      >
        <Background pattern-color="#aaa" :gap="16" />
        <Controls />
        <MiniMap />
      </VueFlow>

      <div class="absolute top-4 right-4 glass-panel p-4 w-64 space-y-3">
        <div>
          <h3 class="text-sm font-semibold text-gray-800 mb-2">推理统计</h3>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between">
              <span class="text-gray-600">推理节点</span>
              <span class="font-medium text-gray-800">{{ nodeCount }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">数据源调用</span>
              <span class="font-medium text-gray-800">{{ dataSourceCount }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">推理深度</span>
              <span class="font-medium text-gray-800">{{ reasoningDepth }} 层</span>
            </div>
          </div>
        </div>

        <div class="border-t border-gray-200 pt-3">
          <h3 class="text-sm font-semibold text-gray-800 mb-2">节点类型</h3>
          <div class="space-y-2">
            <div class="flex items-center text-xs">
              <div class="w-3 h-3 rounded bg-blue-500 mr-2"></div>
              <span class="text-gray-700">数据检索</span>
            </div>
            <div class="flex items-center text-xs">
              <div class="w-3 h-3 rounded bg-purple-500 mr-2"></div>
              <span class="text-gray-700">逻辑推理</span>
            </div>
            <div class="flex items-center text-xs">
              <div class="w-3 h-3 rounded bg-green-500 mr-2"></div>
              <span class="text-gray-700">结果生成</span>
            </div>
            <div class="flex items-center text-xs">
              <div class="w-3 h-3 rounded bg-orange-500 mr-2"></div>
              <span class="text-gray-700">风险评估</span>
            </div>
          </div>
        </div>

        <button class="w-full px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg text-sm font-medium hover:from-blue-600 hover:to-purple-600 transition">
          导出推理图
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'

const elements = ref([
  {
    id: '1',
    type: 'input',
    label: '用户查询\n分析比亚迪财务状况',
    position: { x: 250, y: 50 },
    style: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '12px',
      fontSize: '12px',
      fontWeight: '500'
    }
  },
  {
    id: '2',
    label: '检索财报数据\n2023年年报',
    position: { x: 100, y: 150 },
    style: {
      background: '#3b82f6',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '11px'
    }
  },
  {
    id: '3',
    label: '检索行业数据\n新能源汽车行业',
    position: { x: 400, y: 150 },
    style: {
      background: '#3b82f6',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '11px'
    }
  },
  {
    id: '4',
    label: '财务指标计算\nROE, 毛利率等',
    position: { x: 100, y: 250 },
    style: {
      background: '#8b5cf6',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '11px'
    }
  },
  {
    id: '5',
    label: '行业对标分析\n与竞品对比',
    position: { x: 400, y: 250 },
    style: {
      background: '#8b5cf6',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '11px'
    }
  },
  {
    id: '6',
    label: '风险评估\n识别潜在风险',
    position: { x: 250, y: 350 },
    style: {
      background: '#f97316',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '11px'
    }
  },
  {
    id: '7',
    type: 'output',
    label: '生成分析报告\n综合评估结果',
    position: { x: 250, y: 450 },
    style: {
      background: '#10b981',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '12px',
      fontSize: '12px',
      fontWeight: '500'
    }
  },
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#3b82f6' } },
  { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#3b82f6' } },
  { id: 'e2-4', source: '2', target: '4', animated: true, style: { stroke: '#8b5cf6' } },
  { id: 'e3-5', source: '3', target: '5', animated: true, style: { stroke: '#8b5cf6' } },
  { id: 'e4-6', source: '4', target: '6', animated: true, style: { stroke: '#f97316' } },
  { id: 'e5-6', source: '5', target: '6', animated: true, style: { stroke: '#f97316' } },
  { id: 'e6-7', source: '6', target: '7', animated: true, style: { stroke: '#10b981' } }
])

const nodeCount = computed(() => {
  return elements.value.filter(el => !el.source).length
})

const dataSourceCount = computed(() => {
  return elements.value.filter(el => el.label && el.label.includes('检索')).length
})

const reasoningDepth = computed(() => {
  return 4
})
</script>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
@import '@vue-flow/controls/dist/style.css';
@import '@vue-flow/minimap/dist/style.css';

.vue-flow-custom {
  background: linear-gradient(to bottom right, #f8fafc, #eff6ff);
}
</style>
