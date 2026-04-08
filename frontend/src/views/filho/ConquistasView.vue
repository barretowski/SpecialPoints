<template>
  <div class="conquistas-filho">

    <!-- Cabeçalho com progresso -->
    <div class="progresso-banner">
      <div class="progresso-info">
        <p class="progresso-label">Conquistas desbloqueadas</p>
        <p class="progresso-valor">{{ conquistadas.length }} / {{ TODOS_BADGES.length }}</p>
      </div>
      <div class="progresso-barra-wrap">
        <div class="progresso-barra">
          <div
            class="progresso-fill"
            :style="{ width: `${Math.round((conquistadas.length / TODOS_BADGES.length) * 100)}%` }"
          ></div>
        </div>
        <p class="progresso-pct">{{ Math.round((conquistadas.length / TODOS_BADGES.length) * 100) }}%</p>
      </div>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <div v-else class="grid-badges">
      <div
        v-for="badge in TODOS_BADGES"
        :key="badge.tipo"
        class="badge-card"
        :class="{ desbloqueada: temConquista(badge.tipo), bloqueada: !temConquista(badge.tipo) }"
      >
        <div class="badge-icone-wrap">
          <span class="badge-icone">{{ badge.icone }}</span>
          <span v-if="!temConquista(badge.tipo)" class="badge-lock">🔒</span>
        </div>
        <p class="badge-titulo">{{ badge.titulo }}</p>
        <p class="badge-desc">{{ badge.descricao }}</p>
        <p v-if="temConquista(badge.tipo)" class="badge-data">
          {{ formatarData(getConquista(badge.tipo)?.conquistado_em) }}
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { conquistasService } from '@/services'

const conquistadas = ref([])
const carregando = ref(true)

const TODOS_BADGES = [
  { tipo: 'primeira_tarefa',   titulo: 'Primeira tarefa!',   descricao: 'Conclua sua primeira tarefa',   icone: '🌟' },
  { tipo: 'dez_tarefas',       titulo: 'Dedicado',           descricao: 'Conclua 10 tarefas',            icone: '🔥' },
  { tipo: 'cinquenta_tarefas', titulo: 'Campeão',            descricao: 'Conclua 50 tarefas',            icone: '🏆' },
  { tipo: 'primeira_meta',     titulo: 'Meta atingida!',     descricao: 'Conclua sua primeira meta',     icone: '🎯' },
  { tipo: 'primeiro_resgate',  titulo: 'Primeiro prêmio!',   descricao: 'Faça seu primeiro resgate',     icone: '🎁' },
  { tipo: 'pontos_100',        titulo: 'Centenário',         descricao: 'Acumule 100 pontos',            icone: '💯' },
  { tipo: 'pontos_500',        titulo: 'Explorador',         descricao: 'Acumule 500 pontos',            icone: '💎' },
  { tipo: 'pontos_1000',       titulo: 'Lendário',           descricao: 'Acumule 1000 pontos',           icone: '👑' },
]

const conquistadasMap = computed(() =>
  Object.fromEntries(conquistadas.value.map((c) => [c.tipo, c]))
)

function temConquista(tipo) { return tipo in conquistadasMap.value }
function getConquista(tipo) { return conquistadasMap.value[tipo] || null }

function formatarData(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  const resp = await conquistasService.listar()
  conquistadas.value = resp.data
  carregando.value = false
})
</script>

<style scoped>
.conquistas-filho { display: flex; flex-direction: column; gap: 1.25rem; }

/* Banner de progresso */
.progresso-banner {
  background: var(--grad-primario);
  border-radius: var(--raio);
  padding: 1.1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 6px 20px rgba(124,58,237,0.3);
}

.progresso-label {
  font-size: 0.72rem; font-weight: 600;
  color: rgba(255,255,255,0.75); text-transform: uppercase; letter-spacing: 0.07em;
}

.progresso-valor { font-size: 1.6rem; font-weight: 800; color: #fff; line-height: 1.1; }

.progresso-barra-wrap { display: flex; align-items: center; gap: 0.75rem; }

.progresso-barra {
  flex: 1; height: 8px;
  background: rgba(255,255,255,0.25); border-radius: var(--raio-pill); overflow: hidden;
}
.progresso-fill {
  height: 100%; background: #fff; border-radius: var(--raio-pill);
  transition: width 0.8s cubic-bezier(0.25, 1, 0.5, 1); min-width: 4px;
}
.progresso-pct { font-size: 0.8rem; font-weight: 800; color: rgba(255,255,255,0.9); white-space: nowrap; }

/* Grid */
.grid-badges {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.85rem;
}

/* Card */
.badge-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 1.1rem 0.9rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  text-align: center;
  border: 2px solid var(--cor-borda);
  box-shadow: var(--sombra-xs);
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}

.desbloqueada {
  border-color: #c4b5fd;
}
.desbloqueada:hover { transform: translateY(-2px); box-shadow: var(--sombra-md); border-color: var(--cor-primaria); }

.bloqueada { opacity: 0.45; filter: grayscale(0.4); }

.badge-icone-wrap {
  width: 56px; height: 56px; border-radius: 16px;
  background: var(--cor-primaria-clara);
  display: flex; align-items: center; justify-content: center;
  position: relative;
}

.bloqueada .badge-icone-wrap { background: var(--cor-fundo); }

.badge-icone { font-size: 1.75rem; }

.badge-lock {
  position: absolute; bottom: -4px; right: -4px;
  font-size: 0.7rem; background: var(--cor-fundo);
  border-radius: 50%; width: 18px; height: 18px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--cor-borda);
}

.badge-titulo { font-weight: 700; font-size: 0.85rem; color: var(--cor-texto); }
.badge-desc { font-size: 0.72rem; color: var(--cor-texto-suave); line-height: 1.35; }
.badge-data { font-size: 0.68rem; color: var(--cor-primaria); font-weight: 600; margin-top: 0.1rem; }
</style>
