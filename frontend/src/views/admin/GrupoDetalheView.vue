<template>
  <div>
    <div class="breadcrumb">
      <RouterLink to="/admin/grupos" class="link-voltar">← Grupos</RouterLink>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <template v-else-if="grupo">
      <!-- Cabeçalho do grupo -->
      <div class="grupo-header card">
        <div class="grupo-info">
          <h1 class="grupo-nome" v-if="!editando">{{ grupo.nome }}</h1>
          <div v-else class="editar-inline">
            <input v-model="nomeEdit" class="input-inline" />
            <button class="btn btn-primario btn-sm" @click="salvarNome" :disabled="salvando">
              {{ salvando ? '…' : 'Salvar' }}
            </button>
            <button class="btn btn-sm btn-cancelar" @click="editando = false">Cancelar</button>
          </div>
          <p class="grupo-codigo">
            Código de convite: <code class="codigo">{{ grupo.codigo_convite }}</code>
          </p>
          <p class="grupo-data">Criado em {{ formatarData(grupo.criado_em) }}</p>
        </div>
        <button v-if="!editando" class="btn btn-outline btn-sm" @click="iniciarEdicao">Editar nome</button>
      </div>

      <!-- Stats do grupo -->
      <div class="stats-row">
        <div class="stat-mini card">
          <p class="stat-mini-valor">{{ grupo.total_membros }}</p>
          <p class="stat-mini-label">Membros</p>
        </div>
        <div class="stat-mini card">
          <p class="stat-mini-valor">{{ grupo.total_tarefas }}</p>
          <p class="stat-mini-label">Tarefas</p>
        </div>
        <div class="stat-mini card">
          <p class="stat-mini-valor">⭐ {{ grupo.total_pontos_distribuidos }}</p>
          <p class="stat-mini-label">Pontos distribuídos</p>
        </div>
      </div>

      <!-- Membros -->
      <section class="secao">
        <div class="secao-header">
          <h2 class="secao-titulo">Membros</h2>
          <button class="btn btn-primario btn-sm" @click="modalMembro.aberto = true">+ Adicionar membro</button>
        </div>

        <div v-if="carregandoMembros" class="carregando">Carregando membros…</div>
        <div v-else-if="!membros.length" class="vazio">
          <p>Nenhum membro ainda.</p>
          <button class="btn btn-primario" style="margin-top:1rem" @click="modalMembro.aberto = true">Criar primeiro responsável</button>
        </div>

        <div v-else class="tabela-wrap">
          <table class="tabela">
            <thead>
              <tr>
                <th>#</th>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Papel</th>
                <th>Pontos</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in membros" :key="m.id">
                <td class="td-id">{{ m.id }}</td>
                <td class="td-nome">{{ m.nome }}</td>
                <td class="td-email">{{ m.email }}</td>
                <td><span class="badge-papel" :class="m.papel">{{ m.papel }}</span></td>
                <td class="td-centro">⭐ {{ m.pontos_disponiveis ?? '—' }}</td>
                <td>
                  <span class="badge-status" :class="{ ativo: m.ativo, inativo: !m.ativo }">
                    {{ m.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td>
                  <button
                    class="btn-acao"
                    :class="m.ativo ? 'btn-desativar' : 'btn-ativar'"
                    @click="alternarAtivo(m)"
                  >
                    {{ m.ativo ? 'Desativar' : 'Ativar' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <div v-else class="vazio">Grupo não encontrado.</div>

    <!-- Modal adicionar membro -->
    <div v-if="modalMembro.aberto" class="overlay" @click.self="fecharModalMembro">
      <div class="modal card">
        <h2 class="modal-titulo">Adicionar membro</h2>
        <form @submit.prevent="criarMembro">
          <div class="campo">
            <label for="m-nome">Nome</label>
            <input id="m-nome" v-model="modalMembro.nome" type="text" placeholder="Nome completo" required />
          </div>
          <div class="campo">
            <label for="m-email">E-mail</label>
            <input id="m-email" v-model="modalMembro.email" type="email" placeholder="email@exemplo.com" required />
          </div>
          <div class="campo">
            <label for="m-senha">Senha inicial</label>
            <input id="m-senha" v-model="modalMembro.senha" type="password" placeholder="mínimo 6 caracteres" required minlength="6" />
          </div>
          <div class="campo">
            <label for="m-papel">Papel</label>
            <select id="m-papel" v-model="modalMembro.papel">
              <option value="super_responsavel">Super Admin da família (recomendado para o 1º acesso)</option>
              <option value="responsavel">Responsável</option>
              <option value="filho">Filho(a)</option>
            </select>
          </div>
          <p class="dica-texto" v-if="modalMembro.papel === 'super_responsavel'">
            O Super Admin pode criar outros responsáveis e filhos dentro da família.
          </p>
          <p class="dica-texto" v-else-if="modalMembro.papel === 'responsavel'">
            O Responsável gerencia tarefas e recompensas, mas não pode criar membros.
          </p>
          <p v-if="modalMembro.erro" class="erro-texto">{{ modalMembro.erro }}</p>
          <div class="modal-acoes">
            <button type="button" class="btn btn-secundario" @click="fecharModalMembro">Cancelar</button>
            <button type="submit" class="btn btn-primario" :disabled="modalMembro.salvando">
              {{ modalMembro.salvando ? 'Criando…' : 'Criar membro' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminService } from '@/services'

const route = useRoute()

const grupo = ref(null)
const membros = ref([])
const carregando = ref(true)
const carregandoMembros = ref(true)
const editando = ref(false)
const nomeEdit = ref('')
const salvando = ref(false)

const modalMembro = reactive({
  aberto: false,
  nome: '',
  email: '',
  senha: '',
  papel: 'super_responsavel',
  erro: '',
  salvando: false,
})

function fecharModalMembro() {
  modalMembro.aberto = false
  modalMembro.nome = ''
  modalMembro.email = ''
  modalMembro.senha = ''
  modalMembro.papel = 'responsavel'
  modalMembro.erro = ''
}

async function criarMembro() {
  modalMembro.erro = ''
  modalMembro.salvando = true
  try {
    await adminService.criarMembro(grupo.value.id, {
      nome: modalMembro.nome,
      email: modalMembro.email,
      senha: modalMembro.senha,
      papel: modalMembro.papel,
    })
    fecharModalMembro()
    await carregarMembros()
    await carregarGrupo() // atualiza o contador de membros
  } catch (e) {
    modalMembro.erro = e.response?.data?.detail || 'Erro ao criar membro.'
  } finally {
    modalMembro.salvando = false
  }
}

async function carregarGrupo() {
  const resp = await adminService.obterGrupo(route.params.id)
  grupo.value = resp.data
}

async function carregarMembros() {
  carregandoMembros.value = true
  const resp = await adminService.membrosGrupo(route.params.id)
  membros.value = resp.data
  carregandoMembros.value = false
}

function iniciarEdicao() {
  nomeEdit.value = grupo.value.nome
  editando.value = true
}

async function salvarNome() {
  salvando.value = true
  try {
    await adminService.atualizarGrupo(grupo.value.id, { nome: nomeEdit.value })
    grupo.value.nome = nomeEdit.value
    editando.value = false
  } finally {
    salvando.value = false
  }
}

async function alternarAtivo(membro) {
  await adminService.ativarUsuario(membro.id, !membro.ativo)
  membro.ativo = !membro.ativo
}

function formatarData(iso) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })
}

onMounted(async () => {
  await carregarGrupo()
  carregando.value = false
  await carregarMembros()
})
</script>

<style scoped>
.breadcrumb { margin-bottom: 1rem; }
.link-voltar { color: var(--cor-primaria); font-size: 0.9rem; text-decoration: none; }
.link-voltar:hover { text-decoration: underline; }

.grupo-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 1.25rem 1.5rem;
}

.grupo-nome { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.4rem; }
.grupo-codigo { font-size: 0.88rem; color: var(--cor-texto-suave); margin-top: 0.35rem; }
.grupo-data { font-size: 0.82rem; color: var(--cor-texto-suave); margin-top: 0.15rem; }

.codigo {
  background: var(--cor-fundo);
  border: 1px solid var(--cor-borda);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.88rem;
  letter-spacing: 0.05em;
}

.editar-inline { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
.input-inline {
  border: 1px solid var(--cor-primaria);
  border-radius: var(--raio);
  padding: 0.4rem 0.75rem;
  font-size: 1rem;
  outline: none;
}
.btn-cancelar {
  background: var(--cor-fundo);
  border: 1px solid var(--cor-borda);
  color: var(--cor-texto);
  cursor: pointer;
  border-radius: var(--raio);
  padding: 0.4rem 0.75rem;
  font-size: 0.88rem;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--cor-primaria);
  color: var(--cor-primaria);
  border-radius: var(--raio);
  cursor: pointer;
  flex-shrink: 0;
}
.btn-outline:hover { background: #f0eeff; }

.stats-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.stat-mini {
  flex: 1;
  min-width: 120px;
  text-align: center;
  padding: 1rem;
}

.stat-mini-valor { font-size: 1.75rem; font-weight: 700; color: var(--cor-primaria); }
.stat-mini-label { font-size: 0.8rem; color: var(--cor-texto-suave); margin-top: 0.2rem; }

.secao { margin-top: 1.5rem; }
.secao-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.secao-titulo { font-size: 1.1rem; font-weight: 600; }

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
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cor-texto-suave);
  border-bottom: 1px solid var(--cor-borda);
}

.tabela td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--cor-borda);
  font-size: 0.9rem;
}

.tabela tbody tr:last-child td { border-bottom: none; }
.tabela tbody tr:hover { background: #fafafa; }

.td-id { color: var(--cor-texto-suave); font-size: 0.8rem; }
.td-nome { font-weight: 600; }
.td-email { color: var(--cor-texto-suave); font-size: 0.85rem; }
.td-centro { text-align: center; }

.badge-papel {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}
.badge-papel.responsavel { background: #e3f2fd; color: #1565c0; }
.badge-papel.filho { background: #e8f5e9; color: #2e7d32; }

.badge-status {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}
.badge-status.ativo { background: #e8f5e9; color: #2e7d32; }
.badge-status.inativo { background: #ffebee; color: #c62828; }

.btn-acao {
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
}
.btn-ativar { background: #e8f5e9; color: #2e7d32; }
.btn-ativar:hover { background: #c8e6c9; }
.btn-desativar { background: #ffebee; color: #c62828; }
.btn-desativar:hover { background: #ffcdd2; }

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
  max-width: 460px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-titulo { font-size: 1.2rem; font-weight: 700; }

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

.dica-texto {
  font-size: 0.83rem;
  color: var(--cor-texto-suave);
  background: #f0eeff;
  border-radius: var(--raio);
  padding: 0.6rem 0.85rem;
  border-left: 3px solid var(--cor-primaria);
}

.vazio {
  text-align: center;
  color: var(--cor-texto-suave);
  padding: 2rem;
  background: var(--cor-superficie);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio);
}
</style>
