<template>
  <div>
    <div class="page-header">
      <h1 class="titulo-pagina">Grupos / Famílias</h1>
      <button class="btn btn-primario" @click="abrirModal()">+ Novo Grupo</button>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <div v-else>
      <div v-if="!grupos.length" class="vazio">Nenhum grupo cadastrado ainda.</div>

      <div class="tabela-wrap">
        <table v-if="grupos.length" class="tabela">
          <thead>
            <tr>
              <th>#</th>
              <th>Nome</th>
              <th>Código de convite</th>
              <th>Membros</th>
              <th>Criado em</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in grupos" :key="g.id">
              <td class="td-id">{{ g.id }}</td>
              <td class="td-nome">{{ g.nome }}</td>
              <td><code class="codigo">{{ g.codigo_convite }}</code></td>
              <td class="td-centro">{{ g.total_membros }}</td>
              <td class="td-data">{{ formatarData(g.criado_em) }}</td>
              <td class="td-acoes">
                <RouterLink :to="`/admin/grupos/${g.id}`" class="btn-acao btn-ver">Ver</RouterLink>
                <button class="btn-acao btn-editar" @click="abrirModal(g)">Editar</button>
                <button class="btn-acao btn-excluir" @click="confirmarExcluir(g)">Excluir</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal criar/editar -->
    <div v-if="modal.aberto" class="overlay" @click.self="fecharModal">
      <div class="modal card">
        <h2 class="modal-titulo">{{ modal.editando ? 'Editar Grupo' : 'Novo Grupo' }}</h2>
        <form @submit.prevent="salvar">
          <div class="campo">
            <label for="nome-grupo">Nome do grupo</label>
            <input
              id="nome-grupo"
              v-model="modal.nome"
              type="text"
              placeholder="Ex: Família Silva"
              required
              autofocus
            />
          </div>
          <p v-if="modal.erro" class="erro-texto">{{ modal.erro }}</p>
          <div class="modal-acoes">
            <button type="button" class="btn btn-secundario" @click="fecharModal">Cancelar</button>
            <button type="submit" class="btn btn-primario" :disabled="modal.salvando">
              {{ modal.salvando ? 'Salvando…' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmação exclusão -->
    <div v-if="excluir.aberto" class="overlay" @click.self="excluir.aberto = false">
      <div class="modal card">
        <h2 class="modal-titulo">Excluir grupo?</h2>
        <p class="modal-desc">Tem certeza que deseja excluir <strong>{{ excluir.grupo?.nome }}</strong>? Esta ação não pode ser desfeita.</p>
        <p v-if="excluir.erro" class="erro-texto">{{ excluir.erro }}</p>
        <div class="modal-acoes">
          <button class="btn btn-secundario" @click="excluir.aberto = false">Cancelar</button>
          <button class="btn btn-perigo" :disabled="excluir.carregando" @click="deletar">
            {{ excluir.carregando ? 'Excluindo…' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminService } from '@/services'

const route = useRoute()

const grupos = ref([])
const carregando = ref(true)

const modal = reactive({ aberto: false, editando: null, nome: '', erro: '', salvando: false })
const excluir = reactive({ aberto: false, grupo: null, carregando: false, erro: '' })

async function carregar() {
  const resp = await adminService.listarGrupos({ tamanho: 100 })
  grupos.value = resp.data
  carregando.value = false
}

function abrirModal(grupo = null) {
  modal.editando = grupo
  modal.nome = grupo?.nome || ''
  modal.erro = ''
  modal.salvando = false
  modal.aberto = true
}

function fecharModal() {
  modal.aberto = false
}

async function salvar() {
  modal.erro = ''
  modal.salvando = true
  try {
    if (modal.editando) {
      await adminService.atualizarGrupo(modal.editando.id, { nome: modal.nome })
    } else {
      await adminService.criarGrupo({ nome: modal.nome })
    }
    fecharModal()
    await carregar()
  } catch (e) {
    modal.erro = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    modal.salvando = false
  }
}

function confirmarExcluir(grupo) {
  excluir.grupo = grupo
  excluir.erro = ''
  excluir.carregando = false
  excluir.aberto = true
}

async function deletar() {
  excluir.carregando = true
  excluir.erro = ''
  try {
    await adminService.deletarGrupo(excluir.grupo.id)
    excluir.aberto = false
    await carregar()
  } catch (e) {
    excluir.erro = e.response?.data?.detail || 'Erro ao excluir.'
  } finally {
    excluir.carregando = false
  }
}

function formatarData(iso) {
  return new Date(iso).toLocaleDateString('pt-BR')
}

onMounted(async () => {
  await carregar()
  if (route.query.novo) abrirModal()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.titulo-pagina {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--cor-texto);
}

.tabela-wrap { overflow-x: auto; }

.tabela {
  width: 100%;
  border-collapse: collapse;
  background: var(--cor-superficie);
  border-radius: var(--raio);
  overflow: hidden;
  border: 1px solid var(--cor-borda);
}

.tabela th {
  background: var(--cor-fundo);
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cor-texto-suave);
  border-bottom: 1px solid var(--cor-borda);
}

.tabela td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--cor-borda);
  font-size: 0.9rem;
}

.tabela tbody tr:last-child td { border-bottom: none; }
.tabela tbody tr:hover { background: #fafafa; }

.td-id { color: var(--cor-texto-suave); font-size: 0.8rem; }
.td-nome { font-weight: 600; }
.td-centro { text-align: center; }
.td-data { color: var(--cor-texto-suave); font-size: 0.85rem; }

.codigo {
  background: var(--cor-fundo);
  border: 1px solid var(--cor-borda);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85rem;
  letter-spacing: 0.05em;
}

.td-acoes { display: flex; gap: 0.4rem; align-items: center; }

.btn-acao {
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn-ver { background: #e8e6ff; color: var(--cor-primaria); }
.btn-ver:hover { background: #d4d0ff; }
.btn-editar { background: #e8f5e9; color: #2e7d32; }
.btn-editar:hover { background: #c8e6c9; }
.btn-excluir { background: #ffebee; color: #c62828; }
.btn-excluir:hover { background: #ffcdd2; }

.vazio {
  text-align: center;
  color: var(--cor-texto-suave);
  padding: 3rem;
  background: var(--cor-superficie);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio);
}

/* Modal */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-titulo { font-size: 1.2rem; font-weight: 700; }
.modal-desc { color: var(--cor-texto-suave); font-size: 0.95rem; }

.modal-acoes {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secundario {
  background: var(--cor-fundo);
  border: 1px solid var(--cor-borda);
  color: var(--cor-texto);
  padding: 0.55rem 1.1rem;
  border-radius: var(--raio);
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-perigo {
  background: #c62828;
  color: #fff;
  border: none;
  padding: 0.55rem 1.1rem;
  border-radius: var(--raio);
  font-size: 0.9rem;
  cursor: pointer;
}
.btn-perigo:hover { background: #b71c1c; }
.btn-perigo:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
