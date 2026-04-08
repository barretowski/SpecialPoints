<template>
  <div class="recompensas-filho">

    <!-- Barra de pontos disponíveis -->
    <div class="pontos-banner">
      <div class="pontos-banner-info">
        <p class="pontos-banner-label">Pontos disponíveis</p>
        <p class="pontos-banner-valor">⭐ {{ auth.usuario?.pontos_disponiveis || 0 }}</p>
      </div>
      <div class="pontos-banner-icon">🏆</div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" :class="{ 'tab-ativa': aba === 'loja' }" @click="aba = 'loja'">
        🎁 Loja
      </button>
      <button class="tab" :class="{ 'tab-ativa': aba === 'resgates' }" @click="mudarAbaResgates">
        📦 Resgates
        <span v-if="pendentesCount" class="tab-badge">{{ pendentesCount }}</span>
      </button>
      <button class="tab" :class="{ 'tab-ativa': aba === 'historico' }" @click="mudarAbaHistorico">
        📊 Histórico
      </button>
    </div>

    <!-- Aba: Loja -->
    <template v-if="aba === 'loja'">
      <div v-if="carregando" class="carregando">Carregando…</div>

      <div v-else class="grid">
        <div v-if="!recompensas.length" class="vazio-hero">
          <p class="vazio-emoji">🎁</p>
          <p class="vazio-titulo">Nenhuma recompensa disponível ainda.</p>
        </div>

        <article
          v-for="r in recompensas"
          :key="r.id"
          class="recompensa-card"
          :class="{ bloqueada: pontos < r.custo_pontos }"
        >
          <div class="recompensa-topo">
            <div class="recompensa-icone-wrap">
              <span class="recompensa-icone">🎁</span>
            </div>
            <div v-if="pontos >= r.custo_pontos" class="badge-desbloqueada">✓ Pode resgatar</div>
            <div v-else class="badge-bloqueada">🔒 Bloqueada</div>
          </div>

          <h3 class="recompensa-titulo">{{ r.titulo }}</h3>
          <p v-if="r.descricao" class="recompensa-desc">{{ r.descricao }}</p>

          <div class="recompensa-progresso">
            <div class="progresso-barra">
              <div
                class="progresso-fill"
                :style="{ width: `${Math.min(100, Math.round((pontos / r.custo_pontos) * 100))}%` }"
              ></div>
            </div>
            <p class="progresso-label">
              {{ pontos >= r.custo_pontos
                ? `⭐ ${r.custo_pontos} pts`
                : `Faltam ${r.custo_pontos - pontos} pts` }}
            </p>
          </div>

          <button
            class="btn-resgatar"
            :class="{ ativo: pontos >= r.custo_pontos }"
            :disabled="pontos < r.custo_pontos"
            @click="resgatar(r.id)"
            :aria-label="`Resgatar ${r.titulo} por ${r.custo_pontos} pontos`"
          >
            {{ pontos >= r.custo_pontos ? '🎉 Resgatar' : `⭐ ${r.custo_pontos} pts` }}
          </button>
        </article>
      </div>
    </template>

    <!-- Aba: Meus Resgates -->
    <template v-else>
      <div v-if="carregandoResgates" class="carregando">Carregando…</div>

      <div v-else-if="!resgates.length" class="vazio-hero">
        <p class="vazio-emoji">📦</p>
        <p class="vazio-titulo">Você ainda não resgatou nada.</p>
        <p class="vazio-sub">Troque seus pontos por recompensas!</p>
      </div>

      <div v-else class="lista-resgates">
        <div
          v-for="rs in resgates"
          :key="rs.id"
          class="resgate-card"
          :class="`status-${rs.status}`"
        >
          <div class="resgate-esquerda">
            <div class="resgate-icone">{{ iconeStatus(rs.status) }}</div>
            <div>
              <p class="resgate-titulo">{{ rs.titulo_recompensa }}</p>
              <p class="resgate-data">{{ formatarData(rs.criado_em) }}</p>
              <p v-if="rs.observacao" class="resgate-obs">💬 {{ rs.observacao }}</p>
            </div>
          </div>
          <div class="resgate-direita">
            <span class="resgate-pts">⭐ {{ rs.pontos_gastos }} pts</span>
            <span class="status-chip" :class="`chip-${rs.status}`">{{ labelStatus(rs.status) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Aba: Histórico de pontos -->
    <template v-if="aba === 'historico'">
      <div v-if="carregandoHistorico" class="carregando">Carregando…</div>

      <div v-else-if="!historico.length" class="vazio-hero">
        <p class="vazio-emoji">📊</p>
        <p class="vazio-titulo">Nenhuma movimentação ainda.</p>
      </div>

      <div v-else class="lista-historico">
        <div
          v-for="t in historico"
          :key="t.id"
          class="historico-card"
          :class="t.tipo === 'debito' ? 'debito' : 'credito'"
        >
          <div class="hist-icone">{{ t.tipo === 'debito' ? '💸' : (t.tipo === 'bonus' ? '🎁' : '⭐') }}</div>
          <div class="hist-info">
            <p class="hist-desc">{{ t.descricao }}</p>
            <p class="hist-data">{{ formatarData(t.criado_em) }}</p>
          </div>
          <div class="hist-valor" :class="t.tipo === 'debito' ? 'valor-negativo' : 'valor-positivo'">
            {{ t.tipo === 'debito' ? '-' : '+' }}{{ t.quantidade }}
          </div>
        </div>
      </div>
    </template>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.visivel" class="toast" :class="`toast-${toast.tipo}`" role="status" aria-live="polite">
        {{ toast.msg }}
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { recompensasService, resgatesService, transacoesService } from '@/services'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const recompensas = ref([])
const resgates = ref([])
const historico = ref([])
const carregando = ref(true)
const carregandoResgates = ref(false)
const carregandoHistorico = ref(false)
const aba = ref('loja')
const toast = reactive({ visivel: false, msg: '', tipo: 'sucesso' })

const pontos = computed(() => auth.usuario?.pontos_disponiveis || 0)
const pendentesCount = computed(() => resgates.value.filter((r) => r.status === 'pendente').length)

function iconeStatus(status) {
  const mapa = { pendente: '⏳', aprovado: '✅', entregue: '🎉', recusado: '❌' }
  return mapa[status] || '📦'
}

function labelStatus(status) {
  const mapa = { pendente: 'Pendente', aprovado: 'Aprovado', entregue: 'Entregue', recusado: 'Recusado' }
  return mapa[status] || status
}

function formatarData(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function mostrarToast(msg, tipo = 'sucesso') {
  toast.msg = msg
  toast.tipo = tipo
  toast.visivel = true
  setTimeout(() => { toast.visivel = false }, 3500)
}

async function resgatar(id) {
  try {
    await resgatesService.solicitar(id)
    await auth.carregarPerfil()
    await carregarResgates()
    mostrarToast('Resgate solicitado! Aguarde a aprovação. 🎉')
  } catch (e) {
    mostrarToast(e.response?.data?.detail || 'Erro ao resgatar.', 'erro')
  }
}

async function carregarResgates() {
  carregandoResgates.value = true
  const resp = await resgatesService.listar()
  resgates.value = resp.data
  carregandoResgates.value = false
}

async function mudarAbaResgates() {
  aba.value = 'resgates'
  if (!resgates.value.length) await carregarResgates()
}

async function carregarHistorico() {
  carregandoHistorico.value = true
  const resp = await transacoesService.listar({ tamanho: 100 })
  historico.value = resp.data
  carregandoHistorico.value = false
}

async function mudarAbaHistorico() {
  aba.value = 'historico'
  if (!historico.value.length) await carregarHistorico()
}

onMounted(async () => {
  const [respRecomp, respResgates] = await Promise.all([
    recompensasService.listar(),
    resgatesService.listar(),
  ])
  recompensas.value = respRecomp.data
  resgates.value = respResgates.data
  carregando.value = false
})
</script>

<style scoped>
.recompensas-filho { display: flex; flex-direction: column; gap: 1.25rem; }

/* Banner de pontos */
.pontos-banner {
  background: var(--grad-dourado);
  border-radius: var(--raio);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 6px 20px rgba(245,158,11,0.3);
}
.pontos-banner-label { font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.06em; }
.pontos-banner-valor { font-size: 1.75rem; font-weight: 800; color: #fff; }
.pontos-banner-icon { font-size: 2.5rem; }

/* Tabs */
.tabs {
  display: flex;
  gap: 0.5rem;
  background: var(--cor-fundo);
  border-radius: var(--raio);
  padding: 0.3rem;
}
.tab {
  flex: 1;
  padding: 0.55rem 1rem;
  border-radius: calc(var(--raio) - 2px);
  border: none;
  background: transparent;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--cor-texto-suave);
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.tab-ativa {
  background: #fff;
  color: var(--cor-primaria);
  box-shadow: var(--sombra-xs);
}
.tab-badge {
  background: var(--cor-secundaria);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.1rem 0.4rem;
  border-radius: var(--raio-pill);
  line-height: 1.4;
}

/* Grid loja */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.85rem; }

/* Card recompensa */
.recompensa-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  box-shadow: var(--sombra-xs);
  border: 2px solid var(--cor-borda);
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.recompensa-card:not(.bloqueada) { border-color: #c4b5fd; }
.recompensa-card:not(.bloqueada):hover { transform: translateY(-2px); box-shadow: var(--sombra-md); border-color: var(--cor-primaria); }
.recompensa-card.bloqueada { opacity: 0.75; }

.recompensa-topo { display: flex; align-items: center; justify-content: space-between; }
.recompensa-icone-wrap {
  width: 44px; height: 44px; border-radius: 12px;
  background: var(--cor-primaria-clara);
  display: flex; align-items: center; justify-content: center;
}
.recompensa-icone { font-size: 1.5rem; }

.badge-desbloqueada {
  font-size: 0.68rem; font-weight: 700; color: #065f46;
  background: var(--cor-sucesso-bg); padding: 0.15rem 0.5rem; border-radius: var(--raio-pill);
}
.badge-bloqueada {
  font-size: 0.68rem; font-weight: 700; color: var(--cor-texto-suave);
  background: var(--cor-fundo); padding: 0.15rem 0.5rem; border-radius: var(--raio-pill);
}

.recompensa-titulo { font-weight: 700; font-size: 0.95rem; }
.recompensa-desc { font-size: 0.78rem; color: var(--cor-texto-suave); line-height: 1.4; }

.recompensa-progresso { display: flex; flex-direction: column; gap: 0.3rem; }
.progresso-barra { height: 6px; background: var(--cor-borda); border-radius: var(--raio-pill); overflow: hidden; }
.progresso-fill { height: 100%; background: var(--grad-primario); border-radius: var(--raio-pill); transition: width 0.5s ease; }
.progresso-label { font-size: 0.72rem; font-weight: 600; color: var(--cor-texto-suave); }

.btn-resgatar {
  width: 100%; padding: 0.55rem; border-radius: var(--raio);
  border: 2px solid var(--cor-borda); background: var(--cor-fundo);
  color: var(--cor-texto-suave); font-size: 0.85rem; font-weight: 700;
  transition: all 0.15s; cursor: not-allowed;
}
.btn-resgatar.ativo {
  background: var(--grad-primario); border-color: transparent; color: #fff;
  box-shadow: 0 4px 14px rgba(124,58,237,0.35); cursor: pointer;
}
.btn-resgatar.ativo:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(124,58,237,0.45); }
.btn-resgatar.ativo:active { transform: scale(0.98); }

/* Lista de resgates */
.lista-resgates { display: flex; flex-direction: column; gap: 0.65rem; }

.resgate-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 0.9rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  box-shadow: var(--sombra-xs);
  border: 1.5px solid var(--cor-borda);
  border-left: 4px solid var(--cor-borda);
}

.resgate-card.status-pendente  { border-left-color: var(--cor-aviso); }
.resgate-card.status-aprovado  { border-left-color: var(--cor-primaria); }
.resgate-card.status-entregue  { border-left-color: var(--cor-sucesso); }
.resgate-card.status-recusado  { border-left-color: var(--cor-erro); }

.resgate-esquerda { display: flex; align-items: flex-start; gap: 0.75rem; flex: 1; min-width: 0; }
.resgate-icone { font-size: 1.4rem; flex-shrink: 0; margin-top: 0.1rem; }

.resgate-titulo { font-weight: 700; font-size: 0.9rem; }
.resgate-data { font-size: 0.72rem; color: var(--cor-texto-suave); margin-top: 0.1rem; }
.resgate-obs { font-size: 0.72rem; color: var(--cor-texto-suave); margin-top: 0.2rem; font-style: italic; }

.resgate-direita { display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem; flex-shrink: 0; }

.resgate-pts {
  font-size: 0.75rem; font-weight: 700;
  background: var(--cor-aviso-bg); color: #92400e;
  padding: 0.1rem 0.45rem; border-radius: var(--raio-pill);
}

.status-chip {
  font-size: 0.68rem; font-weight: 700;
  padding: 0.15rem 0.5rem; border-radius: var(--raio-pill);
}
.chip-pendente  { background: var(--cor-aviso-bg);   color: #92400e; }
.chip-aprovado  { background: var(--cor-primaria-clara); color: var(--cor-primaria); }
.chip-entregue  { background: var(--cor-sucesso-bg); color: #065f46; }
.chip-recusado  { background: var(--cor-erro-bg);    color: #991b1b; }

/* Histórico */
.lista-historico { display: flex; flex-direction: column; gap: 0.5rem; }

.historico-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 0.8rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: var(--sombra-xs);
  border: 1.5px solid var(--cor-borda);
  border-left: 4px solid var(--cor-borda);
}
.historico-card.credito { border-left-color: var(--cor-sucesso); }
.historico-card.debito  { border-left-color: var(--cor-erro); }

.hist-icone { font-size: 1.3rem; flex-shrink: 0; }
.hist-info { flex: 1; min-width: 0; }
.hist-desc { font-weight: 600; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hist-data { font-size: 0.72rem; color: var(--cor-texto-suave); margin-top: 0.1rem; }

.hist-valor { font-size: 1rem; font-weight: 800; flex-shrink: 0; }
.valor-positivo { color: var(--cor-sucesso); }
.valor-negativo { color: var(--cor-erro); }

/* Vazio */
.vazio-hero { text-align: center; padding: 2.5rem; }
.vazio-emoji { font-size: 3rem; margin-bottom: 0.5rem; }
.vazio-titulo { font-weight: 600; color: var(--cor-texto-suave); }
.vazio-sub { font-size: 0.8rem; color: var(--cor-texto-suave); margin-top: 0.25rem; }

/* Toast */
.toast {
  position: fixed; bottom: 84px; left: 50%; transform: translateX(-50%);
  padding: 0.75rem 1.5rem; border-radius: var(--raio-pill);
  font-weight: 600; font-size: 0.9rem; box-shadow: var(--sombra-md);
  z-index: 200; white-space: nowrap;
}
.toast-sucesso { background: var(--cor-texto); color: #fff; }
.toast-erro { background: var(--cor-erro); color: #fff; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
</style>
