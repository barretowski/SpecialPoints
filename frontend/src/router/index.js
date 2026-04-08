import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { publica: true },
  },
  {
    path: '/registro',
    name: 'registro',
    component: () => import('@/views/RegistroView.vue'),
    meta: { publica: true },
  },

  // Responsável
  {
    path: '/responsavel',
    component: () => import('@/views/responsavel/LayoutResponsavel.vue'),
    meta: { papel: 'responsavel' },
    children: [
      { path: '', redirect: '/responsavel/dashboard' },
      { path: 'dashboard', name: 'responsavel-dashboard', component: () => import('@/views/responsavel/DashboardView.vue') },
      { path: 'tarefas', name: 'responsavel-tarefas', component: () => import('@/views/responsavel/TarefasView.vue') },
      { path: 'recompensas', name: 'responsavel-recompensas', component: () => import('@/views/responsavel/RecompensasView.vue') },
      { path: 'membros', name: 'responsavel-membros', component: () => import('@/views/responsavel/MembrosView.vue') },
    ],
  },

  // Filho
  {
    path: '/filho',
    component: () => import('@/views/filho/LayoutFilho.vue'),
    meta: { papel: 'filho' },
    children: [
      { path: '', redirect: '/filho/dashboard' },
      { path: 'dashboard', name: 'filho-dashboard', component: () => import('@/views/filho/DashboardView.vue') },
      { path: 'tarefas', name: 'filho-tarefas', component: () => import('@/views/filho/TarefasView.vue') },
      { path: 'recompensas', name: 'filho-recompensas', component: () => import('@/views/filho/RecompensasView.vue') },
    ],
  },

  // Admin
  {
    path: '/admin',
    component: () => import('@/views/admin/LayoutAdmin.vue'),
    meta: { papel: 'admin' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardAdmin.vue') },
      { path: 'grupos', name: 'admin-grupos', component: () => import('@/views/admin/GruposView.vue') },
      { path: 'grupos/:id', name: 'admin-grupo-detalhe', component: () => import('@/views/admin/GrupoDetalheView.vue') },
    ],
  },

  { path: '/', redirect: () => '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  // Não autenticado tentando acessar rota protegida
  if (!to.meta.publica && !auth.autenticado) return '/login'

  // Autenticado tentando acessar login/registro → redireciona para home
  if (to.meta.publica && auth.autenticado) {
    if (auth.ehAdmin) return '/admin/dashboard'
    return auth.ehResponsavel ? '/responsavel/dashboard' : '/filho/dashboard'
  }

  // Admin só acessa rotas admin (ou qualquer rota sem papel definido)
  if (auth.ehAdmin) {
    if (to.meta.papel && to.meta.papel !== 'admin') return '/admin/dashboard'
    return
  }

  // Verifica papel necessário para a rota
  if (to.meta.papel && auth.usuario?.papel !== to.meta.papel) {
    return auth.ehResponsavel ? '/responsavel/dashboard' : '/filho/dashboard'
  }
})

export default router
