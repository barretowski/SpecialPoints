<template>
  <main class="login-page">
    <div class="card login-card">
      <div class="logo-wrap">
        <img src="@/assets/logo.png" alt="Personagem SpecialPoints" class="logo-img" />
      </div>
      <h1 class="titulo">SpecialPoints</h1>
      <p class="subtitulo">Entre na sua conta</p>

      <form @submit.prevent="entrar" novalidate>
        <div class="campo">
          <label for="email">E-mail</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            placeholder="seu@email.com"
            required
          />
        </div>

        <div class="campo">
          <label for="senha">Senha</label>
          <input
            id="senha"
            v-model="form.senha"
            type="password"
            autocomplete="current-password"
            placeholder="••••••"
            required
          />
        </div>

        <p v-if="erro" class="erro-texto" role="alert">{{ erro }}</p>

        <button type="submit" class="btn btn-primario btn-bloco" :disabled="carregando">
          {{ carregando ? 'Entrando…' : 'Entrar' }}
        </button>
      </form>

      <p class="rodape-form">
        Não tem conta?
        <RouterLink to="/registro">Cadastre-se</RouterLink>
      </p>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', senha: '' })
const erro = ref('')
const carregando = ref(false)

async function entrar() {
  erro.value = ''
  carregando.value = true
  try {
    await auth.login(form.email, form.senha)
    router.push(auth.ehResponsavel ? '/responsavel/dashboard' : '/filho/dashboard')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao entrar. Verifique seus dados.'
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.logo-wrap {
  display: flex;
  justify-content: center;
}

.logo-img {
  width: 110px;
  height: 110px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(108, 99, 255, 0.25));
}

.titulo {
  font-size: 1.75rem;
  text-align: center;
  color: var(--cor-primaria);
  margin-top: -0.25rem;
}

.subtitulo {
  text-align: center;
  color: var(--cor-texto-suave);
  margin-top: -0.75rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-bloco {
  width: 100%;
  justify-content: center;
  padding: 0.75rem;
  font-size: 1rem;
}

.rodape-form {
  text-align: center;
  font-size: 0.9rem;
  color: var(--cor-texto-suave);
}
</style>
