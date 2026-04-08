<template>
  <div>
    <div class="cabecalho">
      <h2 class="titulo-pagina">Tarefas</h2>
      <button class="btn btn-primario" @click="abrirModal()">+ Nova tarefa</button>
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
              <span v-if="t.recorrencia" class="tag-recorrencia">
                🔄 {{ labelRecorrencia(t.recorrencia) }}
              </span>
              <span v-if="estaAtrasada(t)" class="tag-atrasada">⚠️ Atrasada</span>
              <span v-else-if="t.data_limite" class="tag-prazo">
                📅 {{ formatarData(t.data_limite) }}
              </span>
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
              @click="abrirRejeitar(t)"
            >Rejeitar</button>
            <button class="btn-icone btn-editar" title="Editar" @click="abrirModal(t)">✏️</button>
            <button
              class="btn-toggle"
              :class="t.ativa ? 'toggle-ativa' : 'toggle-inativa'"
              @click="toggleAtiva(t)"
            >
              {{ t.ativa ? 'Ativa' : 'Inativa' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal criar/editar tarefa -->
    <div v-if="modal.aberto" class="modal-overlay" @click.self="fecharModal">
      <div class="card modal">
        <h3>{{ modal.editando ? 'Editar tarefa' : 'Nova tarefa' }}</h3>
        <form @submit.prevent="salvarTarefa">
          <div class="campo">
            <label>Título</label>
            <input v-model="modal.titulo" type="text" required />
          </div>
          <div class="linha-dois">
            <div class="campo">
              <label>Pontos</label>
              <input v-model.number="modal.pontos" type="number" min="1" required />
            </div>
            <div class="campo">
              <label>Atribuir a</label>
              <select v-model="modal.atribuido_a_id">
                <option :value="null">— Nenhum —</option>
                <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.nome }}</option>
              </select>
            </div>
          </div>
          <div class="linha-dois">
            <div class="campo">
              <label>Recorrência</label>
              <select v-model="modal.recorrencia">
                <option :value="null">Única</option>
                <option value="diaria">Diária</option>
                <option value="semanal">Semanal</option>
                <option value="mensal">Mensal</option>
              </select>
            </div>
            <div class="campo">
              <label>Data de vencimento</label>
              <input v-model="modal.data_limite_input" type="date" />
            </div>
          </div>
          <div class="campo">
            <label>Descrição</label>
            <textarea v-model="modal.descricao" rows="2" />
          </div>
          <p v-if="modal.erro" class="erro-texto">{{ modal.erro }}</p>
          <div class="modal-acoes">
            <button type="button" class="btn btn-ghost" @click="fecharModal">Cancelar</button>
            <button type="submit" class="btn btn-primario">
              {{ modal.editando ? 'Salvar' : 'Criar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal rejeitar -->
    <div v-if="rejeitar.aberto" class="modal-overlay" @click.self="rejeitar.aberto = false">
      <div class="card modal">
        <h3>Rejeitar tarefa</h3>
        <p class="modal-desc">Tarefa: <strong>{{ rejeitar.tarefa?.titulo }}</strong></p>
        <div class="campo">
          <label>Motivo (opcional)</label>
          <textarea v-model="rejeitar.observacao" rows="2" placeholder="Ex: A cama não estava arrumada direito" />
        </div>
        <div class="modal-acoes">
          <button class="btn btn-ghost" @click="rejeitar.aberto = false">Cancelar</button>
          <button class="btn btn-perigo" @click="confirmarRejeitar">Rejeitar</button>
        </div>
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
const filtroAtivo = ref(null)

const filtros = [
  { label: 'Todas', valor: null },
  { label: 'Pendentes', valor: 'pendente' },
  { label: 'Aguardando', valor: 'em_andamento' },
  { label: 'Concluídas', valor: 'concluida' },
]

const modal = reactive({
  aberto: false, editando: null,
  titulo: '', pontos: 10, descricao: '', atribuido_a_id: null,
  recorrencia: null, data_limite_input: '', erro: '',
})

const rejeitar = reactive({ aberto: false, tarefa: null, observacao: '' })

const membrosMap = computed(() => Object.fromEntries(membros.value.map((m) => [m.id, m.nome])))

const tarefasFiltradas = computed(() =>
  filtroAtivo.value ? tarefas.value.filter((t) => t.status === filtroAtivo.value) : tarefas.value,
)

function nomeMembro(id) { return id ? membrosMap.value[id] : null }

function estaAtrasada(t) {
  if (!t.data_limite) return false
  if (['concluida', 'rejeitada', 'expirada'].includes(t.status)) return false
  return new Date(t.data_limite) < new Date()
}

function formatarData(iso) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

function labelRecorrencia(r) {
  return { diaria: 'Diária', semanal: 'Semanal', mensal: 'Mensal' }[r] || r
}

const badgeStatus = (s) => ({
  pendente: 'badge-aviso', em_andamento: 'badge-info',
  concluida: 'badge-sucesso', rejeitada: 'badge-erro', expirada: 'badge-erro',
}[s] || 'badge-info')

const labelStatus = (s) => ({
  pendente: 'Pendente', em_andamento: 'Aguardando',
  concluida: 'Concluída', rejeitada: 'Rejeitada', expirada: 'Expirada',
}[s] || s)

function abrirModal(t = null) {
  modal.editando = t
  modal.titulo = t?.titulo || ''
  modal.pontos = t?.pontos || 10
  modal.descricao = t?.descricao || ''
  modal.atribuido_a_id = t?.atribuido_a_id || null
  modal.recorrencia = t?.recorrencia || null
  modal.data_limite_input = t?.data_limite ? t.data_limite.substring(0, 10) : ''
  modal.erro = ''
  modal.aberto = true
}

function fecharModal() { modal.aberto = false }

function abrirRejeitar(t) {
  rejeitar.tarefa = t
  rejeitar.observacao = ''
  rejeitar.aberto = true
}

async function carregar() {
  const [rt, rm] = await Promise.all([
    tarefasService.listar({ tamanho: 100 }),
    usuariosService.familia(),
  ])
  tarefas.value = rt.data
  membros.value = rm.data.filter((m) => m.papel === 'filho')
  carregando.value = false
}

async function salvarTarefa() {
  modal.erro = ''
  const payload = {
    titulo: modal.titulo,
    pontos: modal.pontos,
    descricao: modal.descricao || null,
    atribuido_a_id: modal.atribuido_a_id,
    recorrencia: modal.recorrencia || null,
    data_limite: modal.data_limite_input ? `${modal.data_limite_input}T23:59:59` : null,
  }
  try {
    if (modal.editando) {
      await tarefasService.atualizar(modal.editando.id, payload)
    } else {
      await tarefasService.criar(payload)
    }
    fecharModal()
    await carregar()
  } catch (e) {
    modal.erro = e.response?.data?.detail || 'Erro ao salvar.'
  }
}

async function aprovar(id) {
  await tarefasService.aprovar(id)
  await carregar()
}

async function confirmarRejeitar() {
  await tarefasService.rejeitar(rejeitar.tarefa.id, rejeitar.observacao || null)
  rejeitar.aberto = false
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
.titulo-pagina { font-size: 1.5rem; font-weight: 800; }

.filtros { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.btn-filtro {
  background: var(--cor-superficie); border: 1.5px solid var(--cor-borda);
  color: var(--cor-texto); padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.88rem;
}
.btn-filtro.ativo { border-color: var(--cor-primaria); color: var(--cor-primaria); background: #f0eeff; }

.lista-tarefas { display: flex; flex-direction: column; gap: 0.75rem; }
.tarefa-card { transition: opacity 0.15s; }
.tarefa-card.inativa { opacity: 0.55; }

.tarefa-main { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.tarefa-info { flex: 1; }
.tarefa-titulo { font-weight: 600; margin-bottom: 0.4rem; }

.tarefa-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.tarefa-pts { color: var(--cor-primaria); font-weight: 600; font-size: 0.88rem; }

.tag-filho {
  font-size: 0.75rem; background: #e8f5e9; color: #2e7d32;
  padding: 0.15rem 0.55rem; border-radius: 999px;
}
.tag-filho.sem-filho { background: var(--cor-fundo); color: var(--cor-texto-suave); }

.tag-recorrencia {
  font-size: 0.72rem; background: #ede9fe; color: var(--cor-primaria);
  padding: 0.12rem 0.45rem; border-radius: 999px; font-weight: 600;
}

.tag-prazo {
  font-size: 0.72rem; background: var(--cor-info-bg); color: #1e40af;
  padding: 0.12rem 0.45rem; border-radius: 999px; font-weight: 600;
}

.tag-atrasada {
  font-size: 0.72rem; background: var(--cor-erro-bg); color: #991b1b;
  padding: 0.12rem 0.45rem; border-radius: 999px; font-weight: 700;
  animation: pulsar 1.5s ease-in-out infinite;
}

@keyframes pulsar {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.tarefa-acoes { display: flex; gap: 0.5rem; align-items: center; flex-shrink: 0; }
.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.82rem; }

.btn-icone {
  width: 30px; height: 30px; border-radius: 8px; border: none;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem; cursor: pointer; transition: background 0.12s;
}
.btn-editar { background: var(--cor-fundo); }
.btn-editar:hover { background: var(--cor-primaria-clara); }

.btn-toggle {
  padding: 0.3rem 0.75rem; border-radius: 999px;
  font-size: 0.78rem; font-weight: 600; border: 1.5px solid; cursor: pointer; transition: background 0.12s;
}
.toggle-ativa { border-color: #4caf50; background: #e8f5e9; color: #2e7d32; }
.toggle-ativa:hover { background: #c8e6c9; }
.toggle-inativa { border-color: #bdbdbd; background: #f5f5f5; color: #757575; }
.toggle-inativa:hover { background: #e0e0e0; }

.vazio { text-align: center; color: var(--cor-texto-suave); padding: 2rem; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 200; padding: 1rem;
}
.modal { width: 100%; max-width: 480px; display: flex; flex-direction: column; gap: 1rem; }
.modal h3 { font-size: 1.2rem; font-weight: 700; }
.modal form { display: flex; flex-direction: column; gap: 0.9rem; }
.modal-desc { font-size: 0.9rem; color: var(--cor-texto-suave); }
.modal-acoes { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.25rem; }

.linha-dois { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
</style>
