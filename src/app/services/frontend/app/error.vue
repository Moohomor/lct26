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
                <AppLogoImg/>
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