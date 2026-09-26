<template>
  <div style="background: var(--rm-bg);
  background-image: linear-gradient(135deg,#6f9fe7,#2968b1 45%,#2270c4);
  background-attachment: fixed;">
  <div class="flex min-h-screen flex-col" style="background: linear-gradient(100deg, rgba(244, 248, 255, 0.94) 0%, rgba(244, 248, 255, 0.72) 38%, rgba(244, 248, 255, 0.18) 60%, rgba(244, 248, 255, 0) 76%);">
    <AppHeader />
    <main class="flex-1">
        <slot />
    </main>    
    <AppFooter />
  </div>
  </div>  
</template>