<template>
  <div class="wrapper">
    <button class="btn-notif" @click="aberto = !aberto" :aria-label="`Notificações (${store.naoLidas} não lidas)`">
      🔔
      <span v-if="store.naoLidas > 0" class="badge-count">{{ store.naoLidas }}</span>
    </button>

    <div v-if="aberto" class="painel" role="dialog" aria-label="Notificações">
      <div class="painel-header">
        <strong>Notificações</strong>
        <button v-if="store.naoLidas > 0" class="btn-todas" @click="store.marcarTodasLidas()">
          Marcar todas como lidas
        </button>
      </div>

      <ul v-if="store.itens.length" class="lista">
        <li
          v-for="n in store.itens.slice(0, 10)"
          :key="n.id"
          class="item"
          :class="{ nao_lida: !n.lida }"
          @click="store.marcarLida(n.id)"
        >
          <p class="item-titulo">{{ n.titulo }}</p>
          <p class="item-msg">{{ n.mensagem }}</p>
        </li>
      </ul>
      <p v-else class="vazio">Nenhuma notificação.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useNotificacoesStore } from '@/stores/notificacoes'

const store = useNotificacoesStore()
const aberto = ref(false)
</script>

<style scoped>
.wrapper { position: relative; }

.btn-notif {
  background: none;
  border: none;
  font-size: 1.4rem;
  position: relative;
  line-height: 1;
}

.badge-count {
  position: absolute;
  top: -4px; right: -6px;
  background: var(--cor-erro);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 999px;
  padding: 1px 5px;
}

.painel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: var(--cor-superficie);
  border-radius: var(--raio);
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  z-index: 100;
  overflow: hidden;
}

.painel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--cor-borda);
}

.btn-todas {
  font-size: 0.78rem;
  background: none;
  border: none;
  color: var(--cor-primaria);
}

.lista { list-style: none; max-height: 360px; overflow-y: auto; }

.item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--cor-borda);
  cursor: pointer;
  transition: background 0.15s;
}
.item:hover { background: var(--cor-fundo); }
.item.nao_lida { background: #f0eeff; }

.item-titulo { font-weight: 600; font-size: 0.9rem; }
.item-msg { font-size: 0.82rem; color: var(--cor-texto-suave); margin-top: 2px; }

.vazio { padding: 1rem; text-align: center; color: var(--cor-texto-suave); font-size: 0.9rem; }
</style>
