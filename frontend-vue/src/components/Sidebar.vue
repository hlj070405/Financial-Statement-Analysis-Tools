<template>
  <aside class="w-72 bg-white/80 backdrop-blur-md border-r border-gray-200/50 flex flex-col shadow-lg">
    <div class="p-6 border-b border-gray-200/50">
      <div class="flex items-center space-x-3">
        <div class="relative">
          <div class="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 rounded-lg blur-md opacity-40"></div>
          <div class="relative w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20 backdrop-blur-md border border-white/30 flex items-center justify-center">
            <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
          </div>
        </div>
        <div>
          <h1 class="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            幻流
          </h1>
          <p class="text-xs text-gray-500">Phantom Flow</p>
        </div>
      </div>
    </div>

    <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
      <button
        v-for="item in menuItems"
        :key="item.id"
        @click="$emit('change-module', item.id)"
        :class="[
          'w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200',
          activeModule === item.id
            ? 'bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 border border-purple-200 shadow-sm'
            : 'hover:bg-gray-100/50'
        ]"
      >
        <div :class="[
          'w-10 h-10 rounded-lg flex items-center justify-center transition-all',
          activeModule === item.id
            ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20'
            : 'bg-gray-100'
        ]">
          <component :is="item.icon" :class="[
            'w-5 h-5',
            activeModule === item.id ? 'text-purple-600' : 'text-gray-600'
          ]" />
        </div>
        <div class="flex-1 text-left">
          <div :class="[
            'font-medium text-sm',
            activeModule === item.id ? 'text-gray-900' : 'text-gray-700'
          ]">
            {{ item.title }}
          </div>
          <div class="text-xs text-gray-500">{{ item.subtitle }}</div>
        </div>
        <div v-if="activeModule === item.id" class="w-1 h-8 bg-gradient-to-b from-blue-500 via-purple-500 to-pink-500 rounded-full"></div>
      </button>
    </nav>

    <div class="p-4 border-t border-gray-200/50">
      <div class="glass-panel p-3">
        <div class="flex items-center space-x-2 mb-2">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-xs font-medium text-gray-700">系统状态</span>
        </div>
        <div class="space-y-1 text-xs text-gray-600">
          <div class="flex justify-between">
            <span>AI引擎</span>
            <span class="text-green-600">正常</span>
          </div>
          <div class="flex justify-between">
            <span>数据源</span>
            <span class="text-green-600">在线</span>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  activeModule: {
    type: String,
    default: 'chat'
  }
})

defineEmits(['change-module'])

const menuItems = [
  {
    id: 'chat',
    title: '幻思·智能咨询',
    subtitle: '企业智能问答',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
      `
    }
  },
  {
    id: 'logic',
    title: '幻化·逻辑流',
    subtitle: '决策链可视化',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
      `
    }
  },
  {
    id: 'data',
    title: '幻诊·运营评估',
    subtitle: '财务数据分析',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
      `
    }
  },
  {
    id: 'sentiment',
    title: '幻感·舆情溯源',
    subtitle: '实时舆情监测',
    icon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      `
    }
  }
]
</script>
