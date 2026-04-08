<template>
  <main class="login-page">
    <div class="login-card">
      <div class="logo-wrap">
        <img src="@/assets/logo.png" alt="SpecialPoints" class="logo-img" />
      </div>
      <h1 class="titulo">SpecialPoints</h1>
      <p class="subtitulo">Entre na sua conta</p>

      <form @submit.prevent="entrar" novalidate class="form">
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
        Não tem conta? <RouterLink to="/registro">Cadastre-se</RouterLink>
      </p>
    </div>

    <div class="bg-deco" aria-hidden="true">
      <div class="deco-circle deco-1"></div>
      <div class="deco-circle deco-2"></div>
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
    router.push(auth.ehAdmin ? '/admin/dashboard' : auth.ehResponsavel ? '/responsavel/dashboard' : '/filho/dashboard')
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
  padding: 1.5rem;
  background: var(--grad-filho);
  position: relative;
  overflow: hidden;
}

.login-card {
  background: #fff;
  border-radius: var(--raio-grande);
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: var(--sombra-lg);
  position: relative;
  z-index: 1;
}

.logo-wrap { display: flex; justify-content: center; margin-bottom: 0.25rem; }
.logo-img {
  width: 90px;
  height: 90px;
  object-fit: contain;
  filter: drop-shadow(0 6px 16px rgba(124,58,237,0.3));
  animation: flutua 3s ease-in-out infinite;
}

@keyframes flutua {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-6px); }
}

.titulo {
  font-size: 1.75rem;
  font-weight: 800;
  text-align: center;
  color: var(--cor-primaria);
  margin-top: -0.25rem;
}

.subtitulo {
  text-align: center;
  color: var(--cor-texto-suave);
  font-size: 0.9rem;
  margin-top: -0.25rem;
  margin-bottom: 0.5rem;
}

.form { display: flex; flex-direction: column; gap: 1rem; margin-top: 0.25rem; }

.btn-bloco {
  width: 100%;
  padding: 0.8rem;
  font-size: 1rem;
  margin-top: 0.25rem;
}

.rodape-form {
  text-align: center;
  font-size: 0.88rem;
  color: var(--cor-texto-suave);
  margin-top: 0.25rem;
}

/* Decoração de fundo */
.bg-deco { position: absolute; inset: 0; pointer-events: none; }
.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
}
.deco-1 { width: 400px; height: 400px; top: -150px; right: -100px; }
.deco-2 { width: 300px; height: 300px; bottom: -100px; left: -80px; }
</style>
