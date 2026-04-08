import api from './api'

// Auth
export const authService = {
  login: (email, senha) => api.post('/auth/login', { email, senha }),
  registro: (dados) => api.post('/auth/registro', dados),
  me: () => api.get('/auth/me'),
  refresh: (refresh_token) => api.post('/auth/refresh', null, { params: { refresh_token } }),
}

// Usuários
export const usuariosService = {
  familia: () => api.get('/usuarios/familia'),
  atualizar: (dados) => api.patch('/usuarios/me', dados),
  trocarSenha: (dados) => api.patch('/usuarios/me/senha', dados),
  criarMembro: (dados) => api.post('/usuarios/familia/membros', dados),
}

// Tarefas
export const tarefasService = {
  listar: (params) => api.get('/tarefas/', { params }),
  obter: (id) => api.get(`/tarefas/${id}`),
  criar: (dados) => api.post('/tarefas/', dados),
  atualizar: (id, dados) => api.patch(`/tarefas/${id}`, dados),
  deletar: (id) => api.delete(`/tarefas/${id}`),
  concluir: (id) => api.post(`/tarefas/${id}/concluir`),
  aprovar: (id) => api.post(`/tarefas/${id}/aprovar`),
  rejeitar: (id, observacao) => api.post(`/tarefas/${id}/rejeitar`, { observacao }),
}

// Recompensas
export const recompensasService = {
  listar: (params) => api.get('/recompensas/', { params }),
  obter: (id) => api.get(`/recompensas/${id}`),
  criar: (dados) => api.post('/recompensas/', dados),
  atualizar: (id, dados) => api.patch(`/recompensas/${id}`, dados),
  deletar: (id) => api.delete(`/recompensas/${id}`),
}

// Metas
export const metasService = {
  listar: () => api.get('/metas/'),
  criar: (dados) => api.post('/metas/', dados),
  atualizar: (id, dados) => api.patch(`/metas/${id}`, dados),
  cancelar: (id) => api.delete(`/metas/${id}`),
}

// Resgates
export const resgatesService = {
  listar: (params) => api.get('/resgates/', { params }),
  solicitar: (recompensa_id) => api.post('/resgates/', { recompensa_id }),
  avaliar: (id, status, observacao) => api.patch(`/resgates/${id}`, { status, observacao }),
}

// Transações
export const transacoesService = {
  listar: (params) => api.get('/transacoes/', { params }),
  bonus: (dados) => api.post('/transacoes/bonus', dados),
}

// Notificações
export const notificacoesService = {
  listar: (apenas_nao_lidas = false) => api.get('/notificacoes/', { params: { apenas_nao_lidas } }),
  marcarLida: (id) => api.patch(`/notificacoes/${id}/lida`),
  marcarTodasLidas: () => api.post('/notificacoes/marcar-todas-lidas'),
}

// Categorias
export const categoriasService = {
  listar: () => api.get('/categorias/'),
  criar: (dados) => api.post('/categorias/', dados),
  atualizar: (id, dados) => api.patch(`/categorias/${id}`, dados),
  deletar: (id) => api.delete(`/categorias/${id}`),
}

// Admin
export const adminService = {
  stats: () => api.get('/admin/stats'),
  listarGrupos: (params) => api.get('/admin/familias', { params }),
  criarGrupo: (dados) => api.post('/admin/familias', dados),
  obterGrupo: (id) => api.get(`/admin/familias/${id}`),
  atualizarGrupo: (id, dados) => api.patch(`/admin/familias/${id}`, dados),
  deletarGrupo: (id) => api.delete(`/admin/familias/${id}`),
  membrosGrupo: (id) => api.get(`/admin/familias/${id}/membros`),
  criarMembro: (familiaId, dados) => api.post(`/admin/familias/${familiaId}/membros`, dados),
  listarUsuarios: (params) => api.get('/admin/usuarios', { params }),
  ativarUsuario: (id, ativo) => api.patch(`/admin/usuarios/${id}/ativar`, null, { params: { ativo } }),
}
