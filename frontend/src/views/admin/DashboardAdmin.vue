<template>
  <div>
    <h1 class="titulo-pagina">Dashboard</h1>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <div v-else class="grid-stats">
      <div class="stat-card">
        <p class="stat-icone">👨‍👩‍👧</p>
        <p class="stat-valor">{{ stats.total_familias }}</p>
        <p class="stat-label">Grupos / Famílias</p>
      </div>
      <div class="stat-card">
        <p class="stat-icone">👤</p>
        <p class="stat-valor">{{ stats.total_usuarios }}</p>
        <p class="stat-label">Usuários</p>
      </div>
      <div class="stat-card">
        <p class="stat-icone">✅</p>
        <p class="stat-valor">{{ stats.total_tarefas }}</p>
        <p class="stat-label">Tarefas</p>
      </div>
      <div class="stat-card">
        <p class="stat-icone">💸</p>
        <p class="stat-valor">{{ stats.total_transacoes }}</p>
        <p class="stat-label">Transações</p>
      </div>
      <div class="stat-card">
        <p class="stat-icone">🎁</p>
        <p class="stat-valor">{{ stats.total_resgates }}</p>
        <p class="stat-label">Resgates</p>
      </div>
      <div class="stat-card destaque">
        <p class="stat-icone">🔔</p>
        <p class="stat-valor">{{ stats.notificacoes_nao_lidas }}</p>
        <p class="stat-label">Notif. não lidas</p>
      </div>
    </div>

    <div class="atalhos">
      <h2 class="secao-titulo">Ações rápidas</h2>
      <div class="atalhos-grid">
        <RouterLink to="/admin/grupos" class="atalho-card">
          <span class="atalho-icone">👨‍👩‍👧</span>
          <span>Ver Grupos</span>
        </RouterLink>
        <button class="atalho-card" @click="$router.push('/admin/grupos?novo=1')">
          <span class="atalho-icone">➕</span>
          <span>Novo Grupo</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminService } from '@/services'

const stats = ref({})
const carregando = ref(true)

onMounted(async () => {
  const resp = await adminService.stats()
  stats.value = resp.data
  carregando.value = false
})
</script>

<style scoped>
.titulo-pagina {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--cor-texto);
}

.grid-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--cor-superficie);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio);
  padding: 1.25rem 1rem;
  text-align: center;
}

.stat-card.destaque { border-color: var(--cor-primaria); }

.stat-icone { font-size: 1.75rem; margin-bottom: 0.5rem; }
.stat-valor { font-size: 2rem; font-weight: 700; color: var(--cor-primaria); }
.stat-label { font-size: 0.8rem; color: var(--cor-texto-suave); margin-top: 0.2rem; }

.secao-titulo { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; }

.atalhos-grid {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.atalho-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: var(--cor-superficie);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio);
  padding: 1.25rem 2rem;
  font-size: 0.95rem;
  color: var(--cor-texto);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-decoration: none;
}

.atalho-card:hover {
  border-color: var(--cor-primaria);
  background: #f0eeff;
}

.atalho-icone { font-size: 1.75rem; }
</style>
