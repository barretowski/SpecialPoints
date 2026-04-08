<template>
  <div>
    <h2 class="titulo-pagina">Minhas tarefas</h2>

    <div class="filtros" role="group" aria-label="Filtrar tarefas">
      <button
        v-for="f in filtros"
        :key="f.valor"
        class="btn btn-filtro"
        :class="{ ativo: filtroAtivo === f.valor }"
        @click="filtroAtivo = f.valor"
        :aria-pressed="filtroAtivo === f.valor"
      >
        {{ f.label }}
      </button>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>
    <div v-else class="lista">
      <div v-if="!filtradas.length" class="vazio">Nenhuma tarefa aqui.</div>
      <article v-for="t in filtradas" :key="t.id" class="card tarefa-card">
        <div class="tarefa-header">
          <h3 class="tarefa-titulo">{{ t.titulo }}</h3>
          <span class="badge" :class="badgeStatus(t.status)">{{ labelStatus(t.status) }}</span>
        </div>
        <p v-if="t.descricao" class="tarefa-desc">{{ t.descricao }}</p>
        <div class="tarefa-footer">
          <span class="tarefa-pts">⭐ {{ t.pontos }} pontos</span>
          <button
            v-if="t.status === 'pendente'"
            class="btn btn-primario btn-sm"
            @click="concluir(t.id)"
            :aria-label="`Marcar tarefa ${t.titulo} como concluída`"
          >
            Marcar como feita
          </button>
          <span v-if="t.status === 'em_andamento'" class="aguardando">⏳ Aguardando aprovação</span>
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
  { label: 'Todas', valor: null },
  { label: 'Pendentes', valor: 'pendente' },
  { label: 'Aguardando', valor: 'em_andamento' },
  { label: 'Concluídas', valor: 'concluida' },
]

const filtradas = computed(() =>
  filtroAtivo.value ? tarefas.value.filter((t) => t.status === filtroAtivo.value) : tarefas.value,
)

const badgeStatus = (s) => ({ pendente: 'badge-aviso', em_andamento: 'badge-info', concluida: 'badge-sucesso', rejeitada: 'badge-erro' }[s] || 'badge-info')
const labelStatus = (s) => ({ pendente: 'Pendente', em_andamento: 'Aguardando', concluida: 'Concluída', rejeitada: 'Rejeitada' }[s] || s)

async function concluir(id) {
  await tarefasService.concluir(id)
  const idx = tarefas.value.findIndex((t) => t.id === id)
  if (idx !== -1) tarefas.value[idx].status = 'em_andamento'
}

onMounted(async () => {
  const resp = await tarefasService.listar({ tamanho: 50 })
  tarefas.value = resp.data
  carregando.value = false
})
</script>

<style scoped>
.titulo-pagina { font-size: 1.4rem; margin-bottom: 1rem; }
.filtros { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.btn-filtro { background: var(--cor-superficie); border: 1.5px solid var(--cor-borda); color: var(--cor-texto); padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.88rem; }
.btn-filtro.ativo { border-color: var(--cor-primaria); color: var(--cor-primaria); background: #f0eeff; }
.lista { display: flex; flex-direction: column; gap: 0.75rem; }
.tarefa-card { display: flex; flex-direction: column; gap: 0.6rem; }
.tarefa-header { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.tarefa-titulo { font-size: 1rem; font-weight: 600; }
.tarefa-desc { font-size: 0.85rem; color: var(--cor-texto-suave); }
.tarefa-footer { display: flex; align-items: center; justify-content: space-between; }
.tarefa-pts { font-weight: 700; color: var(--cor-primaria); }
.btn-sm { padding: 0.4rem 0.9rem; font-size: 0.88rem; }
.aguardando { font-size: 0.85rem; color: var(--cor-texto-suave); }
.vazio { text-align: center; color: var(--cor-texto-suave); padding: 2rem; }
</style>
