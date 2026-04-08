<template>
  <div>
    <div class="cabecalho">
      <h2 class="titulo-pagina">Recompensas</h2>
      <button class="btn btn-primario" @click="modalAberto = true">+ Nova recompensa</button>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>
    <div v-else class="grid">
      <div v-if="!recompensas.length" class="vazio">Nenhuma recompensa cadastrada.</div>
      <div v-for="r in recompensas" :key="r.id" class="card recompensa-card">
        <div class="recompensa-icone">🎁</div>
        <div class="recompensa-info">
          <p class="recompensa-titulo">{{ r.titulo }}</p>
          <p class="recompensa-custo">⭐ {{ r.custo_pontos }} pts</p>
          <p v-if="r.estoque !== null" class="recompensa-estoque">Estoque: {{ r.estoque }}</p>
        </div>
        <button class="btn btn-perigo btn-sm" @click="desativar(r.id)">Remover</button>
      </div>
    </div>

    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false">
      <div class="card modal">
        <h3>Nova recompensa</h3>
        <form @submit.prevent="criar">
          <div class="campo">
            <label>Título</label>
            <input v-model="nova.titulo" type="text" required />
          </div>
          <div class="campo">
            <label>Custo em pontos</label>
            <input v-model.number="nova.custo_pontos" type="number" min="1" required />
          </div>
          <div class="campo">
            <label>Estoque (deixe vazio para ilimitado)</label>
            <input v-model.number="nova.estoque" type="number" min="0" />
          </div>
          <div class="campo">
            <label>Descrição</label>
            <textarea v-model="nova.descricao" rows="2" />
          </div>
          <div class="modal-acoes">
            <button type="button" class="btn btn-outline" @click="modalAberto = false">Cancelar</button>
            <button type="submit" class="btn btn-primario">Criar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { recompensasService } from '@/services'

const recompensas = ref([])
const carregando = ref(true)
const modalAberto = ref(false)
const nova = reactive({ titulo: '', custo_pontos: 50, estoque: null, descricao: '' })

async function carregar() {
  const resp = await recompensasService.listar()
  recompensas.value = resp.data
  carregando.value = false
}

async function criar() {
  await recompensasService.criar({ ...nova, estoque: nova.estoque || null })
  modalAberto.value = false
  Object.assign(nova, { titulo: '', custo_pontos: 50, estoque: null, descricao: '' })
  await carregar()
}

async function desativar(id) {
  await recompensasService.deletar(id)
  await carregar()
}

onMounted(carregar)
</script>

<style scoped>
.cabecalho { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.titulo-pagina { font-size: 1.5rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.recompensa-card { display: flex; align-items: center; gap: 1rem; }
.recompensa-icone { font-size: 2rem; }
.recompensa-info { flex: 1; }
.recompensa-titulo { font-weight: 600; }
.recompensa-custo { color: var(--cor-primaria); font-weight: 600; font-size: 0.9rem; }
.recompensa-estoque { font-size: 0.82rem; color: var(--cor-texto-suave); }
.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.82rem; flex-shrink: 0; }
.vazio { text-align: center; color: var(--cor-texto-suave); padding: 2rem; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { width: 100%; max-width: 420px; display: flex; flex-direction: column; gap: 1rem; }
.modal form { display: flex; flex-direction: column; gap: 0.9rem; }
.modal-acoes { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
</style>
