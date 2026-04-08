<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">⭐ SpecialPoints</div>
      <nav aria-label="Menu principal">
        <RouterLink to="/responsavel/dashboard" class="nav-item">🏠 Dashboard</RouterLink>
        <RouterLink to="/responsavel/tarefas" class="nav-item">✅ Tarefas</RouterLink>
        <RouterLink to="/responsavel/recompensas" class="nav-item">🎁 Recompensas</RouterLink>
        <RouterLink to="/responsavel/membros" class="nav-item">👨‍👩‍👧 Membros</RouterLink>
      </nav>
      <button class="btn-sair" @click="sair">Sair</button>
    </aside>

    <div class="conteudo">
      <header class="topbar">
        <span class="topbar-usuario">Olá, {{ auth.usuario?.nome }}</span>
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

.sidebar {
  width: 220px;
  background: var(--cor-primaria);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  gap: 0.5rem;
  position: fixed;
  top: 0; left: 0; bottom: 0;
}

.sidebar-logo {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.nav-item {
  display: block;
  padding: 0.65rem 0.85rem;
  border-radius: var(--raio);
  color: rgba(255,255,255,0.85);
  font-size: 0.95rem;
  transition: background 0.15s;
}

.nav-item:hover,
.nav-item.router-link-active {
  background: rgba(255,255,255,0.18);
  color: #fff;
}

.btn-sair {
  margin-top: auto;
  background: rgba(255,255,255,0.15);
  border: none;
  color: #fff;
  padding: 0.6rem;
  border-radius: var(--raio);
  font-size: 0.9rem;
}
.btn-sair:hover { background: rgba(255,255,255,0.25); }

.conteudo {
  margin-left: 220px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.topbar {
  background: var(--cor-superficie);
  border-bottom: 1px solid var(--cor-borda);
  padding: 0.85rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.topbar-usuario { font-weight: 500; }

.pagina {
  padding: 1.5rem;
  flex: 1;
}
</style>
