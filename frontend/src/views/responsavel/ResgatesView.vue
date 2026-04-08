<template>
  <div>
    <h2 class="titulo-pagina">Solicitações de recompensas</h2>

    <div class="filtros">
      <button
        v-for="f in filtros"
        :key="f.valor"
        class="btn btn-filtro"
        :class="{ ativo: filtroAtivo === f.valor }"
        @click="mudarFiltro(f.valor)"
      >
        {{ f.label }}
        <span v-if="f.valor === 'pendente' && totalPendentes" class="badge-count">{{ totalPendentes }}</span>
      </button>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <div v-else>
      <div v-if="!resgates.length" class="vazio">Nenhuma solicitação encontrada.</div>

      <div v-for="r in resgates" :key="r.id" class="card resgate-card">
        <div class="resgate-info">
          <p class="resgate-titulo">🎁 {{ r.titulo_recompensa }}</p>
          <p class="resgate-filho">👤 {{ r.nome_usuario }}</p>
          <p class="resgate-pts">⭐ {{ r.pontos_gastos }} pts gastos</p>
          <p class="resgate-data">{{ formatarData(r.criado_em) }}</p>
        </div>

        <div class="resgate-direita">
          <span class="badge" :class="badgeStatus(r.status)">{{ labelStatus(r.status) }}</span>

          <div v-if="r.status === 'pendente'" class="resgate-acoes">
            <button class="btn btn-primario btn-sm" @click="avaliar(r.id, 'aprovado')">Aprovar</button>
            <button class="btn btn-perigo btn-sm" @click="abrirRejeitar(r)">Recusar</button>
          </div>

          <div v-else-if="r.status === 'aprovado'" class="resgate-acoes">
            <button class="btn btn-entregue btn-sm" @click="avaliar(r.id, 'entregue')">Marcar entregue</button>
          </div>

          <p v-if="r.observacao" class="resgate-obs">{{ r.observacao }}</p>
        </div>
      </div>
    </div>

    <!-- Modal recusar com observação -->
    <div v-if="modalRejeitar.aberto" class="overlay" @click.self="modalRejeitar.aberto = false">
      <div class="modal card">
        <h3 class="modal-titulo">Recusar solicitação</h3>
        <p class="modal-desc">Recompensa: <strong>{{ modalRejeitar.resgate?.titulo_recompensa }}</strong></p>
        <p class="modal-desc">Solicitante: <strong>{{ modalRejeitar.resgate?.nome_usuario }}</strong></p>
        <div class="campo">
          <label for="obs-rejeitar">Motivo (opcional)</label>
          <textarea id="obs-rejeitar" v-model="modalRejeitar.observacao" rows="2" placeholder="Ex: pontos insuficientes, prazo expirado…" />
        </div>
        <p class="dica-texto">Os pontos serão estornados automaticamente.</p>
        <div class="modal-acoes">
          <button class="btn btn-secundario" @click="modalRejeitar.aberto = false">Cancelar</button>
          <button class="btn btn-perigo" @click="confirmarRejeitar" :disabled="modalRejeitar.salvando">
            {{ modalRejeitar.salvando ? 'Recusando…' : 'Recusar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { resgatesService } from '@/services'

const resgates = ref([])
const carregando = ref(true)
const filtroAtivo = ref(null)

const filtros = [
  { label: 'Todas', valor: null },
  { label: 'Pendentes', valor: 'pendente' },
  { label: 'Aprovadas', valor: 'aprovado' },
  { label: 'Entregues', valor: 'entregue' },
  { label: 'Recusadas', valor: 'recusado' },
]

const modalRejeitar = reactive({ aberto: false, resgate: null, observacao: '', salvando: false })

const totalPendentes = computed(() => resgates.value.filter((r) => r.status === 'pendente').length)

async function carregar(status = filtroAtivo.value) {
  carregando.value = true
  const resp = await resgatesService.listar(status ? { status_filtro: status } : {})
  resgates.value = resp.data
  carregando.value = false
}

async function mudarFiltro(valor) {
  filtroAtivo.value = valor
  await carregar(valor)
}

async function avaliar(id, status, observacao = null) {
  await resgatesService.avaliar(id, status, observacao)
  await carregar()
}

function abrirRejeitar(resgate) {
  modalRejeitar.resgate = resgate
  modalRejeitar.observacao = ''
  modalRejeitar.salvando = false
  modalRejeitar.aberto = true
}

async function confirmarRejeitar() {
  modalRejeitar.salvando = true
  try {
    await resgatesService.avaliar(modalRejeitar.resgate.id, 'recusado', modalRejeitar.observacao || null)
    modalRejeitar.aberto = false
    await carregar()
  } finally {
    modalRejeitar.salvando = false
  }
}

const badgeStatus = (s) => ({
  pendente: 'badge-aviso',
  aprovado: 'badge-info',
  entregue: 'badge-sucesso',
  recusado: 'badge-erro',
}[s] || 'badge-info')

const labelStatus = (s) => ({
  pendente: 'Pendente',
  aprovado: 'Aprovado',
  entregue: 'Entregue',
  recusado: 'Recusado',
}[s] || s)

function formatarData(iso) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(carregar)
</script>

<style scoped>
.titulo-pagina { font-size: 1.5rem; margin-bottom: 1.25rem; }

.filtros { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.btn-filtro {
  background: var(--cor-superficie); border: 1.5px solid var(--cor-borda);
  color: var(--cor-texto); padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.88rem;
  display: flex; align-items: center; gap: 0.4rem;
}
.btn-filtro.ativo { border-color: var(--cor-primaria); color: var(--cor-primaria); background: #f0eeff; }
.badge-count {
  background: #e53935; color: #fff; border-radius: 999px;
  font-size: 0.7rem; font-weight: 700; padding: 0.05rem 0.45rem; line-height: 1.4;
}

.resgate-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 0.75rem;
}

.resgate-info { flex: 1; }
.resgate-titulo { font-weight: 600; font-size: 1rem; margin-bottom: 0.3rem; }
.resgate-filho { font-size: 0.88rem; color: #2e7d32; }
.resgate-pts { font-size: 0.85rem; color: var(--cor-primaria); font-weight: 600; margin-top: 0.2rem; }
.resgate-data { font-size: 0.78rem; color: var(--cor-texto-suave); margin-top: 0.15rem; }

.resgate-direita { display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; flex-shrink: 0; }
.resgate-acoes { display: flex; gap: 0.4rem; }
.resgate-obs { font-size: 0.78rem; color: var(--cor-texto-suave); max-width: 200px; text-align: right; }

.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.82rem; }
.btn-entregue {
  background: #e8f5e9; color: #2e7d32; border: 1.5px solid #4caf50;
  border-radius: var(--raio); cursor: pointer; font-weight: 600;
}
.btn-entregue:hover { background: #c8e6c9; }

.vazio { text-align: center; color: var(--cor-texto-suave); padding: 3rem; }

/* Modal */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100; padding: 1rem;
}
.modal { width: 100%; max-width: 420px; display: flex; flex-direction: column; gap: 1rem; }
.modal-titulo { font-size: 1.2rem; font-weight: 700; }
.modal-desc { font-size: 0.9rem; color: var(--cor-texto-suave); }
.modal-acoes { display: flex; justify-content: flex-end; gap: 0.75rem; }
.btn-secundario {
  background: var(--cor-fundo); border: 1px solid var(--cor-borda); color: var(--cor-texto);
  padding: 0.55rem 1.1rem; border-radius: var(--raio); font-size: 0.9rem; cursor: pointer;
}
.dica-texto {
  font-size: 0.83rem; color: var(--cor-texto-suave); background: #fff8e1;
  border-radius: var(--raio); padding: 0.6rem 0.85rem; border-left: 3px solid #ffc107;
}
</style>
