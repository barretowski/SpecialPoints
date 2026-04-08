<template>
  <div>
    <h2 class="titulo-pagina">Membros da família</h2>

    <div v-if="auth.usuario?.familia_id" class="card codigo-card">
      <p>Código de convite da família:</p>
      <strong class="codigo">{{ codigoConvite || '—' }}</strong>
      <p class="codigo-hint">Compartilhe este código para que outros membros entrem na família.</p>
    </div>

    <div v-if="carregando" class="carregando">Carregando…</div>
    <div v-else class="membros-lista">
      <div v-for="m in membros" :key="m.id" class="card membro-card">
        <div class="membro-avatar">{{ m.nome[0].toUpperCase() }}</div>
        <div class="membro-dados">
          <p class="membro-nome">{{ m.nome }}</p>
          <p class="membro-email">{{ m.email }}</p>
          <span class="badge" :class="m.papel === 'responsavel' ? 'badge-info' : 'badge-sucesso'">
            {{ m.papel === 'responsavel' ? 'Responsável' : 'Filho(a)' }}
          </span>
        </div>
        <div class="membro-pontos">
          <p class="pts-valor">⭐ {{ m.pontos_disponiveis }}</p>
          <p class="pts-label">disponíveis</p>
          <p class="pts-acumulado">{{ m.pontos_acumulados }} acumulados</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usuariosService } from '@/services'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const membros = ref([])
const carregando = ref(true)
const codigoConvite = ref('')

onMounted(async () => {
  const resp = await usuariosService.familia()
  membros.value = resp.data
  carregando.value = false
})
</script>

<style scoped>
.titulo-pagina { font-size: 1.5rem; margin-bottom: 1.25rem; }

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
</style>
