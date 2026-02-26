<template>
  <header class="h-16 bg-white/80 backdrop-blur-md border-b border-gray-200/50 flex items-center justify-between px-6 shadow-sm">
    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2">
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input 
          type="text" 
          placeholder="搜索企业、财报、分析报告..."
          class="w-96 px-3 py-2 bg-gray-100/50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition"
        />
      </div>
    </div>

    <div class="flex items-center space-x-4">
      <button class="relative p-2 hover:bg-gray-100 rounded-lg transition">
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
        <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
      </button>

      <button class="p-2 hover:bg-gray-100 rounded-lg transition">
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </button>

      <div class="h-8 w-px bg-gray-200"></div>

      <div class="flex items-center space-x-3">
        <div class="text-right">
          <div class="text-sm font-medium text-gray-700">{{ userName }}</div>
          <div class="text-xs text-gray-500">{{ userRole }}</div>
        </div>
        <div class="relative group">
          <button class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-medium">
            {{ userInitial }}
          </button>
          <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
            <div class="p-3 border-b border-gray-100">
              <div class="text-sm font-medium text-gray-700">{{ userName }}</div>
              <div class="text-xs text-gray-500">{{ userEmail }}</div>
            </div>
            <div class="p-2">
              <button class="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded transition flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                <span>个人资料</span>
              </button>
              <button class="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded transition flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
                </svg>
                <span>偏好设置</span>
              </button>
              <div class="border-t border-gray-100 my-2"></div>
              <button 
                @click="$emit('logout')"
                class="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded transition flex items-center space-x-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
                <span>退出登录</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { defineEmits } from 'vue'

defineEmits(['logout'])

const userName = ref('分析师')
const userEmail = ref('analyst@phantomflow.com')
const userRole = ref('金融分析师')

const userInitial = computed(() => {
  return userName.value.charAt(0).toUpperCase()
})

onMounted(() => {
  const user = localStorage.getItem('user')
  if (user) {
    try {
      const userData = JSON.parse(user)
      userName.value = userData.username || '分析师'
      userEmail.value = userData.email || 'analyst@phantomflow.com'
      userRole.value = userData.role || '金融分析师'
    } catch (e) {
      console.error('解析用户信息失败:', e)
    }
  }
})
</script>
