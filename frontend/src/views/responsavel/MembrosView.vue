<template>
  <div>
    <div class="page-header">
      <h2 class="titulo-pagina">Membros da família</h2>
      <button v-if="auth.ehSuperResponsavel || auth.ehAdmin" class="btn btn-primario" @click="abrirModalCriar">
        + Adicionar membro
      </button>
    </div>

    <div v-if="auth.usuario?.familia_id" class="card codigo-card">
      <p>Código de convite da família:</p>
      <strong class="codigo">{{ codigoConvite || '—' }}</strong>
      <p class="codigo-hint">Compartilhe este código para que filhos entrem pela tela de cadastro.</p>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>
    <div v-else class="membros-lista">
      <div v-for="m in membros" :key="m.id" class="card membro-card">
        <div class="membro-avatar" :style="{ background: avatarCor(m.nome) }">
          {{ m.nome[0].toUpperCase() }}
        </div>
        <div class="membro-dados">
          <p class="membro-nome">{{ m.nome }}</p>
          <p class="membro-email">{{ m.email }}</p>
          <span class="badge" :class="badgeClasse(m.papel)">{{ labelPapel(m.papel) }}</span>
        </div>
        <div v-if="m.papel === 'filho'" class="membro-pontos">
          <p class="pts-valor">⭐ {{ m.pontos_disponiveis }}</p>
          <p class="pts-label">disponíveis</p>
          <p class="pts-acumulado">{{ m.pontos_acumulados }} acumulados</p>
        </div>
        <div class="membro-acoes" v-if="m.id !== auth.usuario?.id">
          <button class="btn-icone btn-editar" @click="abrirModalEditar(m)" title="Editar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button class="btn-icone btn-remover" @click="confirmarRemover(m)" title="Remover">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal criar membro -->
    <div v-if="modalCriar.aberto" class="overlay" @click.self="fecharModalCriar">
      <div class="modal card">
        <h2 class="modal-titulo">Adicionar membro</h2>
        <form @submit.prevent="criarMembro">
          <div class="campo">
            <label>Nome</label>
            <input v-model="modalCriar.nome" type="text" placeholder="Nome completo" required />
          </div>
          <div class="campo">
            <label>E-mail</label>
            <input v-model="modalCriar.email" type="email" placeholder="email@exemplo.com" required />
          </div>
          <div class="campo">
            <label>Senha inicial</label>
            <input v-model="modalCriar.senha" type="password" placeholder="Mínimo 6 caracteres" required minlength="6" />
          </div>
          <div class="campo">
            <label>Papel</label>
            <select v-model="modalCriar.papel">
              <option value="responsavel">Responsável</option>
              <option value="filho">Filho(a)</option>
            </select>
          </div>
          <p class="dica-texto">O membro receberá uma senha temporária e deverá alterá-la no primeiro acesso.</p>
          <p v-if="modalCriar.erro" class="erro-texto" role="alert">{{ modalCriar.erro }}</p>
          <div class="modal-acoes">
            <button type="button" class="btn btn-secundario" @click="fecharModalCriar">Cancelar</button>
            <button type="submit" class="btn btn-primario" :disabled="modalCriar.salvando">
              {{ modalCriar.salvando ? 'Criando…' : 'Criar membro' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal editar membro -->
    <div v-if="modalEditar.aberto" class="overlay" @click.self="fecharModalEditar">
      <div class="modal card">
        <h2 class="modal-titulo">Editar membro</h2>
        <form @submit.prevent="salvarEdicao">
          <div class="campo">
            <label>Nome</label>
            <input v-model="modalEditar.nome" type="text" placeholder="Nome completo" required />
          </div>
          <div class="campo">
            <label>E-mail</label>
            <input v-model="modalEditar.email" type="email" placeholder="email@exemplo.com" required />
          </div>
          <div class="campo">
            <label>Nova senha <span class="campo-opcional">(deixe em branco para manter)</span></label>
            <input v-model="modalEditar.nova_senha" type="password" placeholder="Mínimo 6 caracteres" minlength="6" />
          </div>
          <p v-if="modalEditar.erro" class="erro-texto" role="alert">{{ modalEditar.erro }}</p>
          <div class="modal-acoes">
            <button type="button" class="btn btn-secundario" @click="fecharModalEditar">Cancelar</button>
            <button type="submit" class="btn btn-primario" :disabled="modalEditar.salvando">
              {{ modalEditar.salvando ? 'Salvando…' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal confirmar remoção -->
    <div v-if="modalRemover.aberto" class="overlay" @click.self="modalRemover.aberto = false">
      <div class="modal card">
        <h2 class="modal-titulo">Remover membro</h2>
        <p>Tem certeza que deseja remover <strong>{{ modalRemover.membro?.nome }}</strong>? Esta ação desativará o acesso do usuário.</p>
        <p v-if="modalRemover.erro" class="erro-texto" role="alert">{{ modalRemover.erro }}</p>
        <div class="modal-acoes">
          <button type="button" class="btn btn-secundario" @click="modalRemover.aberto = false">Cancelar</button>
          <button type="button" class="btn btn-perigo" @click="removerMembro" :disabled="modalRemover.salvando">
            {{ modalRemover.salvando ? 'Removendo…' : 'Remover' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { usuariosService } from '@/services'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const membros = ref([])
const carregando = ref(true)
const codigoConvite = ref('')

const modalCriar = reactive({ aberto: false, nome: '', email: '', senha: '', papel: 'responsavel', erro: '', salvando: false })
const modalEditar = reactive({ aberto: false, id: null, nome: '', email: '', nova_senha: '', erro: '', salvando: false })
const modalRemover = reactive({ aberto: false, membro: null, erro: '', salvando: false })

function labelPapel(papel) {
  const map = { super_responsavel: 'Super Admin', responsavel: 'Responsável', filho: 'Filho(a)' }
  return map[papel] ?? papel
}

function badgeClasse(papel) {
  if (papel === 'super_responsavel') return 'badge-destaque'
  if (papel === 'responsavel') return 'badge-info'
  return 'badge-sucesso'
}

function avatarCor(nome) {
  const cores = ['#7c3aed','#4f46e5','#0891b2','#059669','#d97706','#dc2626','#db2777']
  return cores[(nome?.charCodeAt(0) || 0) % cores.length]
}

function abrirModalCriar() {
  Object.assign(modalCriar, { aberto: true, nome: '', email: '', senha: '', papel: 'responsavel', erro: '', salvando: false })
}

function fecharModalCriar() { modalCriar.aberto = false }

function abrirModalEditar(membro) {
  Object.assign(modalEditar, { aberto: true, id: membro.id, nome: membro.nome, email: membro.email, nova_senha: '', erro: '', salvando: false })
}

function fecharModalEditar() { modalEditar.aberto = false }

function confirmarRemover(membro) {
  Object.assign(modalRemover, { aberto: true, membro, erro: '', salvando: false })
}

async function criarMembro() {
  modalCriar.erro = ''
  modalCriar.salvando = true
  try {
    await usuariosService.criarMembro({ nome: modalCriar.nome, email: modalCriar.email, senha: modalCriar.senha, papel: modalCriar.papel })
    fecharModalCriar()
    await carregar()
  } catch (e) {
    modalCriar.erro = e.response?.data?.detail || 'Erro ao criar membro.'
  } finally {
    modalCriar.salvando = false
  }
}

async function salvarEdicao() {
  modalEditar.erro = ''
  modalEditar.salvando = true
  try {
    const payload = { nome: modalEditar.nome, email: modalEditar.email }
    if (modalEditar.nova_senha) payload.nova_senha = modalEditar.nova_senha
    await usuariosService.editarMembro(modalEditar.id, payload)
    fecharModalEditar()
    await carregar()
  } catch (e) {
    modalEditar.erro = e.response?.data?.detail || 'Erro ao editar membro.'
  } finally {
    modalEditar.salvando = false
  }
}

async function removerMembro() {
  modalRemover.erro = ''
  modalRemover.salvando = true
  try {
    await usuariosService.removerMembro(modalRemover.membro.id)
    modalRemover.aberto = false
    await carregar()
  } catch (e) {
    modalRemover.erro = e.response?.data?.detail || 'Erro ao remover membro.'
  } finally {
    modalRemover.salvando = false
  }
}

async function carregar() {
  carregando.value = true
  const resp = await usuariosService.familia()
  membros.value = resp.data
  codigoConvite.value = membros.value[0]?.familia_id ? `FAM-${membros.value[0].familia_id}` : ''
  carregando.value = false
}

onMounted(carregar)
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.titulo-pagina { font-size: 1.5rem; }

.codigo-card { margin-bottom: 1.5rem; display: flex; flex-direction: column; gap: 0.4rem; }
.codigo { font-size: 1.6rem; letter-spacing: 0.15em; color: var(--cor-primaria); }
.codigo-hint { font-size: 0.85rem; color: var(--cor-texto-suave); }

.membros-lista { display: flex; flex-direction: column; gap: 0.75rem; }

.membro-card { display: flex; align-items: center; gap: 1.25rem; }

.membro-avatar {
  width: 52px; height: 52px;
  border-radius: 50%;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; font-weight: 700;
  flex-shrink: 0;
}

.membro-dados { flex: 1; }
.membro-nome { font-weight: 600; }
.membro-email { font-size: 0.82rem; color: var(--cor-texto-suave); }

.membro-pontos { text-align: right; }
.pts-valor { font-size: 1.3rem; font-weight: 700; color: var(--cor-primaria); }
.pts-label { font-size: 0.78rem; color: var(--cor-texto-suave); }
.pts-acumulado { font-size: 0.8rem; color: var(--cor-texto-suave); }

.membro-acoes { display: flex; gap: 0.5rem; flex-shrink: 0; }

.btn-icone {
  width: 34px; height: 34px;
  border-radius: var(--raio);
  border: 1px solid var(--cor-borda);
  background: var(--cor-fundo);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  color: var(--cor-texto-suave);
}

.btn-editar:hover { background: var(--cor-primaria-clara); border-color: var(--cor-primaria); color: var(--cor-primaria); }
.btn-remover:hover { background: var(--cor-erro-bg); border-color: var(--cor-erro); color: var(--cor-erro); }

.badge-destaque { background: #ede7f6; color: #6a1b9a; }

.campo-opcional { font-size: 0.78rem; color: var(--cor-texto-suave); font-weight: 400; }

/* Modal */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100; padding: 1rem;
}
.modal { width: 100%; max-width: 440px; display: flex; flex-direction: column; gap: 1.25rem; }
.modal-titulo { font-size: 1.2rem; font-weight: 700; }
.modal-acoes { display: flex; justify-content: flex-end; gap: 0.75rem; }
.btn-secundario {
  background: var(--cor-fundo); border: 1px solid var(--cor-borda); color: var(--cor-texto);
  padding: 0.55rem 1.1rem; border-radius: var(--raio); font-size: 0.9rem; cursor: pointer;
}
.btn-perigo {
  background: var(--cor-erro); color: #fff;
  padding: 0.55rem 1.1rem; border-radius: var(--raio); font-size: 0.9rem; border: none; cursor: pointer;
}
.btn-perigo:hover { background: #dc2626; }
.dica-texto {
  font-size: 0.83rem; color: var(--cor-texto-suave); background: #f0eeff;
  border-radius: var(--raio); padding: 0.6rem 0.85rem; border-left: 3px solid var(--cor-primaria);
}
</style>
