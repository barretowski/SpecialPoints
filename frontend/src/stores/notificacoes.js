import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificacoesService } from '@/services'

export const useNotificacoesStore = defineStore('notificacoes', () => {
  const itens = ref([])
  const naoLidas = computed(() => itens.value.filter((n) => !n.lida).length)

  async function carregar() {
    const resp = await notificacoesService.listar()
    itens.value = resp.data
  }

  async function marcarLida(id) {
    await notificacoesService.marcarLida(id)
    const item = itens.value.find((n) => n.id === id)
    if (item) item.lida = true
  }

  async function marcarTodasLidas() {
    await notificacoesService.marcarTodasLidas()
    itens.value.forEach((n) => (n.lida = true))
  }

  return { itens, naoLidas, carregar, marcarLida, marcarTodasLidas }
})
