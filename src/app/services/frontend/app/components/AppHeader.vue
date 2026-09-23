<script setup lang="ts">
    const headerMobileMenuStore = useHeaderMobileMenuStore()
</script>

<template>    
  <div class="lb-headwrap">
        <div class="lb-pill" style="max-width:1320px">
            <AppLogo/>
            <nav class="hidden lg:flex items-center" style="flex:1;justify-content:center;gap:0">
                <div style="position:relative">
                    <NuxtLink to="/catalog" activeClass="active" class="lb-navlink" style="font-size:13px">Каталог</NuxtLink>
                </div>

                <div style="position:relative">
                    <NuxtLink to="/robot-selection" activeClass="active" class="lb-navlink" style="font-size:13px">Подбор робота</NuxtLink>
                </div>

                <div style="position:relative">
                    <NuxtLink to="/pilot-testing" activeClass="active" class="lb-navlink" style="font-size:13px">Пилотирование</NuxtLink>
                </div>

                <div style="position:relative">
                    <NuxtLink to="/financing" activeClass="active" class="lb-navlink" style="font-size:13px">Финансирование</NuxtLink>
                </div>

                <div style="position:relative">
                    <NuxtLink to="/cases" activeClass="active" class="lb-navlink" style="font-size:13px">Бизнес-кейсы</NuxtLink>
                </div>

                <form style="display:inline-flex;align-items:center;gap:7px;height:34px;padding:0 10px 0 12px;margin-left:6px;border-radius:999px;background:rgba(20,32,51,0.04);border:1px solid rgba(210,220,235,0.75);transition:background 0.15s, border-color 0.15s">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
                         stroke="var(--faint)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-search" style="flex-shrink:0">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.3-4.3"></path>
                    </svg>
                    <input placeholder="Поиск по сайту" aria-label="Поиск по сайту"
                           style="width:130px;background:transparent;border:none;outline:none;color:var(--ink);font-size:13px;padding:0;transition:width 0.2s ease">
                </form>
            </nav>
            <div class="flex items-center gap-2" style="flex-shrink:0">

                <div class="hidden sm:flex items-center gap-2"><a
                        style="height:36px;padding:0 14px;border-radius:8px;display:inline-flex;align-items:center;text-decoration:none;border:1px solid rgba(30,136,255,0.4);color:var(--accent);background:transparent;font-size:13px;font-weight:500;transition:background 0.15s"
                        href="/register?mode=login">Войти</a><a
                        style="height:36px;padding:0 16px;border-radius:8px;display:inline-flex;align-items:center;text-decoration:none;background:var(--accent);color:#FFFFFF;font-size:13px;font-weight:600;white-space:nowrap;transition:background 0.15s"
                        href="/register">Зарегистрироваться</a></div>
                
                <button v-if="!headerMobileMenuStore.open" @click="headerMobileMenuStore.onOpen" class="lg:hidden lb-iconbtn" aria-label="Меню">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-menu">
                        <line x1="4" x2="20" y1="12" y2="12"></line>
                        <line x1="4" x2="20" y1="6" y2="6"></line>
                        <line x1="4" x2="20" y1="18" y2="18"></line>
                    </svg>
                </button>
                <button v-else  @click="headerMobileMenuStore.onClose" class="lg:hidden lb-iconbtn" aria-label="Меню">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>
                </button>
            </div>
        </div>
    </div>
    <HeaderMobileMenu v-if="headerMobileMenuStore.open" />
</template>