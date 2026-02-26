<template>
  <div class="h-screen w-screen overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 flex">
    <Sidebar :activeModule="activeModule" @change-module="changeModule" />
    
    <div class="flex-1 flex flex-col overflow-hidden">
      <TopBar @logout="handleLogout" />
      
      <main class="flex-1 overflow-hidden p-6">
        <transition name="fade" mode="out-in">
          <component :is="currentComponent" :key="activeModule" />
        </transition>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '../components/Sidebar.vue'
import TopBar from '../components/TopBar.vue'
import ChatModule from '../components/ChatModule.vue'
import LogicFlowModule from '../components/LogicFlowModule.vue'
import DataVisualization from '../components/DataVisualization.vue'
import SentimentModule from '../components/SentimentModule.vue'

const router = useRouter()
const activeModule = ref('chat')

const components = {
  chat: ChatModule,
  logic: LogicFlowModule,
  data: DataVisualization,
  sentiment: SentimentModule
}

const currentComponent = computed(() => components[activeModule.value])

const changeModule = (module) => {
  activeModule.value = module
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  router.push('/')
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
