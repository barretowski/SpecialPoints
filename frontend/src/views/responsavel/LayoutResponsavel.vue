<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="@/assets/logo.png" alt="SpecialPoints" class="sidebar-logo-img" />
        <span>SpecialPoints</span>
      </div>

      <div class="sidebar-user">
        <div class="user-avatar" :style="{ background: avatarCor(auth.usuario?.nome || 'U') }">
          {{ (auth.usuario?.nome || 'U')[0].toUpperCase() }}
        </div>
        <div class="user-info">
          <p class="user-nome">{{ auth.usuario?.nome }}</p>
          <span class="user-badge">{{ labelPapel(auth.usuario?.papel) }}</span>
        </div>
      </div>

      <nav aria-label="Menu principal" class="sidebar-nav">
        <RouterLink to="/responsavel/dashboard" class="nav-item">
          <span class="nav-item-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </span>
          Dashboard
        </RouterLink>
        <RouterLink to="/responsavel/tarefas" class="nav-item">
          <span class="nav-item-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
          </span>
          Tarefas
        </RouterLink>
        <RouterLink to="/responsavel/recompensas" class="nav-item">
          <span class="nav-item-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg>
          </span>
          Recompensas
        </RouterLink>
        <RouterLink to="/responsavel/resgates" class="nav-item">
          <span class="nav-item-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
          </span>
          Resgates
        </RouterLink>
        <RouterLink to="/responsavel/membros" class="nav-item">
          <span class="nav-item-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </span>
          Membros
        </RouterLink>
      </nav>

      <button class="btn-sair" @click="sair">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Sair
      </button>
    </aside>

    <div class="conteudo">
      <header class="topbar">
        <NotificacaoBadge />
      </header>
      <main class="pagina">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificacoesStore } from '@/stores/notificacoes'
import NotificacaoBadge from '@/components/NotificacaoBadge.vue'
import { onMounted } from 'vue'

const auth = useAuthStore()
const notificacoes = useNotificacoesStore()
const router = useRouter()

onMounted(() => notificacoes.carregar())

const CORES = ['#7c3aed','#ec4899','#06b6d4','#10b981','#f59e0b','#6366f1']
function avatarCor(nome) { return CORES[nome.charCodeAt(0) % CORES.length] }

function labelPapel(p) {
  return { super_responsavel: 'Super Admin', responsavel: 'Responsável', admin: 'CEO' }[p] ?? p
}

function sair() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ── */
.sidebar {
  width: 230px;
  background: var(--cor-texto);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 1.25rem 0.85rem;
  gap: 0.25rem;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  overflow-y: auto;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 0.5rem;
}

.sidebar-logo-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
  filter: drop-shadow(0 2px 6px rgba(124,58,237,0.5));
  flex-shrink: 0;
}

/* User card */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255,255,255,0.06);
  border-radius: var(--raio);
  padding: 0.75rem;
  margin-bottom: 0.75rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  flex-shrink: 0;
}

.user-nome {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-badge {
  font-size: 0.65rem;
  font-weight: 600;
  background: rgba(124,58,237,0.5);
  color: #c4b5fd;
  padding: 0.1rem 0.45rem;
  border-radius: var(--raio-pill);
}

/* Nav */
.sidebar-nav { display: flex; flex-direction: column; gap: 0.15rem; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.65rem 0.75rem;
  border-radius: var(--raio);
  color: rgba(255,255,255,0.65);
  font-size: 0.88rem;
  font-weight: 500;
  transition: all 0.15s;
}

.nav-item-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  opacity: 0.75;
}

.nav-item:hover {
  background: rgba(255,255,255,0.08);
  color: #fff;
}

.nav-item:hover .nav-item-icon { opacity: 1; }

.nav-item.router-link-active {
  background: rgba(124,58,237,0.4);
  color: #fff;
}

.nav-item.router-link-active .nav-item-icon { opacity: 1; }

.btn-sair {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.6);
  padding: 0.6rem 0.75rem;
  border-radius: var(--raio);
  font-size: 0.88rem;
  font-weight: 500;
  transition: all 0.15s;
}
.btn-sair:hover { background: rgba(239,68,68,0.2); color: #fca5a5; border-color: rgba(239,68,68,0.3); }

/* ── Conteúdo ── */
.conteudo {
  margin-left: 230px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  background: var(--cor-superficie);
  border-bottom: 1px solid var(--cor-borda);
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  position: sticky;
  top: 0;
  z-index: 40;
}

.pagina {
  padding: 1.75rem;
  flex: 1;
}
</style>
