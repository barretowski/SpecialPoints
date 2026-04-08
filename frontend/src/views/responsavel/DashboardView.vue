<template>
  <div class="dashboard-resp">
    <h1 class="titulo-pagina">Dashboard</h1>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card stat-membros">
        <div class="stat-icone-wrap">👨‍👩‍👧</div>
        <div>
          <p class="stat-valor">{{ membros.length }}</p>
          <p class="stat-label">Membros</p>
        </div>
      </div>
      <div class="stat-card stat-pendentes">
        <div class="stat-icone-wrap">📌</div>
        <div>
          <p class="stat-valor">{{ pendentes }}</p>
          <p class="stat-label">Pendentes</p>
        </div>
      </div>
      <div class="stat-card stat-aguardando">
        <div class="stat-icone-wrap">⏳</div>
        <div>
          <p class="stat-valor">{{ aguardando }}</p>
          <p class="stat-label">Para aprovar</p>
        </div>
      </div>
      <div class="stat-card stat-concluidas">
        <div class="stat-icone-wrap">✅</div>
        <div>
          <p class="stat-valor">{{ concluidas }}</p>
          <p class="stat-label">Concluídas</p>
        </div>
      </div>
    </div>

    <!-- Gráficos -->
    <div v-if="!carregando" class="graficos-grid">
      <GraficoStatusTarefas :tarefas="tarefas" />
      <GraficoFilhosPontos :membros="membros" />
    </div>

    <!-- Membros -->
    <section class="secao">
      <h2 class="secao-titulo">Membros da família</h2>
      <div v-if="carregando" class="carregando">Carregando…</div>
      <div v-else class="membros-grid">
        <div v-for="m in membros" :key="m.id" class="membro-card">
          <div class="membro-avatar" :style="{ background: avatarCor(m.nome) }">
            {{ m.nome[0].toUpperCase() }}
          </div>
          <div class="membro-info">
            <p class="membro-nome">{{ m.nome }}</p>
            <span class="badge-papel" :class="m.papel">{{ labelPapel(m.papel) }}</span>
          </div>
          <div v-if="m.papel === 'filho'" class="membro-pts">
            <p class="pts-valor">⭐ {{ m.pontos_disponiveis }}</p>
            <p class="pts-label">pts</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { usuariosService, tarefasService } from '@/services'
import GraficoStatusTarefas from '@/components/charts/GraficoStatusTarefas.vue'
import GraficoFilhosPontos from '@/components/charts/GraficoFilhosPontos.vue'

const membros = ref([])
const tarefas = ref([])
const carregando = ref(true)

const pendentes  = computed(() => tarefas.value.filter((t) => t.status === 'pendente').length)
const aguardando = computed(() => tarefas.value.filter((t) => t.status === 'em_andamento').length)
const concluidas = computed(() => tarefas.value.filter((t) => t.status === 'concluida').length)

const CORES = ['#7c3aed','#ec4899','#06b6d4','#10b981','#f59e0b','#6366f1','#ef4444']
function avatarCor(nome) { return CORES[nome.charCodeAt(0) % CORES.length] }

function labelPapel(p) {
  return { super_responsavel: 'Super Admin', responsavel: 'Responsável', filho: 'Filho(a)' }[p] ?? p
}

onMounted(async () => {
  const [rm, rt] = await Promise.all([
    usuariosService.familia(),
    tarefasService.listar({ tamanho: 100 }),
  ])
  membros.value = rm.data
  tarefas.value = rt.data
  carregando.value = false
})
</script>

<style scoped>
.dashboard-resp { display: flex; flex-direction: column; gap: 1.75rem; }

.titulo-pagina { font-size: 1.6rem; font-weight: 800; color: var(--cor-texto); }

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 1.1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--sombra-xs);
  border: 1.5px solid var(--cor-borda);
  border-top: 4px solid transparent;
  transition: transform 0.15s, box-shadow 0.15s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--sombra); }

.stat-membros   { border-top-color: #7c3aed; }
.stat-pendentes { border-top-color: #f59e0b; }
.stat-aguardando{ border-top-color: #3b82f6; }
.stat-concluidas{ border-top-color: #10b981; }

.stat-icone-wrap { font-size: 1.75rem; }
.stat-valor { font-size: 2rem; font-weight: 800; color: var(--cor-texto); line-height: 1; }
.stat-label { font-size: 0.75rem; color: var(--cor-texto-suave); font-weight: 500; margin-top: 0.15rem; }

/* Gráficos */
.graficos-grid {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 1rem;
  align-items: start;
}

@media (max-width: 700px) {
  .graficos-grid { grid-template-columns: 1fr; }
}

/* Membros */
.secao { display: flex; flex-direction: column; gap: 1rem; }
.secao-titulo { font-size: 1.1rem; font-weight: 700; }

.membros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
}

.membro-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  border: 1.5px solid var(--cor-borda);
  box-shadow: var(--sombra-xs);
  transition: border-color 0.15s;
}
.membro-card:hover { border-color: #c4b5fd; }

.membro-avatar {
  width: 44px; height: 44px;
  border-radius: 12px;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.25rem; font-weight: 800; flex-shrink: 0;
}

.membro-info { flex: 1; min-width: 0; }
.membro-nome { font-weight: 600; font-size: 0.92rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.badge-papel {
  display: inline-block; font-size: 0.68rem; font-weight: 700;
  padding: 0.1rem 0.5rem; border-radius: var(--raio-pill); margin-top: 0.2rem;
}
.badge-papel.super_responsavel { background: #ede9fe; color: #6d28d9; }
.badge-papel.responsavel { background: var(--cor-info-bg); color: #1e40af; }
.badge-papel.filho { background: var(--cor-sucesso-bg); color: #065f46; }

.membro-pts { text-align: right; flex-shrink: 0; }
.pts-valor { font-weight: 700; font-size: 0.9rem; color: var(--cor-primaria); }
.pts-label { font-size: 0.7rem; color: var(--cor-texto-suave); }
</style>
