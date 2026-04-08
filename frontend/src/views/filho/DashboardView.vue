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
        <p class="hero-sub">{{ auth.usuario?.pontos_acumulados || 0 }} pontos no total</p>
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
import { tarefasService } from '@/services'
import { useAuthStore } from '@/stores/auth'
import { useNotificacoesStore } from '@/stores/notificacoes'

const auth = useAuthStore()
const notificacoes = useNotificacoesStore()

const tarefas = ref([])
const carregando = ref(true)

const pendentes = computed(() => tarefas.value.filter((t) => t.status === 'pendente'))
const naoLidas = computed(() => notificacoes.itens.filter((n) => !n.lida).length)

async function carregar() {
  const resp = await tarefasService.listar({ tamanho: 50 })
  tarefas.value = resp.data
  carregando.value = false
}

async function concluir(id) {
  await tarefasService.concluir(id)
  await auth.carregarPerfil()
  await carregar()
}

onMounted(async () => {
  await Promise.all([carregar(), notificacoes.carregar()])
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
  padding: 1.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: var(--sombra-colorida);
  overflow: hidden;
  position: relative;
}

.hero-pontos::before {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 150px;
  height: 150px;
  background: rgba(255,255,255,0.08);
  border-radius: 50%;
}

.personagem {
  width: 90px;
  height: 90px;
  object-fit: contain;
  filter: drop-shadow(0 8px 20px rgba(0,0,0,0.3));
  animation: flutua 3s ease-in-out infinite;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

@keyframes flutua {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-8px); }
}

.hero-conteudo {
  position: relative;
  z-index: 1;
}

.hero-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255,255,255,0.75);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.1rem;
}

.hero-valor {
  font-size: 3.25rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.hero-sub {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.65);
  margin-top: 0.3rem;
}

/* ── Seções ── */
.secao { display: flex; flex-direction: column; gap: 0.75rem; }

.secao-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.secao-titulo {
  font-size: 1rem;
  font-weight: 700;
  color: var(--cor-texto);
}

.count-badge {
  background: var(--cor-primaria);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.1rem 0.5rem;
  border-radius: var(--raio-pill);
}

.notif-badge { background: var(--cor-secundaria); }

/* ── Tarefa card ── */
.lista-tarefas { display: flex; flex-direction: column; gap: 0.6rem; }

.tarefa-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 1rem 1.1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  box-shadow: var(--sombra-xs);
  border: 1.5px solid var(--cor-borda);
  border-left: 4px solid var(--cor-primaria);
  transition: transform 0.15s, box-shadow 0.15s;
}

.tarefa-card:active { transform: scale(0.99); }

.tarefa-card.status-em_andamento { border-left-color: var(--cor-aviso); }
.tarefa-card.status-concluida { border-left-color: var(--cor-sucesso); opacity: 0.7; }

.tarefa-left {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.tarefa-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cor-primaria);
  margin-top: 0.4rem;
  flex-shrink: 0;
}

.tarefa-titulo {
  font-weight: 600;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tarefa-desc {
  font-size: 0.78rem;
  color: var(--cor-texto-suave);
  margin-top: 0.1rem;
}

.tarefa-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.4rem;
  flex-shrink: 0;
}

.pts-chip {
  background: var(--cor-aviso-bg);
  color: #92400e;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: var(--raio-pill);
}

.btn-concluir {
  background: var(--grad-primario);
  color: #fff;
  border: none;
  padding: 0.35rem 0.9rem;
  border-radius: var(--raio-pill);
  font-size: 0.8rem;
  font-weight: 700;
  box-shadow: 0 3px 8px rgba(124,58,237,0.3);
  transition: transform 0.12s, box-shadow 0.12s;
}
.btn-concluir:hover { transform: translateY(-1px); box-shadow: 0 5px 12px rgba(124,58,237,0.4); }
.btn-concluir:active { transform: scale(0.96); }

/* ── Vazio ── */
.vazio-hero {
  text-align: center;
  padding: 1.5rem;
  background: var(--cor-sucesso-bg);
  border-radius: var(--raio);
}
.vazio-emoji { font-size: 2rem; }
.vazio-texto { font-size: 0.95rem; font-weight: 600; color: #065f46; margin-top: 0.25rem; }

.vazio-inline { color: var(--cor-texto-suave); font-size: 0.88rem; padding: 0.75rem 0; }

/* ── Notificações ── */
.lista-notif { display: flex; flex-direction: column; gap: 0.5rem; }

.notif-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 0.85rem 1rem;
  cursor: pointer;
  border: 1.5px solid var(--cor-borda);
  box-shadow: var(--sombra-xs);
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  transition: border-color 0.15s;
}

.notif-card.nao-lida {
  border-color: var(--cor-primaria);
  background: var(--cor-primaria-clara);
}

.notif-dot {
  width: 8px;
  height: 8px;
  background: var(--cor-primaria);
  border-radius: 50%;
  margin-top: 0.4rem;
  flex-shrink: 0;
}

.notif-titulo { font-weight: 600; font-size: 0.88rem; }
.notif-msg { font-size: 0.78rem; color: var(--cor-texto-suave); margin-top: 0.1rem; line-height: 1.4; }
</style>
