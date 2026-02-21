<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useScriptStore } from '@/stores/script'
import { apiBaseUrl } from '@/config/api'

const props = defineProps<{
    isOpen: boolean
}>()

const emit = defineEmits(['close'])

const scriptStore = useScriptStore()
const iframeRef = ref<HTMLIFrameElement | null>(null)
const isLoading = ref(true)
const previewKey = ref(0) // Used to force iframe refresh

// Get the preview URL based on current script
const previewUrl = computed(() => {
    const scriptId = scriptStore.currentScript?.id
    if (!scriptId) return ''
    
    // Use the backend preview endpoint
    return `${apiBaseUrl}/api/preview/${scriptId}?t=${previewKey.value}`
})

function refreshPreview() {
    isLoading.value = true
    previewKey.value++
}

function openInNewTab() {
    const scriptId = scriptStore.currentScript?.id
    if (scriptId) {
        window.open(`${apiBaseUrl}/api/preview/${scriptId}`, '_blank')
    }
}

function onIframeLoad() {
    isLoading.value = false
}

// Watch for script changes to refresh preview
watch(() => scriptStore.currentScript?.id, () => {
    if (props.isOpen) {
        refreshPreview()
    }
})

// Watch for when panel opens
watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        isLoading.value = true
    }
})

onMounted(() => {
    if (props.isOpen) {
        isLoading.value = true
    }
})
</script>

<template>
    <!-- Backdrop -->
    <div 
        v-if="isOpen"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
        @click="$emit('close')"
    ></div>

    <!-- Popup Container -->
    <div 
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-8 pointer-events-none"
    >
        <div 
            class="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl flex flex-col pointer-events-auto overflow-hidden"
            style="width: 960px; max-width: 90vw; height: 600px; max-height: 85vh;"
            @click.stop
        >
            <!-- Header -->
            <div class="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
                <div class="flex items-center gap-2">
                    <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span class="font-bold text-gray-200">游戏预览</span>
                    <span class="text-xs text-gray-500 ml-2">{{ scriptStore.currentScript?.script_name || '' }}</span>
                </div>
                <div class="flex items-center gap-2">
                    <button 
                        @click="refreshPreview"
                        class="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-300 hover:text-white hover:bg-gray-700 rounded transition"
                        title="刷新预览"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        <span>刷新</span>
                    </button>
                    <button 
                        @click="openInNewTab"
                        class="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-300 hover:text-white hover:bg-gray-700 rounded transition"
                        title="在新标签页打开"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                        </svg>
                        <span>新窗口</span>
                    </button>
                    <button 
                        @click="$emit('close')"
                        class="p-1.5 text-gray-400 hover:text-white hover:bg-red-600 rounded transition"
                        title="关闭预览"
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Preview Content -->
            <div class="flex-1 relative overflow-hidden bg-gray-950">
                <!-- Loading Indicator -->
                <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-gray-950 z-10">
                    <div class="flex flex-col items-center gap-3">
                        <div class="w-10 h-10 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                        <span class="text-sm text-gray-400">加载游戏数据...</span>
                    </div>
                </div>

                <!-- No Script Selected -->
                <div v-if="!scriptStore.currentScript?.id" class="absolute inset-0 flex items-center justify-center bg-gray-950 z-20">
                    <div class="flex flex-col items-center gap-3 text-center p-4">
                        <svg class="w-16 h-16 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        <span class="text-gray-500">请先选择一个脚本</span>
                    </div>
                </div>

                <!-- Preview iframe -->
                <iframe
                    v-show="scriptStore.currentScript?.id && !isLoading"
                    ref="iframeRef"
                    :key="previewKey"
                    :src="previewUrl"
                    class="w-full h-full border-0"
                    sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                    @load="onIframeLoad"
                ></iframe>
            </div>

            <!-- Footer -->
            <div class="px-4 py-2 bg-gray-800 border-t border-gray-700 flex items-center justify-between text-xs text-gray-500">
                <div class="flex items-center gap-4">
                    <span class="flex items-center gap-1">
                        <span class="w-2 h-2 rounded-full bg-green-500"></span>
                        实时预览
                    </span>
                    <span v-if="scriptStore.chapters.length > 0">{{ scriptStore.chapters.length }} 章节</span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.animate-spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
</style>