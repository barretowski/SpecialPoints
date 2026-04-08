<template>
  <div>
    <section class="pontos-section card" aria-label="Seus pontos">
      <img src="@/assets/logo.png" alt="Personagem SpecialPoints" class="personagem" />
      <h2 class="pontos-titulo">Seus pontos</h2>
      <p class="pontos-valor" aria-live="polite">⭐ {{ auth.usuario?.pontos_disponiveis || 0 }}</p>
      <p class="pontos-sub">{{ auth.usuario?.pontos_acumulados || 0 }} pontos acumulados no total</p>
    </section>

    <section class="secao" aria-labelledby="tarefas-titulo">
      <h3 id="tarefas-titulo">Tarefas para fazer</h3>
      <div v-if="carregando" class="carregando">Carregando…</div>
      <div v-else class="lista">
        <div v-if="!pendentes.length" class="vazio">Nenhuma tarefa pendente. 🎉</div>
        <div v-for="t in pendentes" :key="t.id" class="card tarefa-card">
          <div class="tarefa-info">
            <p class="tarefa-titulo">{{ t.titulo }}</p>
            <p v-if="t.descricao" class="tarefa-desc">{{ t.descricao }}</p>
          </div>
          <div class="tarefa-direita">
            <p class="tarefa-pts">⭐ {{ t.pontos }}</p>
            <button class="btn btn-primario btn-sm" @click="concluir(t.id)" :aria-label="`Marcar ${t.titulo} como concluída`">
              Concluir
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="secao" aria-labelledby="notif-titulo">
      <h3 id="notif-titulo">Notificações recentes</h3>
      <div class="lista">
        <div v-if="!notificacoes.itens.length" class="vazio">Sem notificações.</div>
        <div
          v-for="n in notificacoes.itens.slice(0, 5)"
          :key="n.id"
          class="card notif-card"
          :class="{ nao_lida: !n.lida }"
          @click="notificacoes.marcarLida(n.id)"
          role="button"
          :aria-label="n.titulo"
          tabindex="0"
        >
          <p class="notif-titulo">{{ n.titulo }}</p>
          <p class="notif-msg">{{ n.mensagem }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { tarefasService } from '@/services'
import { useAuthStore } from '@/stores/auth'
import { useNotificacoesStore } from '@/stores/notificacoes'

const auth = useAuthStore()
const notificacoes = useNotificacoesStore()

const tarefas = ref([])
const carregando = ref(true)

const pendentes = computed(() => tarefas.value.filter((t) => t.status === 'pendente'))

async function carregar() {
  const resp = await tarefasService.listar({ tamanho: 50 })
  tarefas.value = resp.data
  carregando.value = false
}

async function concluir(id) {
  await tarefasService.concluir(id)
  await auth.carregarPerfil()
  await carregar()
}

onMounted(async () => {
  await Promise.all([carregar(), notificacoes.carregar()])
})
</script>

<style scoped>
.pontos-section {
  text-align: center;
  margin-bottom: 1.5rem;
  padding: 2rem 2rem 1.5rem;
}
.personagem {
  width: 120px;
  height: 120px;
  object-fit: contain;
  margin-bottom: 0.75rem;
  filter: drop-shadow(0 6px 16px rgba(108, 99, 255, 0.3));
  animation: flutua 3s ease-in-out infinite;
}
@keyframes flutua {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-8px); }
}
.pontos-titulo { font-size: 1.1rem; color: var(--cor-texto-suave); margin-bottom: 0.5rem; }
.pontos-valor { font-size: 3rem; font-weight: 700; color: var(--cor-primaria); }
.pontos-sub { font-size: 0.85rem; color: var(--cor-texto-suave); margin-top: 0.25rem; }

.secao { margin-bottom: 1.5rem; }
.secao h3 { margin-bottom: 0.75rem; font-size: 1.1rem; }

.lista { display: flex; flex-direction: column; gap: 0.75rem; }

.tarefa-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.tarefa-info { flex: 1; }
.tarefa-titulo { font-weight: 600; font-size: 1rem; }
.tarefa-desc { font-size: 0.85rem; color: var(--cor-texto-suave); margin-top: 2px; }
.tarefa-direita { display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; flex-shrink: 0; }
.tarefa-pts { font-weight: 700; color: var(--cor-primaria); font-size: 1.1rem; }
.btn-sm { padding: 0.4rem 0.9rem; font-size: 0.88rem; }

.notif-card {
  cursor: pointer;
  transition: background 0.15s;
}
.notif-card.nao_lida { background: #f0eeff; }
.notif-titulo { font-weight: 600; font-size: 0.9rem; }
.notif-msg { font-size: 0.82rem; color: var(--cor-texto-suave); margin-top: 2px; }

.vazio { text-align: center; color: var(--cor-texto-suave); padding: 1.5rem; }
</style>
