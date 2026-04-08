<template>
  <div>
    <div class="cabecalho">
      <h2 class="titulo-pagina">Recompensas</h2>
      <button class="btn btn-primario" @click="abrirModal()">+ Nova recompensa</button>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>

    <template v-else>
      <!-- Disponíveis -->
      <section class="secao">
        <div class="secao-header">
          <h3 class="secao-titulo">Disponíveis</h3>
          <span class="count-badge">{{ disponiveis.length }}</span>
        </div>
        <div v-if="!disponiveis.length" class="vazio">Nenhuma recompensa disponível. Crie a primeira!</div>
        <div v-else class="grid">
          <div v-for="r in disponiveis" :key="r.id" class="recompensa-card card-disponivel">
            <div class="card-topo">
              <div class="icone-wrap">🎁</div>
              <div class="card-acoes">
                <button class="btn-icone btn-editar" title="Editar" @click="abrirModal(r)">✏️</button>
                <button class="btn-icone btn-remover" title="Desativar" @click="confirmarDesativar(r)">🗑️</button>
              </div>
            </div>
            <p class="card-titulo">{{ r.titulo }}</p>
            <p v-if="r.descricao" class="card-desc">{{ r.descricao }}</p>
            <div class="card-rodape">
              <span class="pts-chip">⭐ {{ r.custo_pontos }} pts</span>
              <span v-if="r.estoque !== null" class="estoque-chip" :class="estoqueClasse(r.estoque)">
                {{ r.estoque === 0 ? 'Sem estoque' : `${r.estoque} em estoque` }}
              </span>
              <span v-else class="estoque-chip estoque-ilimitado">∞ Ilimitado</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Esgotadas / Desativadas -->
      <section class="secao" v-if="esgotadas.length">
        <div class="secao-header">
          <h3 class="secao-titulo secao-titulo-inativa">Esgotadas / Desativadas</h3>
          <span class="count-badge count-badge-inativo">{{ esgotadas.length }}</span>
        </div>
        <div class="grid">
          <div v-for="r in esgotadas" :key="r.id" class="recompensa-card card-esgotada">
            <div class="card-topo">
              <div class="icone-wrap icone-inativo">🔒</div>
              <div class="card-acoes">
                <button
                  v-if="r.ativa && r.estoque === 0"
                  class="btn-reativar"
                  title="Repor estoque"
                  @click="abrirModal(r)"
                >Repor estoque</button>
                <button
                  v-if="!r.ativa"
                  class="btn-reativar"
                  @click="reativar(r)"
                >Reativar</button>
              </div>
            </div>
            <p class="card-titulo card-titulo-inativo">{{ r.titulo }}</p>
            <div class="card-rodape">
              <span class="pts-chip pts-chip-inativo">⭐ {{ r.custo_pontos }} pts</span>
              <span class="estoque-chip estoque-vazio">
                {{ !r.ativa ? 'Desativada' : 'Sem estoque' }}
              </span>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- Modal criar/editar -->
    <div v-if="modal.aberto" class="overlay" @click.self="fecharModal">
      <div class="modal card">
        <h3 class="modal-titulo">{{ modal.editando ? 'Editar recompensa' : 'Nova recompensa' }}</h3>
        <form @submit.prevent="salvar">
          <div class="campo">
            <label>Título</label>
            <input v-model="modal.titulo" type="text" required />
          </div>
          <div class="campo">
            <label>Custo em pontos</label>
            <input v-model.number="modal.custo_pontos" type="number" min="1" required />
          </div>
          <div class="campo">
            <label>Estoque <span class="campo-hint">(deixe vazio para ilimitado)</span></label>
            <input v-model.number="modal.estoque" type="number" min="0" placeholder="Ex: 5" />
          </div>
          <div class="campo">
            <label>Descrição</label>
            <textarea v-model="modal.descricao" rows="2" />
          </div>
          <p v-if="modal.erro" class="erro-texto">{{ modal.erro }}</p>
          <div class="modal-acoes">
            <button type="button" class="btn btn-ghost" @click="fecharModal">Cancelar</button>
            <button type="submit" class="btn btn-primario" :disabled="modal.salvando">
              {{ modal.salvando ? 'Salvando…' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmação desativar -->
    <div v-if="confirm.aberto" class="overlay" @click.self="confirm.aberto = false">
      <div class="modal card">
        <h3 class="modal-titulo">Desativar recompensa?</h3>
        <p class="modal-desc">
          <strong>{{ confirm.recompensa?.titulo }}</strong> não aparecerá mais para os filhos.
        </p>
        <div class="modal-acoes">
          <button class="btn btn-ghost" @click="confirm.aberto = false">Cancelar</button>
          <button class="btn btn-perigo" @click="desativar" :disabled="confirm.carregando">
            {{ confirm.carregando ? 'Desativando…' : 'Desativar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { recompensasService } from '@/services'

const recompensas = ref([])
const carregando = ref(true)

const modal = reactive({
  aberto: false, editando: null,
  titulo: '', custo_pontos: 50, estoque: null, descricao: '',
  erro: '', salvando: false,
})

const confirm = reactive({ aberto: false, recompensa: null, carregando: false })

// Disponíveis: ativas com estoque > 0 ou ilimitado
const disponiveis = computed(() =>
  recompensas.value.filter((r) => r.ativa && (r.estoque === null || r.estoque > 0))
)

// Esgotadas: ativas com estoque=0 OU desativadas
const esgotadas = computed(() =>
  recompensas.value.filter((r) => !r.ativa || (r.ativa && r.estoque === 0))
)

function estoqueClasse(n) {
  if (n === 0) return 'estoque-vazio'
  if (n <= 3) return 'estoque-baixo'
  return 'estoque-ok'
}

function abrirModal(r = null) {
  modal.editando = r
  modal.titulo = r?.titulo || ''
  modal.custo_pontos = r?.custo_pontos || 50
  modal.estoque = r?.estoque ?? null
  modal.descricao = r?.descricao || ''
  modal.erro = ''
  modal.salvando = false
  modal.aberto = true
}

function fecharModal() { modal.aberto = false }

async function salvar() {
  modal.erro = ''
  modal.salvando = true
  try {
    const payload = {
      titulo: modal.titulo,
      custo_pontos: modal.custo_pontos,
      estoque: modal.estoque === '' ? null : modal.estoque,
      descricao: modal.descricao || null,
    }
    if (modal.editando) {
      await recompensasService.atualizar(modal.editando.id, payload)
    } else {
      await recompensasService.criar(payload)
    }
    fecharModal()
    await carregar()
  } catch (e) {
    modal.erro = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    modal.salvando = false
  }
}

function confirmarDesativar(r) {
  confirm.recompensa = r
  confirm.carregando = false
  confirm.aberto = true
}

async function desativar() {
  confirm.carregando = true
  await recompensasService.deletar(confirm.recompensa.id)
  confirm.aberto = false
  await carregar()
}

async function reativar(r) {
  await recompensasService.atualizar(r.id, { ativa: true })
  await carregar()
}

async function carregar() {
  carregando.value = true
  const resp = await recompensasService.listar({ incluir_inativas: true })
  recompensas.value = resp.data
  carregando.value = false
}

onMounted(carregar)
</script>

<style scoped>
.cabecalho { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
.titulo-pagina { font-size: 1.5rem; font-weight: 800; }

/* Seções */
.secao { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem; }
.secao-header { display: flex; align-items: center; gap: 0.6rem; }
.secao-titulo { font-size: 1rem; font-weight: 700; }
.secao-titulo-inativa { color: var(--cor-texto-suave); }

.count-badge {
  background: var(--cor-primaria); color: #fff;
  font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.5rem; border-radius: var(--raio-pill);
}
.count-badge-inativo { background: var(--cor-texto-suave); }

/* Grid */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 0.85rem; }

/* Cards */
.recompensa-card {
  background: #fff;
  border-radius: var(--raio);
  padding: 1.1rem;
  border: 1.5px solid var(--cor-borda);
  box-shadow: var(--sombra-xs);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: transform 0.15s, box-shadow 0.15s;
}

.card-disponivel:hover { transform: translateY(-2px); box-shadow: var(--sombra); border-color: #c4b5fd; }
.card-esgotada { opacity: 0.65; background: var(--cor-fundo); }

.card-topo { display: flex; align-items: center; justify-content: space-between; }

.icone-wrap {
  width: 40px; height: 40px; border-radius: 10px;
  background: var(--cor-primaria-clara); display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem;
}
.icone-inativo { background: var(--cor-fundo); }

.card-acoes { display: flex; gap: 0.35rem; align-items: center; }

.btn-icone {
  width: 30px; height: 30px; border-radius: 8px; border: none;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem; cursor: pointer; transition: background 0.12s;
}
.btn-editar { background: var(--cor-fundo); }
.btn-editar:hover { background: var(--cor-primaria-clara); }
.btn-remover { background: var(--cor-fundo); }
.btn-remover:hover { background: var(--cor-erro-bg); }

.btn-reativar {
  font-size: 0.72rem; font-weight: 600; border: 1.5px solid var(--cor-sucesso);
  background: var(--cor-sucesso-bg); color: #065f46; padding: 0.2rem 0.6rem;
  border-radius: var(--raio-pill); cursor: pointer;
}
.btn-reativar:hover { background: #a7f3d0; }

.card-titulo { font-weight: 700; font-size: 0.95rem; }
.card-titulo-inativo { color: var(--cor-texto-suave); }
.card-desc { font-size: 0.78rem; color: var(--cor-texto-suave); line-height: 1.4; }

.card-rodape { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.25rem; }

.pts-chip {
  font-size: 0.78rem; font-weight: 700;
  background: var(--cor-primaria-clara); color: var(--cor-primaria);
  padding: 0.15rem 0.55rem; border-radius: var(--raio-pill);
}
.pts-chip-inativo { background: var(--cor-fundo); color: var(--cor-texto-suave); }

.estoque-chip {
  font-size: 0.72rem; font-weight: 700;
  padding: 0.15rem 0.55rem; border-radius: var(--raio-pill);
}
.estoque-ok       { background: var(--cor-sucesso-bg); color: #065f46; }
.estoque-baixo    { background: var(--cor-aviso-bg);   color: #92400e; }
.estoque-vazio    { background: var(--cor-erro-bg);    color: #991b1b; }
.estoque-ilimitado{ background: var(--cor-info-bg);    color: #1e40af; }

.vazio { color: var(--cor-texto-suave); font-size: 0.9rem; padding: 1.5rem; text-align: center;
  background: var(--cor-fundo); border-radius: var(--raio); border: 1.5px dashed var(--cor-borda); }

/* Modal */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100; padding: 1rem;
}
.modal { width: 100%; max-width: 430px; display: flex; flex-direction: column; gap: 1.1rem; }
.modal-titulo { font-size: 1.15rem; font-weight: 700; }
.modal-desc { font-size: 0.9rem; color: var(--cor-texto-suave); }
.modal-acoes { display: flex; justify-content: flex-end; gap: 0.75rem; }

.campo-hint { font-size: 0.75rem; font-weight: 400; color: var(--cor-texto-suave); }
</style>
