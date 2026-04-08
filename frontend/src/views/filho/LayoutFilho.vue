<template>
  <div class="layout-filho">
    <header class="header-filho" role="banner">
      <span class="logo">⭐ SpecialPoints</span>
      <span class="saudacao">Olá, {{ auth.usuario?.nome }}!</span>
      <div class="pontos-badge" aria-label="Seus pontos disponíveis">
        ⭐ {{ auth.usuario?.pontos_disponiveis || 0 }} pts
      </div>
      <button class="btn-sair" @click="sair" aria-label="Sair da conta">Sair</button>
    </header>

    <nav class="nav-filho" aria-label="Navegação principal">
      <RouterLink to="/filho/dashboard" class="nav-btn" aria-label="Início">
        <span class="nav-icone" aria-hidden="true">🏠</span>
        <span>Início</span>
      </RouterLink>
      <RouterLink to="/filho/tarefas" class="nav-btn" aria-label="Minhas tarefas">
        <span class="nav-icone" aria-hidden="true">✅</span>
        <span>Tarefas</span>
      </RouterLink>
      <RouterLink to="/filho/recompensas" class="nav-btn" aria-label="Recompensas">
        <span class="nav-icone" aria-hidden="true">🎁</span>
        <span>Recompensas</span>
      </RouterLink>
    </nav>

    <main class="pagina-filho" id="conteudo-principal" tabindex="-1">
      <RouterView />
    </main>
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
.layout-filho {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--cor-fundo);
}

.header-filho {
  background: var(--cor-primaria);
  color: #fff;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo { font-size: 1.2rem; font-weight: 700; }
.saudacao { flex: 1; font-size: 1rem; }

.pontos-badge {
  background: rgba(255,255,255,0.2);
  padding: 0.4rem 1rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 1rem;
}

.btn-sair {
  background: rgba(255,255,255,0.15);
  border: none;
  color: #fff;
  padding: 0.4rem 0.9rem;
  border-radius: var(--raio);
  font-size: 0.9rem;
}

.nav-filho {
  display: flex;
  background: var(--cor-superficie);
  border-bottom: 1px solid var(--cor-borda);
}

.nav-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.85rem 0.5rem;
  color: var(--cor-texto-suave);
  font-size: 0.85rem;
  gap: 0.25rem;
  border-bottom: 3px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.nav-btn:hover,
.nav-btn.router-link-active {
  color: var(--cor-primaria);
  border-bottom-color: var(--cor-primaria);
}

.nav-icone { font-size: 1.5rem; }

.pagina-filho {
  flex: 1;
  padding: 1.25rem 1rem;
  max-width: 700px;
  width: 100%;
  margin: 0 auto;
}
</style>
