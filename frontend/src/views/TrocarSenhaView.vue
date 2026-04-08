<template>
  <main class="pagina-troca">
    <div class="card troca-card">
      <div class="logo-wrap">
        <img src="@/assets/logo.png" alt="SpecialPoints" class="logo-img" />
      </div>
      <h1 class="titulo">Crie sua senha</h1>
      <p class="subtitulo">
        Por segurança, defina uma senha pessoal antes de continuar.
      </p>

      <form @submit.prevent="trocar" novalidate>
        <div class="campo">
          <label for="senha-atual">Senha fornecida pelo administrador</label>
          <input
            id="senha-atual"
            v-model="form.senhaAtual"
            type="password"
            placeholder="Senha temporária"
            required
            autocomplete="current-password"
          />
        </div>

        <div class="campo">
          <label for="nova-senha">Nova senha</label>
          <input
            id="nova-senha"
            v-model="form.novaSenha"
            type="password"
            placeholder="Mínimo 6 caracteres"
            required
            minlength="6"
            autocomplete="new-password"
          />
        </div>

        <div class="campo">
          <label for="confirmar-senha">Confirmar nova senha</label>
          <input
            id="confirmar-senha"
            v-model="form.confirmar"
            type="password"
            placeholder="Repita a nova senha"
            required
            autocomplete="new-password"
          />
        </div>

        <p v-if="erro" class="erro-texto" role="alert">{{ erro }}</p>

        <button type="submit" class="btn btn-primario btn-bloco" :disabled="carregando">
          {{ carregando ? 'Salvando…' : 'Definir senha e entrar' }}
        </button>
      </form>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usuariosService } from '@/services'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ senhaAtual: '', novaSenha: '', confirmar: '' })
const erro = ref('')
const carregando = ref(false)

async function trocar() {
  erro.value = ''

  if (form.novaSenha !== form.confirmar) {
    erro.value = 'As senhas não coincidem.'
    return
  }

  carregando.value = true
  try {
    const resp = await usuariosService.trocarSenha({
      senha_atual: form.senhaAtual,
      nova_senha: form.novaSenha,
    })
    // Atualiza o perfil local com deve_trocar_senha = false
    auth.usuario = resp.data
    localStorage.setItem('usuario', JSON.stringify(resp.data))

    // Redireciona para o destino correto
    if (auth.ehAdmin) router.push('/admin/dashboard')
    else if (auth.ehResponsavel) router.push('/responsavel/dashboard')
    else router.push('/filho/dashboard')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao trocar senha.'
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.pagina-troca {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.troca-card {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.logo-wrap { display: flex; justify-content: center; }
.logo-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(108, 99, 255, 0.25));
}

.titulo {
  font-size: 1.5rem;
  text-align: center;
  color: var(--cor-primaria);
  margin-top: -0.25rem;
}

.subtitulo {
  text-align: center;
  color: var(--cor-texto-suave);
  font-size: 0.9rem;
  margin-top: -0.75rem;
  line-height: 1.5;
}

form { display: flex; flex-direction: column; gap: 1rem; }

.btn-bloco {
  width: 100%;
  justify-content: center;
  padding: 0.75rem;
  font-size: 1rem;
}
</style>
