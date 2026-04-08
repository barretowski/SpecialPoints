<template>
  <div>
    <h1 class="titulo-pagina">Dashboard</h1>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <template v-else>
      <!-- Stats cards -->
      <div class="grid-stats">
        <div v-for="s in statCards" :key="s.label" class="stat-card" :style="{ '--accent': s.cor }">
          <p class="stat-icone">{{ s.icone }}</p>
          <p class="stat-valor">{{ s.valor }}</p>
          <p class="stat-label">{{ s.label }}</p>
        </div>
      </div>

      <!-- Gráfico de distribuição -->
      <div class="graficos-row">
        <!-- Donut visão geral -->
        <div class="chart-card">
          <p class="chart-titulo">Visão geral do sistema</p>
          <div class="donut-wrap">
            <Doughnut :data="donutData" :options="donutOptions" />
          </div>
          <div class="donut-legenda">
            <div v-for="(item, i) in donutLegenda" :key="i" class="legenda-item">
              <span class="legenda-dot" :style="{ background: item.cor }"></span>
              <span class="legenda-label">{{ item.label }}</span>
              <span class="legenda-valor">{{ item.valor }}</span>
            </div>
          </div>
        </div>

        <!-- Barras de famílias -->
        <div class="chart-card">
          <p class="chart-titulo">Famílias recentes</p>
          <div v-if="!grupos.length" class="vazio">Nenhum grupo ainda.</div>
          <div v-else class="barras-grupos">
            <div v-for="g in gruposTop" :key="g.id" class="barra-grupo">
              <div class="barra-grupo-header">
                <span class="barra-grupo-nome">{{ g.nome }}</span>
                <span class="barra-grupo-val">{{ g.total_membros }} membros</span>
              </div>
              <div class="barra-track">
                <div
                  class="barra-fill"
                  :style="{
                    width: `${porcentagemGrupo(g.total_membros)}%`,
                    background: corGrupo(g.nome),
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Atalhos -->
      <div class="atalhos">
        <RouterLink to="/admin/grupos" class="atalho-card">
          <span class="atalho-icone">👨‍👩‍👧</span>
          <span>Ver Grupos</span>
        </RouterLink>
        <RouterLink to="/admin/grupos?novo=1" class="atalho-card">
          <span class="atalho-icone">➕</span>
          <span>Novo Grupo</span>
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { adminService } from '@/services'

ChartJS.register(ArcElement, Tooltip, Legend)

const stats = ref({})
const grupos = ref([])
const carregando = ref(true)

const CORES = ['#7c3aed','#ec4899','#06b6d4','#10b981','#f59e0b','#6366f1']
function corGrupo(nome) { return CORES[nome.charCodeAt(0) % CORES.length] }

const statCards = computed(() => [
  { icone: '👨‍👩‍👧', valor: stats.value.total_familias,    label: 'Grupos',      cor: '#7c3aed' },
  { icone: '👤',    valor: stats.value.total_usuarios,    label: 'Usuários',    cor: '#ec4899' },
  { icone: '✅',    valor: stats.value.total_tarefas,     label: 'Tarefas',     cor: '#10b981' },
  { icone: '💸',    valor: stats.value.total_transacoes,  label: 'Transações',  cor: '#06b6d4' },
  { icone: '🎁',    valor: stats.value.total_resgates,    label: 'Resgates',    cor: '#f59e0b' },
  { icone: '🔔',    valor: stats.value.notificacoes_nao_lidas, label: 'Notif. não lidas', cor: '#6366f1' },
])

const donutData = computed(() => ({
  labels: ['Grupos', 'Usuários', 'Tarefas'],
  datasets: [{
    data: [
      stats.value.total_familias || 0,
      stats.value.total_usuarios || 0,
      stats.value.total_tarefas  || 0,
    ],
    backgroundColor: ['#7c3aed', '#ec4899', '#10b981'],
    borderWidth: 0,
    hoverOffset: 6,
  }],
}))

const donutOptions = {
  responsive: true,
  maintainAspectRatio: true,
  cutout: '65%',
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.parsed}` } },
  },
}

const donutLegenda = computed(() => [
  { cor: '#7c3aed', label: 'Grupos',   valor: stats.value.total_familias || 0 },
  { cor: '#ec4899', label: 'Usuários', valor: stats.value.total_usuarios || 0 },
  { cor: '#10b981', label: 'Tarefas',  valor: stats.value.total_tarefas  || 0 },
])

const gruposTop = computed(() => grupos.value.slice(0, 8))
const maxMembros = computed(() => Math.max(...gruposTop.value.map((g) => g.total_membros), 1))
function porcentagemGrupo(n) { return Math.max(4, Math.round((n / maxMembros.value) * 100)) }

onMounted(async () => {
  const [rs, rg] = await Promise.all([
    adminService.stats(),
    adminService.listarGrupos({ tamanho: 8 }),
  ])
  stats.value = rs.data
  grupos.value = rg.data
  carregando.value = false
})
</script>

<style scoped>
.titulo-pagina { font-size: 1.5rem; font-weight: 800; margin-bottom: 1.5rem; color: var(--cor-texto); }

/* Stats */
.grid-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--cor-superficie);
  border: 1.5px solid var(--cor-borda);
  border-radius: var(--raio);
  border-top: 4px solid var(--accent);
  padding: 1.1rem 1rem;
  text-align: center;
  box-shadow: var(--sombra-xs);
  transition: transform 0.15s, box-shadow 0.15s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--sombra); }

.stat-icone { font-size: 1.6rem; margin-bottom: 0.4rem; }
.stat-valor { font-size: 2rem; font-weight: 800; color: var(--cor-texto); line-height: 1; }
.stat-label { font-size: 0.75rem; color: var(--cor-texto-suave); margin-top: 0.2rem; font-weight: 500; }

/* Gráficos row */
.graficos-row {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: start;
}

@media (max-width: 700px) {
  .graficos-row { grid-template-columns: 1fr; }
}

.chart-card {
  background: var(--cor-superficie);
  border: 1.5px solid var(--cor-borda);
  border-radius: var(--raio);
  padding: 1.25rem;
  box-shadow: var(--sombra-xs);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-titulo {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--cor-texto-suave);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.donut-wrap { width: 150px; height: 150px; margin: 0 auto; }

.donut-legenda { display: flex; flex-direction: column; gap: 0.45rem; }
.legenda-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; }
.legenda-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legenda-label { flex: 1; color: var(--cor-texto-suave); }
.legenda-valor { font-weight: 700; color: var(--cor-texto); }

/* Barras grupos */
.barras-grupos { display: flex; flex-direction: column; gap: 0.85rem; }

.barra-grupo-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.3rem;
  font-size: 0.82rem;
}
.barra-grupo-nome { font-weight: 600; color: var(--cor-texto); }
.barra-grupo-val { color: var(--cor-texto-suave); }

.barra-track {
  height: 8px;
  background: var(--cor-fundo);
  border-radius: var(--raio-pill);
  overflow: hidden;
}
.barra-fill {
  height: 100%;
  border-radius: var(--raio-pill);
  transition: width 0.8s cubic-bezier(0.25, 1, 0.5, 1);
}

/* Atalhos */
.atalhos { display: flex; gap: 1rem; flex-wrap: wrap; }

.atalho-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: var(--cor-superficie);
  border: 1.5px solid var(--cor-borda);
  border-radius: var(--raio);
  padding: 1.25rem 2rem;
  font-size: 0.9rem;
  color: var(--cor-texto);
  text-decoration: none;
  transition: border-color 0.15s, background 0.15s, transform 0.15s;
}
.atalho-card:hover {
  border-color: var(--cor-primaria);
  background: var(--cor-primaria-clara);
  transform: translateY(-1px);
}
.atalho-icone { font-size: 1.75rem; }

.vazio { font-size: 0.85rem; color: var(--cor-texto-suave); text-align: center; padding: 0.75rem 0; }
</style>
