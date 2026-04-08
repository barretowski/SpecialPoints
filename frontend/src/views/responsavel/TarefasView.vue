<template>
  <div>
    <div class="cabecalho">
      <h2 class="titulo-pagina">Tarefas</h2>
      <button class="btn btn-primario" @click="modalAberto = true">+ Nova tarefa</button>
    </div>

    <div class="filtros">
      <button
        v-for="f in filtros"
        :key="f.valor"
        class="btn btn-filtro"
        :class="{ ativo: filtroAtivo === f.valor }"
        @click="filtroAtivo = f.valor"
      >
        {{ f.label }}
      </button>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <div v-else class="lista-tarefas">
      <div v-if="!tarefasFiltradas.length" class="vazio">Nenhuma tarefa encontrada.</div>
      <div
        v-for="t in tarefasFiltradas"
        :key="t.id"
        class="card tarefa-card"
        :class="{ inativa: !t.ativa }"
      >
        <div class="tarefa-main">
          <div class="tarefa-info">
            <p class="tarefa-titulo">{{ t.titulo }}</p>
            <div class="tarefa-meta">
              <span class="tarefa-pts">⭐ {{ t.pontos }} pts</span>
              <span class="badge" :class="badgeStatus(t.status)">{{ labelStatus(t.status) }}</span>
              <span v-if="nomeMembro(t.atribuido_a_id)" class="tag-filho">
                👤 {{ nomeMembro(t.atribuido_a_id) }}
              </span>
              <span v-else class="tag-filho sem-filho">Sem atribuição</span>
            </div>
          </div>

          <div class="tarefa-acoes">
            <button
              v-if="t.status === 'em_andamento'"
              class="btn btn-primario btn-sm"
              @click="aprovar(t.id)"
            >Aprovar</button>
            <button
              v-if="t.status === 'em_andamento'"
              class="btn btn-perigo btn-sm"
              @click="rejeitar(t.id)"
            >Rejeitar</button>
            <button
              class="btn-toggle"
              :class="t.ativa ? 'toggle-ativa' : 'toggle-inativa'"
              @click="toggleAtiva(t)"
              :title="t.ativa ? 'Desativar (ocultar do filho)' : 'Ativar (mostrar ao filho)'"
            >
              {{ t.ativa ? 'Ativa' : 'Inativa' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal nova tarefa -->
    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false">
      <div class="card modal">
        <h3>Nova tarefa</h3>
        <form @submit.prevent="criarTarefa">
          <div class="campo">
            <label>Título</label>
            <input v-model="novaTarefa.titulo" type="text" required />
          </div>
          <div class="campo">
            <label>Pontos</label>
            <input v-model.number="novaTarefa.pontos" type="number" min="1" required />
          </div>
          <div class="campo">
            <label>Atribuir a</label>
            <select v-model="novaTarefa.atribuido_a_id">
              <option :value="null">— Nenhum —</option>
              <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.nome }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Descrição</label>
            <textarea v-model="novaTarefa.descricao" rows="2" />
          </div>
          <div class="modal-acoes">
            <button type="button" class="btn btn-outline" @click="modalAberto = false">Cancelar</button>
            <button type="submit" class="btn btn-primario">Criar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { tarefasService, usuariosService } from '@/services'

const tarefas = ref([])
const membros = ref([])
const carregando = ref(true)
const modalAberto = ref(false)
const filtroAtivo = ref(null)

const filtros = [
  { label: 'Todas', valor: null },
  { label: 'Pendentes', valor: 'pendente' },
  { label: 'Aguardando', valor: 'em_andamento' },
  { label: 'Concluídas', valor: 'concluida' },
]

const novaTarefa = reactive({ titulo: '', pontos: 10, descricao: '', atribuido_a_id: null })

const membrosMap = computed(() => Object.fromEntries(membros.value.map((m) => [m.id, m.nome])))

const tarefasFiltradas = computed(() =>
  filtroAtivo.value ? tarefas.value.filter((t) => t.status === filtroAtivo.value) : tarefas.value,
)

function nomeMembro(id) {
  return id ? membrosMap.value[id] : null
}

const badgeStatus = (s) => ({
  pendente: 'badge-aviso',
  em_andamento: 'badge-info',
  concluida: 'badge-sucesso',
  rejeitada: 'badge-erro',
  expirada: 'badge-erro',
}[s] || 'badge-info')

const labelStatus = (s) => ({
  pendente: 'Pendente',
  em_andamento: 'Aguardando',
  concluida: 'Concluída',
  rejeitada: 'Rejeitada',
  expirada: 'Expirada',
}[s] || s)

async function carregar() {
  const [rt, rm] = await Promise.all([
    tarefasService.listar({ tamanho: 100 }),
    usuariosService.familia(),
  ])
  tarefas.value = rt.data
  membros.value = rm.data.filter((m) => m.papel === 'filho')
  carregando.value = false
}

async function criarTarefa() {
  await tarefasService.criar({ ...novaTarefa })
  modalAberto.value = false
  Object.assign(novaTarefa, { titulo: '', pontos: 10, descricao: '', atribuido_a_id: null })
  await carregar()
}

async function aprovar(id) {
  await tarefasService.aprovar(id)
  await carregar()
}

async function rejeitar(id) {
  await tarefasService.rejeitar(id, null)
  await carregar()
}

async function toggleAtiva(tarefa) {
  await tarefasService.atualizar(tarefa.id, { ativa: !tarefa.ativa })
  tarefa.ativa = !tarefa.ativa
}

onMounted(carregar)
</script>

<style scoped>
.cabecalho { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.titulo-pagina { font-size: 1.5rem; }

.filtros { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.btn-filtro {
  background: var(--cor-superficie); border: 1.5px solid var(--cor-borda);
  color: var(--cor-texto); padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.88rem;
}
.btn-filtro.ativo { border-color: var(--cor-primaria); color: var(--cor-primaria); background: #f0eeff; }

.lista-tarefas { display: flex; flex-direction: column; gap: 0.75rem; }

.tarefa-card { transition: opacity 0.15s; }
.tarefa-card.inativa { opacity: 0.55; }

.tarefa-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.tarefa-info { flex: 1; }
.tarefa-titulo { font-weight: 600; margin-bottom: 0.4rem; }

.tarefa-meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.tarefa-pts { color: var(--cor-primaria); font-weight: 600; font-size: 0.88rem; }

.tag-filho {
  font-size: 0.78rem;
  background: #e8f5e9;
  color: #2e7d32;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
}
.tag-filho.sem-filho { background: #f5f5f5; color: var(--cor-texto-suave); }

.tarefa-acoes { display: flex; gap: 0.5rem; align-items: center; flex-shrink: 0; }
.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.82rem; }

.btn-toggle {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1.5px solid;
  cursor: pointer;
  transition: background 0.12s;
}
.toggle-ativa {
  border-color: #4caf50;
  background: #e8f5e9;
  color: #2e7d32;
}
.toggle-ativa:hover { background: #c8e6c9; }
.toggle-inativa {
  border-color: #bdbdbd;
  background: #f5f5f5;
  color: #757575;
}
.toggle-inativa:hover { background: #e0e0e0; }

.vazio { text-align: center; color: var(--cor-texto-suave); padding: 2rem; }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.modal { width: 100%; max-width: 440px; display: flex; flex-direction: column; gap: 1rem; }
.modal h3 { font-size: 1.2rem; }
.modal form { display: flex; flex-direction: column; gap: 0.9rem; }
.modal-acoes { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
</style>
