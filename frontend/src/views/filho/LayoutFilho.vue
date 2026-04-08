<template>
  <div class="layout-filho">
    <header class="header-filho" role="banner">
      <div class="header-logo">
        <img src="@/assets/logo.png" alt="SpecialPoints" class="header-logo-img" />
        <span class="header-nome">Olá, <strong>{{ primeiroNome }}</strong>!</span>
      </div>
      <div class="header-direita">
        <div class="pontos-pill" aria-label="Seus pontos disponíveis">
          <span class="pontos-estrela">⭐</span>
          <span class="pontos-num">{{ auth.usuario?.pontos_disponiveis || 0 }}</span>
        </div>
        <button class="btn-sair-filho" @click="sair" aria-label="Sair da conta" title="Sair">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        </button>
      </div>
    </header>

    <main class="pagina-filho" id="conteudo-principal" tabindex="-1">
      <RouterView />
    </main>

    <nav class="nav-filho" aria-label="Navegação principal">
      <RouterLink to="/filho/dashboard" class="nav-btn" aria-label="Início">
        <span class="nav-icone">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        </span>
        <span class="nav-label">Início</span>
      </RouterLink>
      <RouterLink to="/filho/tarefas" class="nav-btn" aria-label="Tarefas">
        <span class="nav-icone">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
        </span>
        <span class="nav-label">Tarefas</span>
      </RouterLink>
      <RouterLink to="/filho/recompensas" class="nav-btn" aria-label="Recompensas">
        <span class="nav-icone">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg>
        </span>
        <span class="nav-label">Prêmios</span>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const primeiroNome = computed(() => auth.usuario?.nome?.split(' ')[0] || '')

function sair() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-filho {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--cor-fundo);
}

/* ── Header ── */
.header-filho {
  background: var(--grad-filho);
  padding: 0.85rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 4px 20px rgba(124,58,237,0.25);
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.header-logo-img {
  width: 34px;
  height: 34px;
  object-fit: contain;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,0.25));
}

.header-nome {
  color: rgba(255,255,255,0.9);
  font-size: 0.95rem;
}

.header-nome strong {
  color: #fff;
  font-weight: 700;
}

.header-direita {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.pontos-pill {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.3);
  padding: 0.3rem 0.85rem;
  border-radius: var(--raio-pill);
}

.pontos-estrela { font-size: 1rem; }

.pontos-num {
  font-weight: 800;
  font-size: 0.95rem;
  color: #fff;
}

.btn-sair-filho {
  background: rgba(255,255,255,0.15);
  border: none;
  color: rgba(255,255,255,0.85);
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.btn-sair-filho:hover { background: rgba(255,255,255,0.25); color: #fff; }

/* ── Conteúdo ── */
.pagina-filho {
  flex: 1;
  padding: 1.25rem 1rem 1.5rem;
  max-width: 680px;
  width: 100%;
  margin: 0 auto;
  padding-bottom: calc(80px + 1rem);
}

/* ── Nav inferior ── */
.nav-filho {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid var(--cor-borda);
  display: flex;
  padding: 0 0.5rem;
  padding-bottom: env(safe-area-inset-bottom, 0);
  box-shadow: 0 -4px 20px rgba(124,58,237,0.08);
  z-index: 50;
  height: 68px;
}

.nav-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 0.5rem;
  gap: 0.2rem;
  color: var(--cor-texto-suave);
  font-size: 0.72rem;
  font-weight: 600;
  border-radius: var(--raio);
  transition: color 0.15s;
  position: relative;
}

.nav-icone {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 32px;
  border-radius: 10px;
  transition: background 0.15s, transform 0.15s;
}

.nav-label {
  letter-spacing: 0.01em;
}

.nav-btn:hover .nav-icone { background: var(--cor-primaria-clara); }

.nav-btn.router-link-active {
  color: var(--cor-primaria);
}

.nav-btn.router-link-active .nav-icone {
  background: var(--cor-primaria-clara);
  transform: translateY(-2px);
}
</style>
