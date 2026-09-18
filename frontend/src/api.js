const baseUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_HOST_REACT)
  .replace(/\/$/, '')

async function requisicao(caminho, opcoes = {}) {
  const resposta = await fetch(`${baseUrl}${caminho}`, opcoes)
  const conteudo = await resposta.json().catch(() => null)
  if (!resposta.ok) throw new Error(conteudo?.detail || `Não foi possível concluir a solicitação (${resposta.status}).`)
  return conteudo
}

export const api = {
  verificarStatus: () => requisicao('/'),
  cadastrar: ({ full_name, name, email, password }) => requisicao('/registrar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ full_name, name, email, password }) }),
  entrar: ({ username, password }) => requisicao('/login', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ username, password }) }),
  obterPerfil: (token) => requisicao('/perfil', { headers: { Authorization: `Bearer ${token}` } }),
}
