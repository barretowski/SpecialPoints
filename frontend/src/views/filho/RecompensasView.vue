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
import { recompensasService, resgatesService } from '@/services'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const recompensas = ref([])
const carregando = ref(true)
const toast = reactive({ visivel: false, msg: '', tipo: 'sucesso' })

const pontos = computed(() => auth.usuario?.pontos_disponiveis || 0)

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
    mostrarToast('Resgate solicitado! Aguarde a aprovação. 🎉')
  } catch (e) {
    mostrarToast(e.response?.data?.detail || 'Erro ao resgatar.', 'erro')
  }
}

onMounted(async () => {
  const resp = await recompensasService.listar()
  recompensas.value = resp.data
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

/* Grid */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.85rem; }

/* Card */
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

.recompensa-card:not(.bloqueada) {
  border-color: #c4b5fd;
}

.recompensa-card:not(.bloqueada):hover {
  transform: translateY(-2px);
  box-shadow: var(--sombra-md);
  border-color: var(--cor-primaria);
}

.recompensa-card.bloqueada { opacity: 0.75; }

.recompensa-topo {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.recompensa-icone-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--cor-primaria-clara);
  display: flex;
  align-items: center;
  justify-content: center;
}
.recompensa-icone { font-size: 1.5rem; }

.badge-desbloqueada {
  font-size: 0.68rem;
  font-weight: 700;
  color: #065f46;
  background: var(--cor-sucesso-bg);
  padding: 0.15rem 0.5rem;
  border-radius: var(--raio-pill);
}
.badge-bloqueada {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--cor-texto-suave);
  background: var(--cor-fundo);
  padding: 0.15rem 0.5rem;
  border-radius: var(--raio-pill);
}

.recompensa-titulo { font-weight: 700; font-size: 0.95rem; }
.recompensa-desc { font-size: 0.78rem; color: var(--cor-texto-suave); line-height: 1.4; }

/* Barra de progresso */
.recompensa-progresso { display: flex; flex-direction: column; gap: 0.3rem; }

.progresso-barra {
  height: 6px;
  background: var(--cor-borda);
  border-radius: var(--raio-pill);
  overflow: hidden;
}

.progresso-fill {
  height: 100%;
  background: var(--grad-primario);
  border-radius: var(--raio-pill);
  transition: width 0.5s ease;
}

.progresso-label { font-size: 0.72rem; font-weight: 600; color: var(--cor-texto-suave); }

/* Botão */
.btn-resgatar {
  width: 100%;
  padding: 0.55rem;
  border-radius: var(--raio);
  border: 2px solid var(--cor-borda);
  background: var(--cor-fundo);
  color: var(--cor-texto-suave);
  font-size: 0.85rem;
  font-weight: 700;
  transition: all 0.15s;
  cursor: not-allowed;
}

.btn-resgatar.ativo {
  background: var(--grad-primario);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 14px rgba(124,58,237,0.35);
  cursor: pointer;
}
.btn-resgatar.ativo:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(124,58,237,0.45); }
.btn-resgatar.ativo:active { transform: scale(0.98); }

/* Vazio */
.vazio-hero { text-align: center; padding: 2.5rem; }
.vazio-emoji { font-size: 3rem; margin-bottom: 0.5rem; }
.vazio-titulo { font-weight: 600; color: var(--cor-texto-suave); }

/* Toast */
.toast {
  position: fixed;
  bottom: 84px;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.75rem 1.5rem;
  border-radius: var(--raio-pill);
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: var(--sombra-md);
  z-index: 200;
  white-space: nowrap;
}
.toast-sucesso { background: var(--cor-texto); color: #fff; }
.toast-erro { background: var(--cor-erro); color: #fff; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
</style>
