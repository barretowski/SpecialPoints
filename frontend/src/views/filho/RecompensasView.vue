<template>
  <div>
    <h2 class="titulo-pagina">Recompensas</h2>
    <p class="seus-pontos" aria-live="polite">Você tem <strong>⭐ {{ auth.usuario?.pontos_disponiveis || 0 }} pontos</strong></p>

    <div v-if="carregando" class="carregando">Carregando…</div>
    <div v-else class="grid">
      <div v-if="!recompensas.length" class="vazio">Nenhuma recompensa disponível.</div>
      <article v-for="r in recompensas" :key="r.id" class="card recompensa-card">
        <div class="recompensa-icone" aria-hidden="true">🎁</div>
        <h3 class="recompensa-titulo">{{ r.titulo }}</h3>
        <p v-if="r.descricao" class="recompensa-desc">{{ r.descricao }}</p>
        <p class="recompensa-custo">⭐ {{ r.custo_pontos }} pontos</p>
        <button
          class="btn btn-primario"
          :disabled="(auth.usuario?.pontos_disponiveis || 0) < r.custo_pontos"
          @click="resgatar(r.id)"
          :aria-label="`Resgatar ${r.titulo} por ${r.custo_pontos} pontos`"
        >
          {{ (auth.usuario?.pontos_disponiveis || 0) >= r.custo_pontos ? 'Resgatar' : 'Pontos insuficientes' }}
        </button>
      </article>
    </div>

    <div v-if="mensagem" class="mensagem-sucesso" role="status" aria-live="polite">
      {{ mensagem }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { recompensasService, resgatesService } from '@/services'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const recompensas = ref([])
const carregando = ref(true)
const mensagem = ref('')

async function carregar() {
  const resp = await recompensasService.listar()
  recompensas.value = resp.data
  carregando.value = false
}

async function resgatar(id) {
  try {
    await resgatesService.solicitar(id)
    await auth.carregarPerfil()
    mensagem.value = 'Resgate solicitado! Aguarde a aprovação do responsável.'
    setTimeout(() => (mensagem.value = ''), 4000)
  } catch (e) {
    mensagem.value = e.response?.data?.detail || 'Erro ao resgatar.'
    setTimeout(() => (mensagem.value = ''), 4000)
  }
}

onMounted(carregar)
</script>

<style scoped>
.titulo-pagina { font-size: 1.4rem; margin-bottom: 0.5rem; }
.seus-pontos { color: var(--cor-texto-suave); margin-bottom: 1.25rem; font-size: 1rem; }
.seus-pontos strong { color: var(--cor-primaria); }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }

.recompensa-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.6rem;
}
.recompensa-icone { font-size: 2.5rem; }
.recompensa-titulo { font-size: 1rem; font-weight: 600; }
.recompensa-desc { font-size: 0.82rem; color: var(--cor-texto-suave); }
.recompensa-custo { font-weight: 700; color: var(--cor-primaria); font-size: 1.1rem; }

.recompensa-card .btn { width: 100%; justify-content: center; }
.recompensa-card .btn:disabled { background: var(--cor-borda); color: var(--cor-texto-suave); cursor: not-allowed; }

.vazio { text-align: center; color: var(--cor-texto-suave); padding: 2rem; }

.mensagem-sucesso {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--cor-sucesso);
  color: #fff;
  padding: 0.85rem 1.5rem;
  border-radius: var(--raio);
  font-weight: 500;
  box-shadow: var(--sombra);
}
</style>
