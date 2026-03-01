<template>
  <div class="h-full flex bg-gray-50/50 font-sans">
    <!-- 中间主对话区 (Left) -->
    <div class="flex-1 flex flex-col relative min-w-0 bg-white">
      <!-- 顶部导航 -->
      <header class="h-16 border-b border-gray-100 flex items-center justify-between px-6 bg-white/80 backdrop-blur-md sticky top-0 z-10">
        <div class="flex items-center gap-2">
           <span class="text-gray-500 text-sm flex items-center gap-2">
             <Bot class="w-4 h-4" />
             幻思·智能咨询
           </span>
           <span class="text-gray-300">/</span>
           <span class="text-gray-900 font-medium text-sm">{{ currentConversationId ? '当前会话' : '新会话' }}</span>
        </div>
        <div class="flex items-center gap-3">
          <div class="flex items-center bg-gray-100 rounded-lg p-1">
             <button 
               v-for="style in ['专业', '简洁']" 
               :key="style"
               @click="analysisStyle = style === '专业' ? '专业分析' : '简单分析(不含专业术语)'"
               :class="cn(
                 'px-3 py-1.5 text-xs font-medium rounded-md transition-all relative group overflow-hidden',
                 (style === '专业' && analysisStyle === '专业分析') || (style === '简洁' && analysisStyle !== '专业分析')
                   ? 'bg-white text-gray-900 shadow-sm'
                   : 'text-gray-500 hover:text-gray-700'
               )"
             >
               <div class="absolute bottom-0 left-0 w-full h-0.5 bg-orange-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
               {{ style }}
             </button>
          </div>
        </div>
      </header>

      <!-- 消息列表 -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto px-4 py-6 scroll-smooth custom-scrollbar">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center max-w-3xl mx-auto w-full animate-in fade-in zoom-in duration-500">
          <div class="text-center mb-10 space-y-4">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-900 shadow-xl shadow-gray-900/20 mb-4 transform hover:scale-105 transition-transform duration-300">
              <Sparkles class="w-8 h-8 text-white" />
            </div>
            <h1 class="text-3xl font-bold text-gray-900 tracking-tight">
              Phantom Flow<br/>
              <span class="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">多源数据驱动的决策进化智能体</span>
            </h1>
            <p class="text-gray-500 max-w-lg mx-auto text-lg">
              于金融幻海中捕捉瞬息，在数据流动间成就决策。
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4 w-full max-w-2xl px-4">
            <button 
              v-for="(question, idx) in exampleQuestions" 
              :key="idx"
              @click="sendMessage(question)"
              class="group relative flex flex-col items-start p-5 bg-white border border-gray-200 rounded-2xl hover:border-violet-200 hover:shadow-lg hover:shadow-violet-500/5 transition-all duration-300 text-left overflow-hidden"
            >
              <div class="absolute bottom-0 left-0 w-full h-0.5 bg-orange-500 opacity-100 transition-opacity"></div>
              <div class="absolute top-4 right-4 text-gray-300 group-hover:text-violet-500 transition-colors">
                <ArrowUpRight class="w-5 h-5" />
              </div>
              <span class="text-2xl mb-3">{{ ['📊', '💰', '⚖️', '🌐'][idx] || '💡' }}</span>
              <h3 class="font-semibold text-gray-900 mb-1 group-hover:text-violet-600 transition-colors">{{ question }}</h3>
              <p class="text-xs text-gray-500 line-clamp-2">点击立即开始分析此话题...</p>
            </button>
          </div>
        </div>

        <!-- 消息流 -->
        <div v-else class="max-w-3xl mx-auto w-full space-y-8 pb-4">
          <div v-for="(message, index) in messages" :key="index" class="animate-in slide-in-from-bottom-2 duration-300">
            <!-- System Message -->
            <div v-if="message.role === 'system'" class="flex justify-center">
              <span class="text-xs font-medium text-gray-400 bg-gray-50 px-3 py-1 rounded-full border border-gray-100">
                {{ message.content }}
              </span>
            </div>

            <!-- User Message -->
            <div v-else-if="message.role === 'user'" class="flex justify-end">
              <div class="bg-gray-900 text-white px-5 py-3.5 rounded-2xl rounded-tr-sm shadow-md max-w-[85%] text-sm leading-relaxed tracking-wide">
                {{ message.content }}
              </div>
            </div>

            <!-- Assistant Message -->
            <div v-else class="flex items-start gap-4 group">
              <div class="w-10 h-10 rounded-xl bg-gray-900 flex items-center justify-center shrink-0 shadow-lg shadow-gray-900/10">
                <Bot class="w-6 h-6 text-white" />
              </div>
              <div class="flex-1 min-w-0 space-y-2">
                <div class="bg-white border border-gray-100 rounded-2xl rounded-tl-sm p-6 shadow-sm">
                  <!-- AI Loading State -->
                  <div v-if="!message.content && message.isLoading" class="flex items-center gap-2 text-gray-500">
                    <Loader2 class="w-4 h-4 animate-spin" />
                    <span class="text-sm font-medium">正在深度分析数据...</span>
                  </div>
                  
                  <!-- AI Content -->
                  <div v-else class="prose prose-sm max-w-none prose-p:text-gray-600 prose-headings:text-gray-900 prose-strong:text-gray-900 prose-code:text-violet-600 prose-pre:bg-gray-900 prose-pre:border-gray-800" v-html="formatMessage(message.content)"></div>

                  <!-- Thinking Process -->
                  <div v-if="message.thinking" class="mt-4 pt-4 border-t border-dashed border-gray-200">
                    <div class="flex items-center gap-2 text-xs font-medium text-gray-500 mb-2">
                      <BrainCircuit class="w-4 h-4" />
                      <span>思维链推理</span>
                    </div>
                    <div class="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg leading-relaxed font-mono">
                      {{ message.thinking }}
                    </div>
                  </div>

                  <!-- Sources -->
                  <div v-if="message.sources && message.sources.length > 0" class="mt-4 pt-4 border-t border-gray-100">
                    <div class="flex flex-wrap gap-2">
                      <div v-for="(source, idx) in message.sources" :key="idx" 
                        class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-violet-50 text-violet-700 text-xs rounded-md font-medium border border-violet-100 hover:bg-violet-100 transition-colors cursor-pointer"
                      >
                        <FileText class="w-3 h-3" />
                        {{ source }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Actions -->
                <div class="flex items-center gap-2 px-2 opacity-0 group-hover:opacity-100 transition-opacity">
                   <button class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition" title="复制">
                     <Copy class="w-4 h-4" />
                   </button>
                   <button class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition" title="重试">
                     <RotateCw class="w-4 h-4" />
                   </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入区域 -->
      <div class="p-6 bg-white shrink-0 relative z-20">
        <div class="max-w-3xl mx-auto">
          <!-- 文件上传提示 -->
          <div v-if="uploadedFiles.length > 0" class="flex flex-wrap gap-2 mb-3 px-1">
            <div v-for="(file, idx) in uploadedFiles" :key="idx" class="group flex items-center gap-2 px-3 py-1.5 bg-gray-900 text-white rounded-lg text-xs font-medium shadow-md shadow-gray-200 transition-all hover:pr-2">
              <File class="w-3.5 h-3.5" />
              <span class="max-w-[150px] truncate">{{ file.name }}</span>
              <button @click="removeFile(idx)" class="text-gray-400 hover:text-white transition-colors ml-1">
                <X class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="relative group">
            <div class="absolute -inset-1 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl opacity-20 blur transition duration-500 group-hover:opacity-40"></div>
            <form @submit.prevent="handleSend" class="relative bg-white rounded-xl shadow-xl shadow-gray-200/50 border border-gray-100 flex items-center p-2 gap-2 transition-all duration-300 ring-1 ring-transparent focus-within:ring-violet-500/20">
              
              <!-- 上传按钮 -->
              <label 
                class="p-3 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-xl cursor-pointer transition-colors relative group overflow-hidden"
                :class="{'opacity-50 cursor-not-allowed': isUploading}"
                title="上传文件"
              >
                <div class="absolute bottom-0 left-0 w-full h-0.5 bg-orange-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div v-if="isUploading" class="animate-spin">
                  <Loader2 class="w-5 h-5" />
                </div>
                <Paperclip v-else class="w-5 h-5" />
                <input type="file" @change="handleFileUpload" accept=".pdf,.docx,.doc,.xls,.xlsx,.txt" class="hidden" :disabled="isUploading || isLoading" />
              </label>

              <input
                v-model="inputMessage"
                type="text"
                placeholder="询问任何关于企业财报、市场趋势的问题..."
                class="flex-1 bg-transparent border-none focus:ring-0 text-gray-800 placeholder-gray-400 text-base h-12 px-2"
                :disabled="isLoading"
              />

              <button
                type="submit"
                :disabled="!inputMessage.trim() || isLoading"
                class="p-3 bg-gray-900 text-white rounded-xl hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-gray-900/20 active:scale-95 flex items-center gap-2 font-medium px-4 relative group overflow-hidden"
              >
                <div class="absolute bottom-0 left-0 w-full h-0.5 bg-orange-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span v-if="!isLoading">发送</span>
                <Send v-if="!isLoading" class="w-4 h-4" />
                <Loader2 v-else class="w-5 h-5 animate-spin" />
              </button>
            </form>
          </div>
          <div class="text-center mt-3 text-xs text-gray-400 flex items-center justify-center gap-1.5">
            <ShieldCheck class="w-3.5 h-3.5" />
            <span>AI 生成内容仅供参考，请核对重要数据。</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Sidebar (History) -->
    <div class="w-72 bg-white border-l border-gray-100 flex flex-col shrink-0 transition-all duration-300 z-20">
      <div class="p-4 border-b border-gray-100 flex items-center justify-between">
        <span class="font-bold text-gray-900">会话历史</span>
        <button @click="startNewConversation" class="p-2 hover:bg-gray-50 rounded-lg text-gray-500 hover:text-gray-900 transition-colors relative group overflow-hidden" title="新建对话">
          <div class="absolute bottom-0 left-0 w-full h-0.5 bg-orange-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <SquarePen class="w-5 h-5" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-3 space-y-1 custom-scrollbar">
        <div class="text-xs font-medium text-gray-400 px-3 py-2">近期对话</div>
        <button
          v-for="session in historySessions"
          :key="session.id"
          @click="loadConversation(session.id)"
          :class="cn(
            'w-full text-left px-3 py-2.5 rounded-xl text-sm transition-all duration-200 flex items-center gap-3 group relative overflow-hidden',
            currentConversationId === session.id 
              ? 'bg-gray-100 text-gray-900 font-medium' 
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          )"
        >
          <div class="absolute bottom-0 left-0 w-full h-0.5 bg-orange-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <MessageSquare class="w-4 h-4 shrink-0 opacity-50 group-hover:opacity-100 transition-opacity" />
          <div class="truncate flex-1">{{ session.title }}</div>
          <span class="text-[10px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">{{ session.time }}</span>
        </button>
        
        <div v-if="historySessions.length === 0" class="flex flex-col items-center justify-center py-10 text-gray-400 gap-2">
          <History class="w-8 h-8 opacity-20" />
          <span class="text-xs">暂无历史记录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, defineEmits } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { 
  Sparkles, 
  SquarePen, 
  MessageSquare, 
  History, 
  Bot, 
  ArrowUpRight, 
  Loader2, 
  BrainCircuit, 
  FileText, 
  Copy, 
  RotateCw, 
  File, 
  X, 
  Paperclip, 
  Send,
  ShieldCheck
} from 'lucide-vue-next'

const cn = (...inputs) => twMerge(clsx(inputs))
const emit = defineEmits(['logout'])

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const isUploading = ref(false)
const chatContainer = ref(null)
const uploadedFiles = ref([])
const analysisStyle = ref('专业分析')
const currentConversationId = ref(null)
const currentUserMessage = ref('')
const currentAssistantResponse = ref('')

const exampleQuestions = [
  '分析比亚迪2023年财务状况',
  '对比宁德时代和比亚迪',
  '评估特斯拉的经营风险',
  '追踪新能源汽车行业舆情'
]

const historySessions = ref([])

// 加载聊天历史列表
const loadChatHistory = async () => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const response = await axios.get('http://localhost:8000/api/chat/history', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    historySessions.value = response.data.history.map(h => ({
      id: h.conversation_id,
      title: h.title,
      time: formatTime(h.updated_at)
    }))
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

// 格式化时间
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (hours < 1) return '刚刚'
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

// 加载特定会话的消息
const loadConversation = async (conversationId) => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`http://localhost:8000/api/chat/history/${conversationId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    messages.value = response.data.messages
    currentConversationId.value = conversationId
    scrollToBottom()
  } catch (error) {
    console.error('加载会话失败:', error)
  }
}

// 保存聊天记录
const saveChatHistory = async (conversationId, userMsg, assistantMsg) => {
  try {
    const token = localStorage.getItem('access_token')
    await axios.post('http://localhost:8000/api/chat/save', {
      conversation_id: conversationId,
      message: userMsg,
      response: assistantMsg
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    // 重新加载历史列表
    await loadChatHistory()
  } catch (error) {
    console.error('保存聊天记录失败:', error)
  }
}

const formatMessage = (content) => {
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
  currentUserMessage.value = question
  inputMessage.value = ''
  scrollToBottom()

  isLoading.value = true

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
    
    if (currentConversationId.value) {
      payload.conversation_id = currentConversationId.value
    }
    
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    
    const conversationId = response.headers.get('X-Conversation-ID')
    if (conversationId && !currentConversationId.value) {
      currentConversationId.value = conversationId
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    currentAssistantResponse.value = ''

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
              messages.value[messageIndex].isLoading = false
              messages.value[messageIndex].content += parsed.text
              currentAssistantResponse.value += parsed.text
              if (isUserAtBottom()) {
                scrollToBottom()
              }
            } else if (parsed.type === 'finish') {
              if (currentConversationId.value && currentUserMessage.value && currentAssistantResponse.value) {
                saveChatHistory(currentConversationId.value, currentUserMessage.value, currentAssistantResponse.value)
              }
              const finishData = parsed.data?.data || {}
              messages.value[messageIndex].workflowRunId = finishData.workflow_run_id
              messages.value[messageIndex].elapsedTime = finishData.elapsed_time
              
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

const startNewConversation = () => {
  messages.value = []
  currentConversationId.value = null
  currentUserMessage.value = ''
  currentAssistantResponse.value = ''
  uploadedFiles.value = []
}

onMounted(() => {
  scrollToBottom()
  loadChatHistory()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}
</style>
