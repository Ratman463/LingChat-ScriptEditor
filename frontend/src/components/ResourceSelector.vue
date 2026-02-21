<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useScriptStore } from '@/stores/script'
import { apiBaseUrl } from '@/config/api'

const props = defineProps<{
    modelValue: string
    resourceType: 'background' | 'music' | 'character' | 'sound'
    placeholder?: string
}>()

const emit = defineEmits(['update:modelValue'])

const scriptStore = useScriptStore()
const showDropdown = ref(false)
const searchText = ref('')
const resources = ref<string[]>([])

// Map resource type to asset category
const categoryMap: Record<string, string[]> = {
    background: ['Backgrounds', 'background', 'images'],
    music: ['Musics', 'music', 'bgm'],
    character: ['Characters', 'characters'],
    sound: ['Sounds', 'sound', 'effects']
}

// Fetch resources from backend
async function fetchResources() {
    const scriptId = scriptStore.currentScript?.id
    if (!scriptId) return

    try {
        // Fetch characters from dedicated endpoint
        if (props.resourceType === 'character') {
            const res = await fetch(`${apiBaseUrl}/api/scripts/${scriptId}/characters`)
            if (res.ok) {
                const data = await res.json()
                resources.value = data.map((c: any) => c.name || c.id || c._path)
            }
        } else {
            // Use assets from store
            const assets = scriptStore.assets
            const categories = categoryMap[props.resourceType] || []
            
            let allResources: string[] = []
            for (const cat of categories) {
                if (assets[cat]) {
                    allResources = [...allResources, ...assets[cat]]
                }
            }
            resources.value = [...new Set(allResources)] // Remove duplicates
        }
    } catch (e) {
        console.error('Failed to fetch resources:', e)
        resources.value = []
    }
}

// Filter resources based on search text
const filteredResources = computed(() => {
    if (!searchText.value) return resources.value
    const search = searchText.value.toLowerCase()
    return resources.value.filter(r => r.toLowerCase().includes(search))
})

// Get display name from path
function getDisplayName(path: string): string {
    if (!path) return ''
    const parts = path.split('/')
    return parts[parts.length - 1] || path
}

function selectResource(resource: string) {
    emit('update:modelValue', resource)
    showDropdown.value = false
    searchText.value = ''
}

function clearSelection() {
    emit('update:modelValue', '')
}

function toggleDropdown() {
    showDropdown.value = !showDropdown.value
    if (showDropdown.value) {
        fetchResources()
    }
}

// Watch for script changes
watch(() => scriptStore.currentScript?.id, (newId) => {
    if (showDropdown.value && newId) {
        fetchResources()
    }
})

onMounted(() => {
    if (showDropdown.value) {
        fetchResources()
    }
})
</script>

<template>
    <div class="relative" @mousedown.stop>
        <div class="flex items-center gap-1">
            <div 
                class="flex-1 bg-black/30 border border-white/10 rounded p-1.5 text-xs cursor-pointer hover:border-purple-500/30 transition flex items-center justify-between min-h-[28px]"
                @click="toggleDropdown"
            >
                <span v-if="modelValue" class="truncate text-gray-200">{{ getDisplayName(modelValue) }}</span>
                <span v-else class="text-gray-500">{{ placeholder || '选择资源...' }}</span>
                <svg class="w-3 h-3 text-gray-400 flex-shrink-0 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
            </div>
            <button 
                v-if="modelValue"
                @click="clearSelection"
                class="text-gray-500 hover:text-red-400 transition p-1"
                title="清除选择"
            >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>

        <!-- Dropdown -->
        <div 
            v-if="showDropdown"
            class="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 max-h-48 overflow-hidden"
        >
            <!-- Search Input -->
            <div class="p-2 border-b border-gray-700">
                <input 
                    v-model="searchText"
                    type="text"
                    placeholder="搜索..."
                    class="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs focus:outline-none focus:border-purple-500"
                    @mousedown.stop
                />
            </div>

            <!-- Resource List -->
            <div class="overflow-y-auto max-h-32">
                <div v-if="filteredResources.length === 0" class="p-2 text-gray-500 text-xs text-center">
                    没有找到资源
                </div>
                <div 
                    v-for="resource in filteredResources" 
                    :key="resource"
                    @click="selectResource(resource)"
                    class="px-3 py-1.5 text-xs cursor-pointer transition"
                    :class="resource === modelValue ? 'bg-purple-600/30 text-purple-300' : 'text-gray-300 hover:bg-gray-700'"
                >
                    <div class="flex items-center gap-2">
                        <svg v-if="resourceType === 'background'" class="w-3 h-3 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <svg v-else-if="resourceType === 'music'" class="w-3 h-3 text-yellow-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path>
                        </svg>
                        <svg v-else-if="resourceType === 'character'" class="w-3 h-3 text-blue-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                        </svg>
                        <svg v-else class="w-3 h-3 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        <span class="truncate">{{ getDisplayName(resource) }}</span>
                    </div>
                    <div v-if="resource !== getDisplayName(resource)" class="text-[10px] text-gray-500 mt-0.5 ml-5 truncate">
                        {{ resource }}
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="p-2 border-t border-gray-700 bg-gray-900/50">
                <div class="flex items-center justify-between text-[10px] text-gray-500">
                    <span>{{ filteredResources.length }} 个资源</span>
                    <button 
                        @click="showDropdown = false"
                        class="text-gray-400 hover:text-gray-200"
                    >
                        关闭
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>