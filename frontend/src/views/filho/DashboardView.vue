<template>
  <div class="dashboard-filho">

    <!-- Hero de pontos -->
    <section class="hero-pontos" aria-label="Seus pontos">
      <div class="hero-personagem">
        <img src="@/assets/logo.png" alt="Personagem SpecialPoints" class="personagem" />
      </div>
      <div class="hero-conteudo">
        <p class="hero-label">Seus pontos</p>
        <p class="hero-valor" aria-live="polite">{{ auth.usuario?.pontos_disponiveis || 0 }}</p>
        <p class="hero-sub">{{ auth.usuario?.pontos_acumulados || 0 }} no total</p>
      </div>
      <div class="hero-semana" v-if="pontosSemanais !== null">
        <p class="semana-valor">+{{ pontosSemanais }}</p>
        <p class="semana-label">essa semana</p>
      </div>
    </section>

    <!-- Painel First-Then -->
    <section v-if="firstThen.tarefa" class="first-then" aria-label="Primeiro faça, depois ganhe">
      <div class="ft-lado ft-primeiro">
        <p class="ft-label">Primeiro</p>
        <div class="ft-conteudo">
          <div class="ft-icone">📋</div>
          <p class="ft-texto">{{ firstThen.tarefa.titulo }}</p>
          <div class="ft-pts">⭐ {{ firstThen.tarefa.pontos }} pts</div>
        </div>
      </div>
      <div class="ft-seta">→</div>
      <div class="ft-lado ft-depois">
        <p class="ft-label">Depois</p>
        <div class="ft-conteudo" v-if="firstThen.recompensa">
          <div class="ft-icone">🎁</div>
          <p class="ft-texto">{{ firstThen.recompensa.titulo }}</p>
          <div class="ft-progresso-wrap">
            <div class="ft-progresso-barra">
              <div class="ft-progresso-fill" :style="{ width: `${firstThen.progressoPct}%` }"></div>
            </div>
            <span class="ft-progresso-label">{{ firstThen.progressoPct }}%</span>
          </div>
        </div>
        <div class="ft-conteudo ft-sem-recompensa" v-else>
          <div class="ft-icone">🏆</div>
          <p class="ft-texto">Escolha um prêmio!</p>
        </div>
      </div>
    </section>

    <!-- Metas ativas -->
    <section v-if="metas.length" class="secao" aria-labelledby="metas-titulo">
      <div class="secao-header">
        <h3 id="metas-titulo" class="secao-titulo">Minhas metas</h3>
      </div>
      <div class="lista-metas">
        <div v-for="m in metas" :key="m.id" class="meta-card">
          <div class="meta-header">
            <p class="meta-titulo">🎯 {{ m.titulo }}</p>
            <span class="meta-pts">{{ m.pontos_atuais }} / {{ m.pontos_alvo }} pts</span>
          </div>
          <div class="meta-track">
            <div
              class="meta-fill"
              :style="{ width: `${Math.min(100, Math.round((m.pontos_atuais / m.pontos_alvo) * 100))}%` }"
            ></div>
          </div>
          <div class="meta-rodape">
            <span class="meta-pct">{{ Math.min(100, Math.round((m.pontos_atuais / m.pontos_alvo) * 100)) }}%</span>
            <span v-if="m.bonus_conclusao" class="meta-bonus">+{{ m.bonus_conclusao }} pts de bônus</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Tarefas pendentes -->
    <section class="secao" aria-labelledby="tarefas-titulo">
      <div class="secao-header">
        <h3 id="tarefas-titulo" class="secao-titulo">Para fazer</h3>
        <span v-if="pendentes.length" class="count-badge">{{ pendentes.length }}</span>
      </div>

      <div v-if="carregando" class="carregando">Carregando…</div>
      <div v-else class="lista-tarefas">
        <div v-if="!pendentes.length" class="vazio-hero">
          <p class="vazio-emoji">🎉</p>
          <p class="vazio-texto">Tudo em dia!</p>
        </div>
        <article
          v-for="t in pendentes"
          :key="t.id"
          class="tarefa-card"
          :class="[`status-${t.status}`, { concluindo: concluidoIds.has(t.id) }]"
        >
          <div class="tarefa-left">
            <div class="tarefa-dot"></div>
            <div>
              <p class="tarefa-titulo">{{ t.titulo }}</p>
              <p v-if="t.descricao" class="tarefa-desc">{{ t.descricao }}</p>
              <span v-if="t.aprovacao_automatica" class="tag-auto">⚡ Pontos automáticos</span>
            </div>
          </div>
          <div class="tarefa-right">
            <div class="pts-chip">⭐ {{ t.pontos }}</div>
            <button
              class="btn-concluir"
              :class="{ concluido: concluidoIds.has(t.id) }"
              :disabled="concluidoIds.has(t.id)"
              @click="concluir(t)"
              :aria-label="`Marcar ${t.titulo} como feita`"
            >
              {{ concluidoIds.has(t.id) ? '✓ Enviado!' : 'Feito!' }}
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Notificações recentes -->
    <section class="secao" aria-labelledby="notif-titulo">
      <div class="secao-header">
        <h3 id="notif-titulo" class="secao-titulo">Avisos</h3>
        <span v-if="naoLidas" class="count-badge notif-badge">{{ naoLidas }}</span>
      </div>
      <div class="lista-notif">
        <div v-if="!notificacoes.itens.length" class="vazio-inline">Sem novidades por aqui.</div>
        <div
          v-for="n in notificacoes.itens.slice(0, 4)"
          :key="n.id"
          class="notif-card"
          :class="{ 'nao-lida': !n.lida }"
          @click="notificacoes.marcarLida(n.id)"
          role="button"
          tabindex="0"
          :aria-label="n.titulo"
        >
          <div class="notif-dot" v-if="!n.lida"></div>
          <div>
            <p class="notif-titulo">{{ n.titulo }}</p>
            <p class="notif-msg">{{ n.mensagem }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Feedback imediato de conclusão -->
    <Transition name="feedback">
      <div v-if="feedback.visivel" class="feedback-overlay" aria-live="assertive" role="status">
        <div class="feedback-card" :class="feedback.tipo">
          <div class="feedback-icone">{{ feedback.icone }}</div>
          <p class="feedback-titulo">{{ feedback.titulo }}</p>
          <p class="feedback-msg">{{ feedback.msg }}</p>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { tarefasService, metasService, transacoesService, recompensasService } from '@/services'
import { useAuthStore } from '@/stores/auth'
import { useNotificacoesStore } from '@/stores/notificacoes'

const auth = useAuthStore()
const notificacoes = useNotificacoesStore()

const tarefas = ref([])
const metas = ref([])
const recompensas = ref([])
const pontosSemanais = ref(null)
const carregando = ref(true)
const concluidoIds = ref(new Set())

const feedback = reactive({ visivel: false, tipo: 'sucesso', icone: '', titulo: '', msg: '' })

const pendentes = computed(() => tarefas.value.filter((t) => t.status === 'pendente'))
const naoLidas = computed(() => notificacoes.itens.filter((n) => !n.lida).length)

// First-Then: primeira tarefa pendente + recompensa mais próxima de ser resgatada
const firstThen = computed(() => {
  const tarefa = pendentes.value[0] || null
  if (!tarefa) return { tarefa: null, recompensa: null, progressoPct: 0 }

  const pontos = auth.usuario?.pontos_disponiveis || 0
  const disponiveis = recompensas.value.filter((r) => r.ativa)
  // Recompensa mais próxima: menor custo que o filho ainda não pode pagar OU a mais barata possível
  const alvo = disponiveis
    .filter((r) => r.custo_pontos > pontos)
    .sort((a, b) => a.custo_pontos - b.custo_pontos)[0]
    || disponiveis.sort((a, b) => a.custo_pontos - b.custo_pontos)[0]
    || null

  const progressoPct = alvo
    ? Math.min(100, Math.round((pontos / alvo.custo_pontos) * 100))
    : 0

  return { tarefa, recompensa: alvo, progressoPct }
})

function mostrarFeedback(tipo, icone, titulo, msg) {
  Object.assign(feedback, { visivel: true, tipo, icone, titulo, msg })
  setTimeout(() => { feedback.visivel = false }, 3000)
}

async function concluir(tarefa) {
  if (concluidoIds.value.has(tarefa.id)) return
  concluidoIds.value = new Set([...concluidoIds.value, tarefa.id])

  try {
    await tarefasService.concluir(tarefa.id)
    await auth.carregarPerfil()
    await carregar()

    if (tarefa.aprovacao_automatica) {
      mostrarFeedback('sucesso-auto', '⭐', 'Arrasou!', `+${tarefa.pontos} pontos na conta!`)
    } else {
      mostrarFeedback('sucesso', '✅', 'Enviado!', 'Aguardando aprovação do responsável.')
    }
  } catch {
    concluidoIds.value = new Set([...concluidoIds.value].filter((id) => id !== tarefa.id))
    mostrarFeedback('erro', '❌', 'Ops!', 'Não foi possível concluir. Tente novamente.')
  }
}

async function carregar() {
  const resp = await tarefasService.listar({ tamanho: 50 })
  tarefas.value = resp.data
  carregando.value = false
}

async function carregarMetas() {
  const resp = await metasService.listar()
  metas.value = resp.data.filter((m) => m.status === 'ativa')
}

async function carregarSemanais() {
  try {
    const resp = await transacoesService.listar({ tamanho: 50 })
    const umaSemanaAtras = Date.now() - 7 * 24 * 60 * 60 * 1000
    pontosSemanais.value = resp.data
      .filter((t) => t.tipo === 'credito' || t.tipo === 'bonus')
      .filter((t) => new Date(t.criado_em).getTime() >= umaSemanaAtras)
      .reduce((soma, t) => soma + t.quantidade, 0)
  } catch {
    pontosSemanais.value = 0
  }
}

onMounted(async () => {
  await Promise.all([
    carregar(),
    carregarMetas(),
    carregarSemanais(),
    notificacoes.carregar(),
    recompensasService.listar().then((r) => { recompensas.value = r.data }),
  ])
})
</script>

<style scoped>
.dashboard-filho {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Hero ── */
.hero-pontos {
  background: var(--grad-filho);
  border-radius: var(--raio-grande);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--sombra-colorida);
  overflow: hidden;
  position: relative;
}
.hero-pontos::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 160px; height: 160px;
  background: rgba(255,255,255,0.07);
  border-radius: 50%;
}
.personagem {
  width: 76px; height: 76px; object-fit: contain;
  filter: drop-shadow(0 6px 16px rgba(0,0,0,0.25));
  animation: flutua 3s ease-in-out infinite;
  flex-shrink: 0; position: relative; z-index: 1;
}
@keyframes flutua {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-7px); }
}
.hero-conteudo { flex: 1; position: relative; z-index: 1; }
.hero-label { font-size: 0.72rem; font-weight: 600; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.08em; }
.hero-valor { font-size: 2.75rem; font-weight: 800; color: #fff; line-height: 1.1; text-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.hero-sub { font-size: 0.72rem; color: rgba(255,255,255,0.6); margin-top: 0.2rem; }
.hero-semana {
  text-align: center; background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.25); border-radius: var(--raio);
  padding: 0.5rem 0.75rem; flex-shrink: 0; position: relative; z-index: 1;
}
.semana-valor { font-size: 1.25rem; font-weight: 800; color: #fff; }
.semana-label { font-size: 0.65rem; color: rgba(255,255,255,0.7); font-weight: 600; text-transform: uppercase; }

/* ── First-Then ── */
.first-then {
  display: flex;
  align-items: stretch;
  gap: 0;
  background: #fff;
  border-radius: var(--raio);
  box-shadow: var(--sombra-xs);
  overflow: hidden;
  border: 2px solid #c4b5fd;
}
.ft-lado {
  flex: 1;
  padding: 0.9rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.ft-primeiro { background: #faf5ff; border-right: 2px solid #c4b5fd; }
.ft-depois { background: #f0fdf4; }

.ft-label {
  font-size: 0.65rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: 0.1em;
}
.ft-primeiro .ft-label { color: var(--cor-primaria); }
.ft-depois .ft-label { color: var(--cor-sucesso); }

.ft-conteudo { display: flex; flex-direction: column; gap: 0.35rem; }
.ft-icone { font-size: 1.5rem; }
.ft-texto { font-weight: 700; font-size: 0.85rem; line-height: 1.3; }
.ft-pts {
  font-size: 0.72rem; font-weight: 700;
  background: var(--cor-aviso-bg); color: #92400e;
  padding: 0.1rem 0.4rem; border-radius: var(--raio-pill); width: fit-content;
}

.ft-progresso-wrap { display: flex; align-items: center; gap: 0.4rem; }
.ft-progresso-barra { flex: 1; height: 6px; background: #d1fae5; border-radius: 999px; overflow: hidden; }
.ft-progresso-fill {
  height: 100%; background: var(--cor-sucesso); border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.25, 1, 0.5, 1); min-width: 3px;
}
.ft-progresso-label { font-size: 0.7rem; font-weight: 700; color: var(--cor-sucesso); white-space: nowrap; }
.ft-sem-recompensa .ft-texto { color: var(--cor-texto-suave); font-style: italic; }

.ft-seta {
  display: flex; align-items: center; justify-content: center;
  font-size: 1.25rem; font-weight: 800;
  color: var(--cor-primaria); padding: 0 0.25rem;
  background: linear-gradient(#faf5ff, #f0fdf4);
}

/* ── Seções ── */
.secao { display: flex; flex-direction: column; gap: 0.75rem; }
.secao-header { display: flex; align-items: center; gap: 0.6rem; }
.secao-titulo { font-size: 1rem; font-weight: 700; color: var(--cor-texto); }
.count-badge {
  background: var(--cor-primaria); color: #fff;
  font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.5rem; border-radius: var(--raio-pill);
}
.notif-badge { background: var(--cor-secundaria); }

/* ── Metas ── */
.lista-metas { display: flex; flex-direction: column; gap: 0.6rem; }
.meta-card {
  background: #fff; border-radius: var(--raio); padding: 0.9rem 1rem;
  border: 1.5px solid var(--cor-borda); box-shadow: var(--sombra-xs);
  display: flex; flex-direction: column; gap: 0.4rem;
}
.meta-header { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.meta-titulo { font-weight: 600; font-size: 0.88rem; }
.meta-pts { font-size: 0.75rem; font-weight: 700; color: var(--cor-primaria); flex-shrink: 0; }
.meta-track { height: 10px; background: var(--cor-fundo); border-radius: var(--raio-pill); overflow: hidden; }
.meta-fill {
  height: 100%; background: var(--grad-primario); border-radius: var(--raio-pill);
  transition: width 0.8s cubic-bezier(0.25, 1, 0.5, 1); min-width: 4px;
}
.meta-rodape { display: flex; align-items: center; justify-content: space-between; }
.meta-pct { font-size: 0.72rem; font-weight: 700; color: var(--cor-texto-suave); }
.meta-bonus {
  font-size: 0.7rem; font-weight: 700;
  background: var(--cor-aviso-bg); color: #92400e;
  padding: 0.1rem 0.45rem; border-radius: var(--raio-pill);
}

/* ── Tarefas ── */
.lista-tarefas { display: flex; flex-direction: column; gap: 0.6rem; }
.tarefa-card {
  background: #fff; border-radius: var(--raio); padding: 0.9rem 1rem;
  display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;
  box-shadow: var(--sombra-xs); border: 1.5px solid var(--cor-borda);
  border-left: 4px solid var(--cor-primaria);
  transition: opacity 0.3s, transform 0.3s;
}
.tarefa-card.status-em_andamento { border-left-color: var(--cor-aviso); }
.tarefa-card.concluindo { opacity: 0.55; transform: scale(0.98); }

.tarefa-left { display: flex; align-items: flex-start; gap: 0.6rem; flex: 1; min-width: 0; }
.tarefa-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--cor-primaria); margin-top: 0.45rem; flex-shrink: 0; }
.tarefa-titulo { font-weight: 600; font-size: 0.9rem; }
.tarefa-desc { font-size: 0.75rem; color: var(--cor-texto-suave); margin-top: 0.1rem; }

.tag-auto {
  display: inline-block; margin-top: 0.2rem;
  font-size: 0.68rem; font-weight: 700;
  background: #fef9c3; color: #713f12;
  padding: 0.1rem 0.4rem; border-radius: 999px;
}

.tarefa-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.4rem; flex-shrink: 0; }
.pts-chip {
  background: var(--cor-aviso-bg); color: #92400e;
  font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: var(--raio-pill);
}
.btn-concluir {
  background: var(--grad-primario); color: #fff; border: none;
  padding: 0.35rem 0.85rem; border-radius: var(--raio-pill);
  font-size: 0.78rem; font-weight: 700;
  box-shadow: 0 3px 8px rgba(124,58,237,0.3);
  transition: transform 0.12s, box-shadow 0.12s, background 0.2s;
}
.btn-concluir:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 5px 12px rgba(124,58,237,0.4); }
.btn-concluir:active { transform: scale(0.96); }
.btn-concluir.concluido {
  background: var(--grad-sucesso); box-shadow: 0 3px 8px rgba(16,185,129,0.3); cursor: default;
}

/* ── Vazio ── */
.vazio-hero {
  text-align: center; padding: 1.25rem;
  background: var(--cor-sucesso-bg); border-radius: var(--raio);
}
.vazio-emoji { font-size: 1.75rem; }
.vazio-texto { font-size: 0.9rem; font-weight: 600; color: #065f46; margin-top: 0.2rem; }
.vazio-inline { color: var(--cor-texto-suave); font-size: 0.85rem; padding: 0.5rem 0; }

/* ── Notificações ── */
.lista-notif { display: flex; flex-direction: column; gap: 0.5rem; }
.notif-card {
  background: #fff; border-radius: var(--raio); padding: 0.8rem 0.9rem;
  cursor: pointer; border: 1.5px solid var(--cor-borda); box-shadow: var(--sombra-xs);
  display: flex; gap: 0.6rem; align-items: flex-start; transition: border-color 0.15s;
}
.notif-card.nao-lida { border-color: var(--cor-primaria); background: var(--cor-primaria-clara); }
.notif-dot { width: 8px; height: 8px; background: var(--cor-primaria); border-radius: 50%; margin-top: 0.35rem; flex-shrink: 0; }
.notif-titulo { font-weight: 600; font-size: 0.85rem; }
.notif-msg { font-size: 0.75rem; color: var(--cor-texto-suave); margin-top: 0.1rem; line-height: 1.4; }

/* ── Feedback overlay ── */
.feedback-overlay {
  position: fixed; inset: 0; z-index: 300;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.35); backdrop-filter: blur(3px);
  pointer-events: none;
}
.feedback-card {
  background: #fff; border-radius: var(--raio-grande);
  padding: 2rem 2.5rem; text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
  min-width: 220px;
}
.feedback-card.sucesso-auto { border-top: 5px solid var(--cor-primaria); }
.feedback-card.sucesso { border-top: 5px solid var(--cor-sucesso); }
.feedback-card.erro { border-top: 5px solid var(--cor-erro); }

.feedback-icone { font-size: 3rem; animation: pop 0.3s cubic-bezier(0.17, 0.89, 0.32, 1.28); }
@keyframes pop {
  from { transform: scale(0.4); opacity: 0; }
  to   { transform: scale(1);   opacity: 1; }
}
.feedback-titulo { font-size: 1.3rem; font-weight: 800; color: var(--cor-texto); }
.feedback-msg { font-size: 0.88rem; color: var(--cor-texto-suave); }

.feedback-enter-active, .feedback-leave-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.feedback-enter-from, .feedback-leave-to { opacity: 0; transform: scale(0.92); }
</style>
