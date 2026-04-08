<template>
  <div>
    <div class="page-header">
      <h2 class="titulo-pagina">Membros da família</h2>
      <button v-if="auth.ehSuperResponsavel" class="btn btn-primario" @click="abrirModal">
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
        <div class="membro-avatar">{{ m.nome[0].toUpperCase() }}</div>
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
      </div>
    </div>

    <!-- Modal adicionar membro (só super_responsavel) -->
    <div v-if="modal.aberto" class="overlay" @click.self="fecharModal">
      <div class="modal card">
        <h2 class="modal-titulo">Adicionar membro</h2>
        <form @submit.prevent="criarMembro">
          <div class="campo">
            <label for="m-nome">Nome</label>
            <input id="m-nome" v-model="modal.nome" type="text" placeholder="Nome completo" required />
          </div>
          <div class="campo">
            <label for="m-email">E-mail</label>
            <input id="m-email" v-model="modal.email" type="email" placeholder="email@exemplo.com" required />
          </div>
          <div class="campo">
            <label for="m-senha">Senha inicial</label>
            <input id="m-senha" v-model="modal.senha" type="password" placeholder="Mínimo 6 caracteres" required minlength="6" />
          </div>
          <div class="campo">
            <label for="m-papel">Papel</label>
            <select id="m-papel" v-model="modal.papel">
              <option value="responsavel">Responsável</option>
              <option value="filho">Filho(a)</option>
            </select>
          </div>
          <p class="dica-texto">O membro receberá uma senha temporária e deverá alterá-la no primeiro acesso.</p>
          <p v-if="modal.erro" class="erro-texto" role="alert">{{ modal.erro }}</p>
          <div class="modal-acoes">
            <button type="button" class="btn btn-secundario" @click="fecharModal">Cancelar</button>
            <button type="submit" class="btn btn-primario" :disabled="modal.salvando">
              {{ modal.salvando ? 'Criando…' : 'Criar membro' }}
            </button>
          </div>
        </form>
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

const modal = reactive({ aberto: false, nome: '', email: '', senha: '', papel: 'responsavel', erro: '', salvando: false })

function labelPapel(papel) {
  const map = { super_responsavel: 'Super Admin', responsavel: 'Responsável', filho: 'Filho(a)' }
  return map[papel] ?? papel
}

function badgeClasse(papel) {
  if (papel === 'super_responsavel') return 'badge-destaque'
  if (papel === 'responsavel') return 'badge-info'
  return 'badge-sucesso'
}

function abrirModal() {
  Object.assign(modal, { aberto: true, nome: '', email: '', senha: '', papel: 'responsavel', erro: '', salvando: false })
}

function fecharModal() {
  modal.aberto = false
}

async function criarMembro() {
  modal.erro = ''
  modal.salvando = true
  try {
    await usuariosService.criarMembro({ nome: modal.nome, email: modal.email, senha: modal.senha, papel: modal.papel })
    fecharModal()
    await carregar()
  } catch (e) {
    modal.erro = e.response?.data?.detail || 'Erro ao criar membro.'
  } finally {
    modal.salvando = false
  }
}

async function carregar() {
  carregando.value = true
  const resp = await usuariosService.familia()
  membros.value = resp.data
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
  background: var(--cor-primaria);
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

.badge-destaque { background: #ede7f6; color: #6a1b9a; }

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
.dica-texto {
  font-size: 0.83rem; color: var(--cor-texto-suave); background: #f0eeff;
  border-radius: var(--raio); padding: 0.6rem 0.85rem; border-left: 3px solid var(--cor-primaria);
}
</style>
