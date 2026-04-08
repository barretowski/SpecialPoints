<template>
  <div class="tarefas-filho">

    <div class="filtros" role="group" aria-label="Filtrar tarefas">
      <button
        v-for="f in filtros"
        :key="f.valor"
        class="filtro-chip"
        :class="{ ativo: filtroAtivo === f.valor }"
        @click="filtroAtivo = f.valor"
        :aria-pressed="filtroAtivo === f.valor"
      >
        <span>{{ f.icone }}</span>{{ f.label }}
      </button>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <div v-else class="lista">
      <div v-if="!filtradas.length" class="vazio-hero">
        <p class="vazio-emoji">{{ filtroAtivo === 'concluida' ? '🏆' : '✨' }}</p>
        <p class="vazio-titulo">{{ filtroAtivo === 'concluida' ? 'Nenhuma tarefa concluída ainda.' : 'Tudo em dia!' }}</p>
      </div>

      <article
        v-for="t in filtradas"
        :key="t.id"
        class="tarefa-card"
        :class="`card-${t.status}`"
      >
        <div class="tarefa-status-bar"></div>
        <div class="tarefa-body">
          <div class="tarefa-topo">
            <h3 class="tarefa-titulo">{{ t.titulo }}</h3>
            <span class="badge" :class="badgeStatus(t.status)">{{ labelStatus(t.status) }}</span>
          </div>
          <p v-if="t.descricao" class="tarefa-desc">{{ t.descricao }}</p>
          <div class="tarefa-rodape">
            <div class="pts-chip">
              <span>⭐</span>
              <span>{{ t.pontos }} pts</span>
            </div>
            <button
              v-if="t.status === 'pendente'"
              class="btn-feito"
              @click="concluir(t.id)"
              :aria-label="`Marcar ${t.titulo} como feita`"
            >
              ✓ Marcar como feita
            </button>
            <div v-else-if="t.status === 'em_andamento'" class="aguardando-chip">
              ⏳ Aguardando
            </div>
          </div>
        </div>
      </article>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { tarefasService } from '@/services'

const tarefas = ref([])
const carregando = ref(true)
const filtroAtivo = ref(null)

const filtros = [
  { label: 'Todas',     valor: null,         icone: '📋' },
  { label: 'Pendentes', valor: 'pendente',    icone: '📌' },
  { label: 'Enviadas',  valor: 'em_andamento',icone: '⏳' },
  { label: 'Concluídas',valor: 'concluida',   icone: '✅' },
]

const filtradas = computed(() =>
  filtroAtivo.value ? tarefas.value.filter((t) => t.status === filtroAtivo.value) : tarefas.value,
)

const badgeStatus = (s) => ({
  pendente:    'badge-aviso',
  em_andamento:'badge-info',
  concluida:   'badge-sucesso',
  rejeitada:   'badge-erro',
}[s] || 'badge-info')

const labelStatus = (s) => ({
  pendente:    'Pendente',
  em_andamento:'Aguardando',
  concluida:   'Concluída',
  rejeitada:   'Rejeitada',
}[s] || s)

async function concluir(id) {
  await tarefasService.concluir(id)
  const t = tarefas.value.find((t) => t.id === id)
  if (t) t.status = 'em_andamento'
}

onMounted(async () => {
  const resp = await tarefasService.listar({ tamanho: 50 })
  tarefas.value = resp.data
  carregando.value = false
})
</script>

<style scoped>
.tarefas-filho { display: flex; flex-direction: column; gap: 1rem; }

/* Filtros */
.filtros {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filtro-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.9rem;
  border-radius: var(--raio-pill);
  font-size: 0.82rem;
  font-weight: 600;
  border: 1.5px solid var(--cor-borda);
  background: #fff;
  color: var(--cor-texto-suave);
  transition: all 0.15s;
}
.filtro-chip.ativo {
  background: var(--cor-primaria);
  border-color: var(--cor-primaria);
  color: #fff;
  box-shadow: 0 3px 10px rgba(124,58,237,0.3);
}

/* Cards */
.lista { display: flex; flex-direction: column; gap: 0.75rem; }

.tarefa-card {
  background: #fff;
  border-radius: var(--raio);
  box-shadow: var(--sombra-xs);
  border: 1.5px solid var(--cor-borda);
  overflow: hidden;
  display: flex;
  transition: transform 0.15s, box-shadow 0.15s;
}
.tarefa-card:hover { transform: translateY(-1px); box-shadow: var(--sombra); }

.tarefa-status-bar {
  width: 5px;
  flex-shrink: 0;
}

.card-pendente    .tarefa-status-bar { background: var(--grad-primario); }
.card-em_andamento .tarefa-status-bar { background: var(--grad-dourado); }
.card-concluida   .tarefa-status-bar { background: var(--grad-sucesso); }
.card-rejeitada   .tarefa-status-bar { background: var(--cor-erro); }

.tarefa-body {
  padding: 1rem 1.1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tarefa-topo {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.tarefa-titulo { font-weight: 700; font-size: 0.95rem; flex: 1; }
.tarefa-desc { font-size: 0.8rem; color: var(--cor-texto-suave); line-height: 1.5; }

.tarefa-rodape {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.25rem;
}

.pts-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--cor-aviso-bg);
  color: #92400e;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: var(--raio-pill);
}

.btn-feito {
  background: var(--grad-primario);
  color: #fff;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: var(--raio-pill);
  font-size: 0.82rem;
  font-weight: 700;
  box-shadow: 0 3px 8px rgba(124,58,237,0.3);
  transition: transform 0.12s, box-shadow 0.12s;
}
.btn-feito:hover { transform: translateY(-1px); box-shadow: 0 5px 12px rgba(124,58,237,0.4); }
.btn-feito:active { transform: scale(0.97); }

.aguardando-chip {
  font-size: 0.78rem;
  font-weight: 600;
  color: #92400e;
  background: var(--cor-aviso-bg);
  padding: 0.2rem 0.65rem;
  border-radius: var(--raio-pill);
}

/* Vazio */
.vazio-hero {
  text-align: center;
  padding: 2rem;
  background: #fff;
  border-radius: var(--raio);
  border: 1.5px dashed var(--cor-borda);
}
.vazio-emoji { font-size: 2.5rem; margin-bottom: 0.5rem; }
.vazio-titulo { font-weight: 600; color: var(--cor-texto-suave); }
</style>
