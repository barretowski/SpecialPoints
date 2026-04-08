<template>
  <div class="grafico-wrap">
    <p class="grafico-titulo">Status das tarefas</p>
    <div class="grafico-inner">
      <Doughnut :data="chartData" :options="options" />
    </div>
    <div class="legenda">
      <div v-for="(item, i) in legenda" :key="i" class="legenda-item">
        <span class="legenda-dot" :style="{ background: item.cor }"></span>
        <span class="legenda-label">{{ item.label }}</span>
        <span class="legenda-valor">{{ item.valor }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  tarefas: { type: Array, default: () => [] },
})

const CORES = {
  pendente:     '#f59e0b',
  em_andamento: '#3b82f6',
  concluida:    '#10b981',
  rejeitada:    '#ef4444',
  expirada:     '#9ca3af',
}

const LABELS = {
  pendente:     'Pendentes',
  em_andamento: 'Aguardando',
  concluida:    'Concluídas',
  rejeitada:    'Rejeitadas',
  expirada:     'Expiradas',
}

const contagem = computed(() => {
  const c = { pendente: 0, em_andamento: 0, concluida: 0, rejeitada: 0, expirada: 0 }
  props.tarefas.forEach((t) => { if (c[t.status] !== undefined) c[t.status]++ })
  return c
})

const statusComDados = computed(() =>
  Object.entries(contagem.value).filter(([, v]) => v > 0)
)

const chartData = computed(() => ({
  labels: statusComDados.value.map(([k]) => LABELS[k]),
  datasets: [{
    data: statusComDados.value.map(([, v]) => v),
    backgroundColor: statusComDados.value.map(([k]) => CORES[k]),
    borderWidth: 0,
    hoverOffset: 6,
  }],
}))

const options = {
  responsive: true,
  maintainAspectRatio: true,
  cutout: '68%',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${ctx.parsed}`,
      },
    },
  },
}

const legenda = computed(() =>
  statusComDados.value.map(([k, v]) => ({
    cor: CORES[k],
    label: LABELS[k],
    valor: v,
  }))
)
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

.grafico-inner {
  width: 160px;
  height: 160px;
  margin: 0 auto;
}

.legenda {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.legenda-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
}

.legenda-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legenda-label {
  flex: 1;
  color: var(--cor-texto-suave);
}

.legenda-valor {
  font-weight: 700;
  color: var(--cor-texto);
}
</style>
