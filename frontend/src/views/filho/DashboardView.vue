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
          :class="`status-${t.status}`"
        >
          <div class="tarefa-left">
            <div class="tarefa-dot"></div>
            <div>
              <p class="tarefa-titulo">{{ t.titulo }}</p>
              <p v-if="t.descricao" class="tarefa-desc">{{ t.descricao }}</p>
            </div>
          </div>
          <div class="tarefa-right">
            <div class="pts-chip">⭐ {{ t.pontos }}</div>
            <button
              class="btn-concluir"
              @click="concluir(t.id)"
              :aria-label="`Marcar ${t.titulo} como feita`"
            >
              Feito!
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

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { tarefasService, metasService, transacoesService } from '@/services'
import { useAuthStore } from '@/stores/auth'
import { useNotificacoesStore } from '@/stores/notificacoes'

const auth = useAuthStore()
const notificacoes = useNotificacoesStore()

const tarefas = ref([])
const metas = ref([])
const pontosSemanais = ref(null)
const carregando = ref(true)

const pendentes = computed(() => tarefas.value.filter((t) => t.status === 'pendente'))
const naoLidas = computed(() => notificacoes.itens.filter((n) => !n.lida).length)

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

async function concluir(id) {
  await tarefasService.concluir(id)
  await auth.carregarPerfil()
  await carregar()
}

onMounted(async () => {
  await Promise.all([
    carregar(),
    carregarMetas(),
    carregarSemanais(),
    notificacoes.carregar(),
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
  width: 76px; height: 76px;
  object-fit: contain;
  filter: drop-shadow(0 6px 16px rgba(0,0,0,0.25));
  animation: flutua 3s ease-in-out infinite;
  flex-shrink: 0;
  position: relative; z-index: 1;
}

@keyframes flutua {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-7px); }
}

.hero-conteudo { flex: 1; position: relative; z-index: 1; }
.hero-label {
  font-size: 0.72rem; font-weight: 600;
  color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.08em;
}
.hero-valor {
  font-size: 2.75rem; font-weight: 800; color: #fff; line-height: 1.1;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.hero-sub { font-size: 0.72rem; color: rgba(255,255,255,0.6); margin-top: 0.2rem; }

.hero-semana {
  text-align: center;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: var(--raio);
  padding: 0.5rem 0.75rem;
  flex-shrink: 0;
  position: relative; z-index: 1;
}
.semana-valor { font-size: 1.25rem; font-weight: 800; color: #fff; }
.semana-label { font-size: 0.65rem; color: rgba(255,255,255,0.7); font-weight: 600; text-transform: uppercase; }

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
  background: #fff;
  border-radius: var(--raio);
  padding: 0.9rem 1rem;
  border: 1.5px solid var(--cor-borda);
  box-shadow: var(--sombra-xs);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.meta-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.meta-titulo { font-weight: 600; font-size: 0.88rem; }
.meta-pts { font-size: 0.75rem; font-weight: 700; color: var(--cor-primaria); flex-shrink: 0; }

.meta-track {
  height: 10px;
  background: var(--cor-fundo);
  border-radius: var(--raio-pill);
  overflow: hidden;
}

.meta-fill {
  height: 100%;
  background: var(--grad-primario);
  border-radius: var(--raio-pill);
  transition: width 0.8s cubic-bezier(0.25, 1, 0.5, 1);
  min-width: 4px;
}

.meta-rodape {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.meta-pct { font-size: 0.72rem; font-weight: 700; color: var(--cor-texto-suave); }
.meta-bonus {
  font-size: 0.7rem; font-weight: 700;
  background: var(--cor-aviso-bg); color: #92400e;
  padding: 0.1rem 0.45rem; border-radius: var(--raio-pill);
}

/* ── Tarefas ── */
.lista-tarefas { display: flex; flex-direction: column; gap: 0.6rem; }

.tarefa-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 0.9rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  box-shadow: var(--sombra-xs);
  border: 1.5px solid var(--cor-borda);
  border-left: 4px solid var(--cor-primaria);
}

.tarefa-card.status-em_andamento { border-left-color: var(--cor-aviso); }

.tarefa-left { display: flex; align-items: flex-start; gap: 0.6rem; flex: 1; min-width: 0; }
.tarefa-dot {
  width: 8px; height: 8px; border-radius: 50%; background: var(--cor-primaria);
  margin-top: 0.45rem; flex-shrink: 0;
}
.tarefa-titulo { font-weight: 600; font-size: 0.9rem; }
.tarefa-desc { font-size: 0.75rem; color: var(--cor-texto-suave); margin-top: 0.1rem; }

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
  transition: transform 0.12s, box-shadow 0.12s;
}
.btn-concluir:hover { transform: translateY(-1px); box-shadow: 0 5px 12px rgba(124,58,237,0.4); }
.btn-concluir:active { transform: scale(0.96); }

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
.notif-dot {
  width: 8px; height: 8px; background: var(--cor-primaria);
  border-radius: 50%; margin-top: 0.35rem; flex-shrink: 0;
}
.notif-titulo { font-weight: 600; font-size: 0.85rem; }
.notif-msg { font-size: 0.75rem; color: var(--cor-texto-suave); margin-top: 0.1rem; line-height: 1.4; }
</style>
