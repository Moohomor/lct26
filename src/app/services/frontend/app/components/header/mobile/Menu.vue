<script setup lang="ts">
const store = useHeaderMobileMenuStore()
</script>

<template>
    <div @click="store.onClose" class="fixed inset-0 z-40 lg:hidden" style="background: rgba(13, 27, 46, 0.35); backdrop-filter: blur(4px);"></div>
<div class="fixed top-0 right-0 bottom-0 z-50 lg:hidden flex flex-col"
     style="width: min(320px, 92vw); background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(24px); border-left: 1px solid rgba(210, 220, 235, 0.7); box-shadow: rgba(90, 120, 160, 0.16) -12px 0px 48px;">
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 0px 20px; height: 64px; border-bottom: 1px solid rgba(210, 220, 235, 0.55); flex-shrink: 0;">
        <AppLogo/>
        <button @click="store.onClose" style="background: none; border-width: medium; border-style: none; border-color: currentcolor; border-image: none; cursor: pointer; padding: 6px; color: var(--sub);">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 class="lucide lucide-x">
                <path d="M18 6 6 18"></path>
                <path d="m6 6 12 12"></path>
            </svg>
        </button>
    </div>
    <nav style="flex: 1 1 0%; overflow-y: auto; padding: 12px 10px;">
        
        <NuxtLink to="/catalog" style="display: flex; align-items: center; gap: 10px; padding: 13px 16px; border-radius: 10px; text-decoration: none; background: transparent; border: 1px solid transparent; margin-bottom: 4px; transition: background 0.15s;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
             stroke="var(--sub)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
             class="lucide lucide-package">
            <path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"></path>
            <path d="M12 22V12"></path>
            <path d="m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7"></path>
            <path d="m7.5 4.27 9 5.15"></path>
        </svg>
        <span style="font-size: 14.5px; font-weight: 600; color: var(--ink);">Каталог</span></NuxtLink>
        
        <NuxtLink to="/robot-selection" style="display: flex; align-items: center; gap: 10px; padding: 13px 16px; border-radius: 10px; text-decoration: none; background: transparent; border: 1px solid transparent; margin-bottom: 4px; transition: background 0.15s;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
             stroke="var(--sub)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
             class="lucide lucide-clipboard-list">
            <rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect>
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
            <path d="M12 11h4"></path>
            <path d="M12 16h4"></path>
            <path d="M8 11h.01"></path>
            <path d="M8 16h.01"></path>
        </svg>
        <span style="font-size: 14.5px; font-weight: 600; color: var(--ink);">Подбор робота</span></NuxtLink>

        <NuxtLink to="/financing" style="display: flex; align-items: center; gap: 10px; padding: 13px 16px; border-radius: 10px; text-decoration: none; background: transparent; border: 1px solid transparent; margin-bottom: 4px; transition: background 0.15s;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
             stroke="var(--sub)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
             class="lucide lucide-wallet">
            <path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"></path>
            <path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"></path>
        </svg>
        <span style="font-size: 14.5px; font-weight: 600; color: var(--ink);">Финансирование</span></NuxtLink>

        <NuxtLink to="/pilot-testing" style="display: flex; align-items: center; gap: 10px; padding: 13px 16px; border-radius: 10px; text-decoration: none; background: transparent; border: 1px solid transparent; margin-bottom: 4px; transition: background 0.15s;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
             stroke="var(--sub)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
             class="lucide lucide-flask-conical">
            <path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"></path>
            <path d="M8.5 2h7"></path>
            <path d="M7 16h10"></path>
        </svg>
        <span style="font-size: 14.5px; font-weight: 600; color: var(--ink);">Пилотирование</span></NuxtLink>
        
        <NuxtLink to="/cases" style="display: flex; align-items: center; gap: 10px; padding: 13px 16px; border-radius: 10px; text-decoration: none; background: transparent; border: 1px solid transparent; margin-bottom: 4px; transition: background 0.15s;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
             stroke="var(--sub)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
             class="lucide lucide-book-open">
            <path d="M12 7v14"></path>
            <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path>
        </svg>
        <span style="font-size: 14.5px; font-weight: 600; color: var(--ink);">Бизнес-кейсы</span></NuxtLink>
    </nav>
    <div style="padding: 12px 16px; border-top: 1px solid rgba(210, 220, 235, 0.55); flex-shrink: 0; display: flex; flex-direction: column; gap: 8px;">
        <NuxtLink to="/catalog" style="display: flex; align-items: center; justify-content: center; padding: 11px 16px; font-size: 14px; font-weight: 500; color: var(--ink); border: 1px solid rgba(210, 220, 235, 0.85); border-radius: 8px; text-decoration: none; background: rgba(20, 32, 51, 0.04);">Открыть каталог</NuxtLink>
        <NuxtLink to="/login"
                          style="display: flex; align-items: center; justify-content: center; padding: 10px 16px; font-size: 13.5px; color: var(--accent); border: 1px solid rgba(30, 136, 255, 0.35); border-radius: 8px; text-decoration: none;">Войти</NuxtLink><NuxtLink to="/register"
            style="display: flex; align-items: center; justify-content: center; padding: 10px 16px; font-size: 13.5px; font-weight: 600; color: rgb(255, 255, 255); background: var(--accent); border-radius: 8px; text-decoration: none;">Зарегистрироваться</NuxtLink>
    </div>
</div>
</template>