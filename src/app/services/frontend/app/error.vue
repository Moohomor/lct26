<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4" style="background:var(--paper)">
    <div class="text-center">
        <div class="flex justify-center mb-6">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl"
                 style="background:var(--accent-soft);border:1px solid var(--line)">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                     class="lucide lucide-bot h-8 w-8" style="color:var(--accent)">
                    <path d="M12 8V4H8"></path>
                    <rect width="16" height="12" x="4" y="8" rx="2"></rect>
                    <path d="M2 14h2"></path>
                    <path d="M20 14h2"></path>
                    <path d="M15 13v2"></path>
                    <path d="M9 13v2"></path>
                </svg>
            </div>
        </div>
        <p class="mono" style="font-size:52px;font-weight:700;color:var(--ink);line-height:1;margin-bottom:16px">{{ error.status }}</p>
        <template v-if="error.status === 404">
            <p style="font-size:20px;font-weight:600;color:var(--ink);margin-bottom:8px">Страница не найдена</p>
            <p style="color:var(--sub);margin-bottom:32px">Запрошенная страница не существует или была перемещена</p>
        </template>       

        <div class="flex flex-wrap gap-3 justify-center">
            <NuxtLink 
                style="display:inline-flex;align-items:center;height:42px;padding:0 20px;border-radius:10px;background:var(--accent);color:#fff;font-weight:600;font-size:14px;text-decoration:none"
                to="/">На главную</NuxtLink>
        </div>
    </div>
</div>
</template>