<template>
  <div>
    <h2 class="titulo-pagina">Dashboard</h2>

    <div class="cards-resumo">
      <div class="card resumo-card">
        <span class="resumo-icone">👨‍👩‍👧</span>
        <div>
          <p class="resumo-valor">{{ membros.length }}</p>
          <p class="resumo-label">Membros</p>
        </div>
      </div>
      <div class="card resumo-card">
        <span class="resumo-icone">✅</span>
        <div>
          <p class="resumo-valor">{{ pendentes }}</p>
          <p class="resumo-label">Tarefas pendentes</p>
        </div>
      </div>
      <div class="card resumo-card">
        <span class="resumo-icone">⏳</span>
        <div>
          <p class="resumo-valor">{{ aguardando }}</p>
          <p class="resumo-label">Aguardando aprovação</p>
        </div>
      </div>
    </div>

    <div class="secao">
      <h3>Membros da família</h3>
      <div v-if="carregando" class="carregando">Carregando…</div>
      <div v-else class="membros-grid">
        <div v-for="m in membros" :key="m.id" class="card membro-card">
          <div class="membro-avatar">{{ m.nome[0].toUpperCase() }}</div>
          <div>
            <p class="membro-nome">{{ m.nome }}</p>
            <p class="membro-papel">{{ m.papel === 'filho' ? 'Filho(a)' : 'Responsável' }}</p>
            <p class="membro-pontos">⭐ {{ m.pontos_disponiveis }} pts disponíveis</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { usuariosService, tarefasService } from '@/services'

const membros = ref([])
const tarefas = ref([])
const carregando = ref(true)

const pendentes = computed(() => tarefas.value.filter((t) => t.status === 'pendente').length)
const aguardando = computed(() => tarefas.value.filter((t) => t.status === 'em_andamento').length)

onMounted(async () => {
  const [respMembros, respTarefas] = await Promise.all([
    usuariosService.familia(),
    tarefasService.listar({ tamanho: 100 }),
  ])
  membros.value = respMembros.data
  tarefas.value = respTarefas.data
  carregando.value = false
})
</script>

<style scoped>
.titulo-pagina { font-size: 1.5rem; margin-bottom: 1.5rem; }

.cards-resumo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.resumo-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.resumo-icone { font-size: 2rem; }
.resumo-valor { font-size: 1.8rem; font-weight: 700; color: var(--cor-primaria); }
.resumo-label { font-size: 0.85rem; color: var(--cor-texto-suave); }

.secao { margin-top: 1.5rem; }
.secao h3 { margin-bottom: 1rem; }

.membros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.membro-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.membro-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--cor-primaria);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: 700;
  flex-shrink: 0;
}

.membro-nome { font-weight: 600; }
.membro-papel { font-size: 0.82rem; color: var(--cor-texto-suave); }
.membro-pontos { font-size: 0.88rem; color: var(--cor-primaria); margin-top: 2px; }
</style>
