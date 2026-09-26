<script setup lang="ts">
defineProps({
    name: String,
})
</script>

<template>
    <div class="h-full" style="opacity: 1; transform: none;">
                        <NuxtLink
                            class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                            style="min-height:200px;padding:24px 18px 16px;border-radius:16px;background:rgba(255,255,255,0.94);border:1px solid rgba(36,83,151,0.08);box-shadow:0 16px 45px rgba(31,73,136,0.08)"
                            :to="`/${name}`">
                        
                            <slot></slot>

                             <span aria-hidden="true"
                                                                  class="absolute z-[3] grid place-items-center text-white transition-transform group-hover:translate-x-0.5"
                                                                  style="left:18px;bottom:16px;width:28px;height:28px;border-radius:50%;background:var(--accent)"><svg
                            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                            class="lucide lucide-arrow-right"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></NuxtLink>
                    </div>
</template>