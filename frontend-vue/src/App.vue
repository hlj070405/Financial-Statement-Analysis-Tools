<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
      <header class="mb-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-2">📊 企业财报智能分析系统</h1>
        <p class="text-gray-600">基于 AI 智能体的财报分析与决策支持</p>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左侧：上传区域 -->
        <UploadArea 
          @file-uploaded="handleFileUploaded"
          @analyze="handleAnalyze"
          :is-analyzing="isAnalyzing"
        />

        <!-- 右侧：分析结果 -->
        <ResultDisplay 
          :result="analysisResult"
          :is-loading="isAnalyzing"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UploadArea from './components/UploadArea.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import { analyzeDocumentStream } from './api/analysis'

const isAnalyzing = ref(false)
const analysisResult = ref('')
const currentFileId = ref(null)

const handleFileUploaded = (fileId) => {
  currentFileId.value = fileId
  analysisResult.value = ''
}

const handleAnalyze = async ({ question, style }) => {
  if (!currentFileId.value) {
    alert('请先上传文件')
    return
  }

  isAnalyzing.value = true
  analysisResult.value = ''

  try {
    await analyzeDocumentStream(
      {
        file_id: currentFileId.value,
        question,
        style
      },
      // onChunk - 接收文本块
      (chunk) => {
        analysisResult.value += chunk
      },
      // onDone - 完成
      (data) => {
        console.log('分析完成，总长度:', data.total_length)
        isAnalyzing.value = false
      },
      // onError - 错误
      (error) => {
        alert('分析失败: ' + error)
        isAnalyzing.value = false
      }
    )
  } catch (error) {
    alert('分析失败: ' + error.message)
    isAnalyzing.value = false
  }
}
</script>
