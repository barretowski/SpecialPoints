<template>
  <div class="grafico-wrap">
    <p class="grafico-titulo">Pontos por filho</p>

    <div v-if="!filhos.length" class="vazio">Nenhum filho cadastrado.</div>

    <div v-else class="barras">
      <div v-for="f in filhos" :key="f.id" class="barra-row">
        <div class="barra-avatar" :style="{ background: avatarCor(f.nome) }">
          {{ f.nome[0].toUpperCase() }}
        </div>
        <div class="barra-dados">
          <div class="barra-header">
            <span class="barra-nome">{{ primeiroNome(f.nome) }}</span>
            <span class="barra-pts">⭐ {{ f.pontos_disponiveis }}</span>
          </div>
          <div class="barra-track">
            <div
              class="barra-fill"
              :style="{
                width: `${porcentagem(f.pontos_disponiveis)}%`,
                background: avatarCor(f.nome),
              }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  membros: { type: Array, default: () => [] },
})

const CORES = ['#7c3aed', '#ec4899', '#06b6d4', '#10b981', '#f59e0b', '#6366f1', '#ef4444']
function avatarCor(nome) { return CORES[nome.charCodeAt(0) % CORES.length] }
function primeiroNome(nome) { return nome.split(' ')[0] }

const filhos = computed(() => props.membros.filter((m) => m.papel === 'filho'))

const maxPontos = computed(() => Math.max(...filhos.value.map((f) => f.pontos_disponiveis), 1))

function porcentagem(pts) {
  return Math.max(4, Math.round((pts / maxPontos.value) * 100))
}
</script>

<style scoped>
.grafico-wrap {
  background: #fff;
  border-radius: var(--raio);
  border: 1.5px solid var(--cor-borda);
  padding: 1.25rem;
  box-shadow: var(--sombra-xs);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.grafico-titulo {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--cor-texto-suave);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.barras { display: flex; flex-direction: column; gap: 0.85rem; }

.barra-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.barra-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.barra-dados { flex: 1; min-width: 0; }

.barra-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.3rem;
}

.barra-nome {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--cor-texto);
}

.barra-pts {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--cor-texto-suave);
}

.barra-track {
  height: 8px;
  background: var(--cor-fundo);
  border-radius: var(--raio-pill);
  overflow: hidden;
}

.barra-fill {
  height: 100%;
  border-radius: var(--raio-pill);
  transition: width 0.8s cubic-bezier(0.25, 1, 0.5, 1);
}

.vazio {
  font-size: 0.85rem;
  color: var(--cor-texto-suave);
  text-align: center;
  padding: 0.75rem 0;
}
</style>
