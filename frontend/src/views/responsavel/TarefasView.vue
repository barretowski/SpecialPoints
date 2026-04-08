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
      <div v-for="t in tarefasFiltradas" :key="t.id" class="card tarefa-card">
        <div class="tarefa-info">
          <p class="tarefa-titulo">{{ t.titulo }}</p>
          <p class="tarefa-pts">⭐ {{ t.pontos }} pts</p>
          <span class="badge" :class="badgeStatus(t.status)">{{ labelStatus(t.status) }}</span>
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
            <input v-model="novatarefa.titulo" type="text" required />
          </div>
          <div class="campo">
            <label>Pontos</label>
            <input v-model.number="novatarefa.pontos" type="number" min="1" required />
          </div>
          <div class="campo">
            <label>Atribuir a</label>
            <select v-model="novatarefa.atribuido_a_id">
              <option :value="null">— Nenhum —</option>
              <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.nome }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Descrição</label>
            <textarea v-model="novatarefa.descricao" rows="2" />
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

const novatarefa = reactive({ titulo: '', pontos: 10, descricao: '', atribuido_a_id: null })

const tarefasFiltradas = computed(() =>
  filtroAtivo.value ? tarefas.value.filter((t) => t.status === filtroAtivo.value) : tarefas.value,
)

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
    tarefasService.listar({ tamanho: 50 }),
    usuariosService.familia(),
  ])
  tarefas.value = rt.data
  membros.value = rm.data.filter((m) => m.papel === 'filho')
  carregando.value = false
}

async function criarTarefa() {
  await tarefasService.criar({ ...novatarefa })
  modalAberto.value = false
  Object.assign(novatarefa, { titulo: '', pontos: 10, descricao: '', atribuido_a_id: null })
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

onMounted(carregar)
</script>

<style scoped>
.cabecalho { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.titulo-pagina { font-size: 1.5rem; }

.filtros { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }

.btn-filtro {
  background: var(--cor-superficie);
  border: 1.5px solid var(--cor-borda);
  color: var(--cor-texto);
  padding: 0.4rem 1rem;
  border-radius: 999px;
  font-size: 0.88rem;
}
.btn-filtro.ativo { border-color: var(--cor-primaria); color: var(--cor-primaria); background: #f0eeff; }

.lista-tarefas { display: flex; flex-direction: column; gap: 0.75rem; }

.tarefa-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.tarefa-info { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.tarefa-titulo { font-weight: 500; }
.tarefa-pts { color: var(--cor-primaria); font-weight: 600; font-size: 0.9rem; }

.tarefa-acoes { display: flex; gap: 0.5rem; flex-shrink: 0; }
.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.82rem; }

.vazio { text-align: center; color: var(--cor-texto-suave); padding: 2rem; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal { width: 100%; max-width: 440px; display: flex; flex-direction: column; gap: 1rem; }
.modal h3 { font-size: 1.2rem; }
.modal form { display: flex; flex-direction: column; gap: 0.9rem; }
.modal-acoes { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
</style>
