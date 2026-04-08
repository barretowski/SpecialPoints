import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services'

export const useAuthStore = defineStore('auth', () => {
  const usuario = ref(JSON.parse(localStorage.getItem('usuario') || 'null'))
  const token = ref(localStorage.getItem('access_token') || null)

  const autenticado = computed(() => !!token.value)
  const ehAdmin = computed(() => usuario.value?.papel === 'admin')
  const ehResponsavel = computed(() => ['admin', 'responsavel'].includes(usuario.value?.papel))
  const ehFilho = computed(() => usuario.value?.papel === 'filho')

  async function login(email, senha) {
    const resp = await authService.login(email, senha)
    token.value = resp.data.access_token
    localStorage.setItem('access_token', resp.data.access_token)
    localStorage.setItem('refresh_token', resp.data.refresh_token)
    await carregarPerfil()
  }

  async function carregarPerfil() {
    const resp = await authService.me()
    usuario.value = resp.data
    localStorage.setItem('usuario', JSON.stringify(resp.data))
  }

  function logout() {
    token.value = null
    usuario.value = null
    localStorage.clear()
  }

  return { usuario, token, autenticado, ehAdmin, ehResponsavel, ehFilho, login, logout, carregarPerfil }
})
