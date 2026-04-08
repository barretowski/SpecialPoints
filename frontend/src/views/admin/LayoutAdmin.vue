<template>
  <div class="layout-admin">
    <aside class="sidebar-admin">
      <div class="sidebar-logo">
        <img src="@/assets/logo.png" alt="SpecialPoints" class="sidebar-logo-img" />
        <span>SpecialPoints</span>
      </div>
      <p class="sidebar-tag">Painel Admin</p>

      <nav aria-label="Menu admin">
        <RouterLink to="/admin/dashboard" class="nav-item">📊 Dashboard</RouterLink>
        <RouterLink to="/admin/grupos" class="nav-item">👨‍👩‍👧 Grupos</RouterLink>
      </nav>

      <button class="btn-sair" @click="sair">Sair</button>
    </aside>

    <div class="conteudo-admin">
      <header class="topbar-admin">
        <span class="topbar-usuario">Olá, {{ auth.usuario?.nome }} <span class="badge-admin">Admin</span></span>
      </header>
      <main class="pagina-admin">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function sair() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-admin {
  display: flex;
  min-height: 100vh;
}

.sidebar-admin {
  width: 230px;
  background: #1a1a2e;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  gap: 0.5rem;
  position: fixed;
  top: 0; left: 0; bottom: 0;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.sidebar-logo-img {
  width: 38px;
  height: 38px;
  object-fit: contain;
  filter: drop-shadow(0 2px 6px rgba(108,99,255,0.4));
  flex-shrink: 0;
}

.sidebar-tag {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.4);
  margin-bottom: 1rem;
  padding-left: 2px;
}

.nav-item {
  display: block;
  padding: 0.65rem 0.85rem;
  border-radius: var(--raio);
  color: rgba(255,255,255,0.75);
  font-size: 0.95rem;
  transition: background 0.15s;
}

.nav-item:hover,
.nav-item.router-link-active {
  background: rgba(108,99,255,0.35);
  color: #fff;
}

.btn-sair {
  margin-top: auto;
  background: rgba(255,255,255,0.1);
  border: none;
  color: rgba(255,255,255,0.7);
  padding: 0.6rem;
  border-radius: var(--raio);
  font-size: 0.9rem;
  cursor: pointer;
}
.btn-sair:hover { background: rgba(255,255,255,0.2); color: #fff; }

.conteudo-admin {
  margin-left: 230px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--cor-fundo);
}

.topbar-admin {
  background: var(--cor-superficie);
  border-bottom: 1px solid var(--cor-borda);
  padding: 0.85rem 1.5rem;
  display: flex;
  align-items: center;
}

.topbar-usuario {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge-admin {
  background: #1a1a2e;
  color: #fff;
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.pagina-admin {
  padding: 1.5rem;
  flex: 1;
}
</style>
