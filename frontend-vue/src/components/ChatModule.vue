<template>
  <div class="h-full flex gap-4">
    <div class="flex-1 flex flex-col glass-panel">
      <div class="p-4 border-b border-gray-200/50">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center">
          <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
          </svg>
          幻思·智能企业咨询
        </h2>
        <p class="text-sm text-gray-500 mt-1">基于多源数据的智能财务分析对话</p>
      </div>

      <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-if="messages.length === 0" class="h-full flex items-center justify-center">
          <div class="text-center max-w-2xl">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
              <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-800 mb-2">开始您的智能分析之旅</h3>
            <p class="text-gray-600 mb-6">我可以帮您分析企业财报、评估经营风险、追踪市场舆情</p>
            
            <div class="grid grid-cols-2 gap-3 text-left">
              <button 
                v-for="example in exampleQuestions" 
                :key="example"
                @click="sendMessage(example)"
                class="p-3 bg-white/50 hover:bg-white/80 border border-gray-200 rounded-lg text-sm text-gray-700 transition"
              >
                {{ example }}
              </button>
            </div>
          </div>
        </div>

        <!-- 系统提示消息 -->
        <div v-for="(message, index) in messages" :key="index">
          <div v-if="message.role === 'system'" class="flex justify-center my-2">
            <span class="text-xs text-gray-400">{{ message.content }}</span>
          </div>
          
          <!-- 普通消息 -->
          <div v-else class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
            <div :class="[
              'max-w-[80%] rounded-lg',
              message.role === 'user' 
                ? 'bg-gradient-to-br from-blue-500 to-purple-500 text-white p-4' 
                : 'bg-white border border-gray-200'
            ]">
              <div v-if="message.role === 'assistant'" class="flex items-start space-x-3 p-4">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                </div>
                <div class="flex-1">
                  <!-- AI分析提示 -->
                  <div v-if="!message.content && message.isLoading" class="flex items-center space-x-2">
                    <div class="flex space-x-1">
                      <div class="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                      <div class="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                      <div class="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                    </div>
                    <span class="text-xs text-gray-500">AI正在分析中...</span>
                  </div>
                  <div v-else class="text-sm text-gray-800" v-html="formatMessage(message.content)"></div>
                
                  <div v-if="message.thinking" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div class="flex items-center text-xs text-blue-700 mb-2">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                      </svg>
                      <span class="font-medium">思维链推理</span>
                    </div>
                    <div class="text-xs text-gray-700">{{ message.thinking }}</div>
                  </div>

                  <div v-if="message.sources && message.sources.length > 0" class="mt-3 space-y-2">
                    <div class="text-xs text-gray-500 font-medium">数据来源</div>
                    <div class="flex flex-wrap gap-2">
                      <button 
                        v-for="(source, idx) in message.sources" 
                        :key="idx"
                        class="text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded border border-purple-200 hover:bg-purple-100 transition"
                      >
                        {{ source }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-sm">
                {{ message.content }}
              </div>
            </div>
          </div>
        </div>

      </div>

      <div class="p-4 border-t border-gray-200/50 space-y-3">
        <div v-if="uploadedFiles.length > 0" class="flex flex-wrap gap-2">
          <div v-for="(file, idx) in uploadedFiles" :key="idx" class="flex items-center space-x-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg text-xs">
            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <span class="text-blue-700">{{ file.name }}</span>
            <button @click="removeFile(idx)" class="text-blue-600 hover:text-blue-800">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <select v-model="analysisStyle" class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/50">
            <option value="专业分析">专业分析</option>
            <option value="简单分析(不含专业术语)">简单分析</option>
          </select>
          
          <label class="cursor-pointer px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition text-sm flex items-center space-x-1" :class="{'opacity-50 cursor-not-allowed': isUploading}">
            <div v-if="isUploading" class="flex items-center space-x-1">
              <svg class="w-3 h-3 text-purple-600 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="text-gray-600">上传中...</span>
            </div>
            <div v-else class="flex items-center space-x-1">
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
              </svg>
              <span class="text-gray-700">上传文件</span>
            </div>
            <input type="file" @change="handleFileUpload" accept=".pdf,.docx,.doc,.xls,.xlsx,.txt" class="hidden" :disabled="isUploading || isLoading" />
          </label>
        </div>
        
        <form @submit.prevent="handleSend" class="flex space-x-3">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="输入您的问题，例如：分析比亚迪2023年财务状况..."
            class="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition text-sm"
            :disabled="isLoading"
          />
          <button
            type="submit"
            :disabled="!inputMessage.trim() || isLoading"
            class="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium text-sm"
          >
            发送
          </button>
        </form>
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>支持上传PDF、Word、Excel等文件进行分析</span>
          <span>{{ messages.length }} 条对话</span>
        </div>
      </div>
    </div>

    <div class="w-80 glass-panel p-4 space-y-4">
      <div>
        <h3 class="text-sm font-semibold text-gray-800 mb-3">快速操作</h3>
        <div class="space-y-2">
          <button class="w-full text-left px-3 py-2 bg-white/50 hover:bg-white/80 border border-gray-200 rounded-lg text-sm text-gray-700 transition flex items-center">
            <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            生成分析报告
          </button>
          <button class="w-full text-left px-3 py-2 bg-white/50 hover:bg-white/80 border border-gray-200 rounded-lg text-sm text-gray-700 transition flex items-center">
            <svg class="w-4 h-4 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            导出对话记录
          </button>
          <button class="w-full text-left px-3 py-2 bg-white/50 hover:bg-white/80 border border-gray-200 rounded-lg text-sm text-gray-700 transition flex items-center">
            <svg class="w-4 h-4 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            新建对话
          </button>
        </div>
      </div>

      <div>
        <h3 class="text-sm font-semibold text-gray-800 mb-3">历史会话</h3>
        <div class="space-y-2 max-h-96 overflow-y-auto">
          <button 
            v-for="session in historySessions" 
            :key="session.id"
            class="w-full text-left px-3 py-2 bg-white/50 hover:bg-white/80 border border-gray-200 rounded-lg text-xs text-gray-700 transition"
          >
            <div class="font-medium truncate">{{ session.title }}</div>
            <div class="text-gray-500 mt-1">{{ session.time }}</div>
          </button>
        </div>
      </div>

      <div class="p-3 bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
        <div class="flex items-start space-x-2">
          <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div class="text-xs text-gray-700">
            <div class="font-medium mb-1">提示</div>
            <div>您可以询问企业财务指标、行业对比、风险评估等问题，系统会自动调用相关数据源进行分析。</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const isUploading = ref(false)
const chatContainer = ref(null)
const uploadedFiles = ref([])
const analysisStyle = ref('专业分析')

const exampleQuestions = [
  '分析比亚迪2023年的财务状况',
  '对比宁德时代和比亚迪的盈利能力',
  '评估特斯拉的经营风险',
  '追踪新能源汽车行业的最新舆情'
]

const historySessions = ref([
  { id: 1, title: '比亚迪财务分析', time: '2小时前' },
  { id: 2, title: '新能源行业对比', time: '昨天' },
  { id: 3, title: '特斯拉风险评估', time: '3天前' }
])

const formatMessage = (content) => {
  // 使用marked渲染Markdown
  try {
    return marked.parse(content)
  } catch (error) {
    return content.replace(/\n/g, '<br>')
  }
}

// 检查用户是否在底部
const isUserAtBottom = () => {
  if (!chatContainer.value) return true
  const threshold = 50
  const position = chatContainer.value.scrollTop + chatContainer.value.clientHeight
  const height = chatContainer.value.scrollHeight
  return position >= height - threshold
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const sendMessage = (text) => {
  inputMessage.value = text
  handleSend()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isUploading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(
      'http://localhost:8000/api/upload-file',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    uploadedFiles.value.push(response.data)
    
    messages.value.push({
      role: 'system',
      content: `文件 "${file.name}" 上传成功`
    })
  } catch (error) {
    console.error('文件上传失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '文件上传失败: ' + (error.response?.data?.detail || error.message)
    })
  } finally {
    isUploading.value = false
    scrollToBottom()
    event.target.value = ''
  }
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value
  }

  messages.value.push(userMessage)
  const question = inputMessage.value
  inputMessage.value = ''
  scrollToBottom()

  isLoading.value = true

  // 创建一个空的assistant消息用于流式更新
  const assistantMessage = {
    role: 'assistant',
    content: '',
    isLoading: true,
    thinking: null,
    sources: [],
    workflowRunId: null,
    elapsedTime: null
  }
  messages.value.push(assistantMessage)
  const messageIndex = messages.value.length - 1

  try {
    const token = localStorage.getItem('access_token')
    const payload = {
      message: question,
      style: analysisStyle.value
    }
    
    if (uploadedFiles.value.length > 0) {
      payload.files = uploadedFiles.value
    }
    
    // 使用fetch进行流式请求
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          
          if (data === '[DONE]') {
            isLoading.value = false
            break
          }

          try {
            const parsed = JSON.parse(data)
            
            if (parsed.type === 'text') {
              // 追加文本块
              messages.value[messageIndex].isLoading = false
              messages.value[messageIndex].content += parsed.text
              // 只有用户在底部时才自动滚动
              if (isUserAtBottom()) {
                scrollToBottom()
              }
            } else if (parsed.type === 'finish') {
              // 工作流完成,提取额外信息
              const finishData = parsed.data?.data || {}
              messages.value[messageIndex].workflowRunId = finishData.workflow_run_id
              messages.value[messageIndex].elapsedTime = finishData.elapsed_time
              
              // 提取outputs中的thinking和sources
              const outputs = finishData.outputs || {}
              if (outputs.thinking) {
                messages.value[messageIndex].thinking = outputs.thinking
              }
              if (outputs.sources) {
                messages.value[messageIndex].sources = outputs.sources
              }
            } else if (parsed.type === 'error') {
              messages.value[messageIndex].content = '错误: ' + parsed.error
              isLoading.value = false
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e, data)
          }
        }
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value[messageIndex].content = '抱歉，服务暂时不可用。请稍后再试。\n\n错误信息: ' + error.message
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
/* Markdown渲染样式 */
:deep(.text-sm) h1,
:deep(.text-sm) h2,
:deep(.text-sm) h3 {
  font-weight: 600;
  margin-top: 0.4em;
  margin-bottom: 0.2em;
  color: #1f2937;
}

:deep(.text-sm) h1 {
  font-size: 1.5em;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.3em;
}

:deep(.text-sm) h2 {
  font-size: 1.3em;
}

:deep(.text-sm) h3 {
  font-size: 1.1em;
}

:deep(.text-sm) p {
  margin-bottom: 0.25em;
  line-height: 1.4;
}

:deep(.text-sm) code {
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: #dc2626;
}

:deep(.text-sm) pre {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 0.5em;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.3em 0;
}

:deep(.text-sm) pre code {
  background-color: transparent;
  padding: 0;
  color: #f9fafb;
}

:deep(.text-sm) ul,
:deep(.text-sm) ol {
  margin-left: 1.5em;
  margin-bottom: 0.25em;
}

:deep(.text-sm) li {
  margin-bottom: 0.1em;
  line-height: 1.4;
}

:deep(.text-sm) blockquote {
  border-left: 4px solid #8b5cf6;
  padding-left: 1em;
  margin: 0.3em 0;
  color: #6b7280;
  font-style: italic;
}

:deep(.text-sm) table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.3em 0;
}

:deep(.text-sm) th,
:deep(.text-sm) td {
  border: 1px solid #e5e7eb;
  padding: 0.5em;
  text-align: left;
}

:deep(.text-sm) th {
  background-color: #f3f4f6;
  font-weight: 600;
}

:deep(.text-sm) a {
  color: #8b5cf6;
  text-decoration: underline;
}

:deep(.text-sm) a:hover {
  color: #7c3aed;
}

:deep(.text-sm) strong {
  font-weight: 600;
  color: #111827;
}

:deep(.text-sm) em {
  font-style: italic;
}

:deep(.text-sm) hr {
  border: none;
  border-top: 2px solid #e5e7eb;
  margin: 0.4em 0;
}
</style>
