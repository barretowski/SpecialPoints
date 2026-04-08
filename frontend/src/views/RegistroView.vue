<template>
  <main class="login-page">
    <div class="card login-card">
      <div class="logo-wrap">
        <img src="@/assets/logo.png" alt="Personagem SpecialPoints" class="logo-img" />
      </div>
      <h1 class="titulo">SpecialPoints</h1>
      <p class="subtitulo">Crie sua conta</p>

      <form @submit.prevent="cadastrar" novalidate>
        <div class="campo">
          <label for="nome">Nome</label>
          <input id="nome" v-model="form.nome" type="text" placeholder="Seu nome" required />
        </div>

        <div class="campo">
          <label for="email">E-mail</label>
          <input id="email" v-model="form.email" type="email" placeholder="seu@email.com" required />
        </div>

        <div class="campo">
          <label for="senha">Senha</label>
          <input id="senha" v-model="form.senha" type="password" placeholder="mínimo 6 caracteres" required />
        </div>

        <div class="campo">
          <label for="papel">Você é</label>
          <select id="papel" v-model="form.papel">
            <option value="responsavel">Responsável (pai/mãe)</option>
            <option value="filho">Filho(a)</option>
          </select>
        </div>

        <div v-if="form.papel === 'responsavel'" class="campo">
          <label for="familia_nome">Nome da família</label>
          <input id="familia_nome" v-model="form.familia_nome" type="text" placeholder="Ex: Família Silva" />
        </div>

        <div v-if="form.papel === 'filho'" class="campo">
          <label for="familia_codigo">Código de convite da família</label>
          <input id="familia_codigo" v-model="form.familia_codigo" type="text" placeholder="Código fornecido pelo responsável" />
        </div>

        <p v-if="erro" class="erro-texto" role="alert">{{ erro }}</p>

        <button type="submit" class="btn btn-primario btn-bloco" :disabled="carregando">
          {{ carregando ? 'Cadastrando…' : 'Cadastrar' }}
        </button>
      </form>

      <p class="rodape-form">
        Já tem conta? <RouterLink to="/login">Entrar</RouterLink>
      </p>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services'

const router = useRouter()

const form = reactive({
  nome: '',
  email: '',
  senha: '',
  papel: 'responsavel',
  familia_nome: '',
  familia_codigo: '',
})
const erro = ref('')
const carregando = ref(false)

async function cadastrar() {
  erro.value = ''
  carregando.value = true
  try {
    await authService.registro({
      nome: form.nome,
      email: form.email,
      senha: form.senha,
      papel: form.papel,
      familia_nome: form.papel === 'responsavel' ? form.familia_nome || null : null,
      familia_codigo: form.papel === 'filho' ? form.familia_codigo || null : null,
    })
    router.push('/login')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao cadastrar.'
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
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.logo-wrap { display: flex; justify-content: center; }
.logo-img { width: 90px; height: 90px; object-fit: contain; filter: drop-shadow(0 4px 12px rgba(108, 99, 255, 0.25)); }
.titulo { font-size: 1.75rem; text-align: center; color: var(--cor-primaria); margin-top: -0.25rem; }
.subtitulo { text-align: center; color: var(--cor-texto-suave); margin-top: -0.75rem; }
form { display: flex; flex-direction: column; gap: 1rem; }
.btn-bloco { width: 100%; justify-content: center; padding: 0.75rem; font-size: 1rem; }
.rodape-form { text-align: center; font-size: 0.9rem; color: var(--cor-texto-suave); }
</style>
