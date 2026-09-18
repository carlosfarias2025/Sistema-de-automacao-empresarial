import { useEffect, useState } from 'react'
import { api } from './api'
import './App.css'

const TOKEN_KEY = 'sistema-automacao:access-token'

function App() {
  const [modo, setModo] = useState('login')
  const [apiOnline, setApiOnline] = useState(null)
  const [perfil, setPerfil] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [mensagem, setMensagem] = useState(null)

  async function carregarPerfil(token) { setPerfil(await api.obterPerfil(token)) }

  useEffect(() => {
    async function iniciar() {
      try { await api.verificarStatus(); setApiOnline(true) } catch { setApiOnline(false) }
      const token = localStorage.getItem(TOKEN_KEY)
      if (!token) return
      try { await carregarPerfil(token) } catch { localStorage.removeItem(TOKEN_KEY) }
    }
    iniciar()
  }, [])

  async function enviarLogin(event) {
    event.preventDefault()
    const formulario = new FormData(event.currentTarget)
    setCarregando(true); setMensagem(null)
    try {
      const resposta = await api.entrar({ username: formulario.get('username'), password: formulario.get('password') })
      localStorage.setItem(TOKEN_KEY, resposta.access_token)
      await carregarPerfil(resposta.access_token)
    } catch (erro) { setMensagem({ tipo: 'erro', texto: erro.message }) } finally { setCarregando(false) }
  }

  async function enviarCadastro(event) {
    event.preventDefault()
    const formulario = new FormData(event.currentTarget)
    setCarregando(true); setMensagem(null)
    try {
      const resposta = await api.cadastrar({ full_name: formulario.get('full_name'), name: formulario.get('name'), email: formulario.get('email'), password: formulario.get('password') })
      localStorage.setItem(TOKEN_KEY, resposta.access_token)
      await carregarPerfil(resposta.access_token)
    } catch (erro) { setMensagem({ tipo: 'erro', texto: erro.message }) } finally { setCarregando(false) }
  }

  function sair() { localStorage.removeItem(TOKEN_KEY); setPerfil(null); setMensagem(null); setModo('login') }

  if (perfil) return <main className="pagina"><section className="painel painel-perfil">
    <span className="marca">Sistema de automação</span><div className="avatar" aria-hidden="true">{perfil.username.slice(0, 1).toUpperCase()}</div>
    <p className="sobretitulo">Sessão ativa</p><h1>Olá, {perfil.full_name || perfil.username}.</h1><p className="descricao">Você está conectado e sua área protegida está disponível.</p>
    <dl className="dados-perfil"><div><dt>Usuário</dt><dd>{perfil.username}</dd></div><div><dt>Permissão</dt><dd>{perfil.role}</dd></div></dl>
    <button className="botao botao-secundario" onClick={sair}>Sair da conta</button>
  </section></main>

  return <main className="pagina"><section className="painel">
    <span className="marca">Sistema de automação</span><p className="sobretitulo">Acesso à plataforma</p><h1>{modo === 'login' ? 'Entre na sua conta' : 'Crie sua conta'}</h1>
    <p className="descricao">{modo === 'login' ? 'Use suas credenciais para continuar.' : 'Preencha seus dados para começar.'}</p>
    {apiOnline !== null && <p className={`status-api ${apiOnline ? 'online' : 'offline'}`}><span /> {apiOnline ? 'API conectada' : 'Não foi possível conectar à API'}</p>}
    <div className="abas" role="tablist" aria-label="Acesso"><button className={modo === 'login' ? 'ativa' : ''} onClick={() => { setModo('login'); setMensagem(null) }}>Entrar</button><button className={modo === 'cadastro' ? 'ativa' : ''} onClick={() => { setModo('cadastro'); setMensagem(null) }}>Cadastrar</button></div>
    {mensagem && <p className={`mensagem ${mensagem.tipo}`}>{mensagem.texto}</p>}
    {modo === 'login' ? <form onSubmit={enviarLogin} className="formulario"><label>Usuário<input name="username" autoComplete="username" required /></label><label>Senha<input name="password" type="password" autoComplete="current-password" required /></label><button className="botao" disabled={carregando}>{carregando ? 'Entrando...' : 'Entrar'}</button></form> : <form onSubmit={enviarCadastro} className="formulario"><label>Nome completo<input name="full_name" autoComplete="name" required /></label><label>Usuário<input name="name" autoComplete="username" required /></label><label>E-mail<input name="email" type="email" autoComplete="email" required /></label><label>Senha<input name="password" type="password" autoComplete="new-password" minLength="6" required /></label><button className="botao" disabled={carregando}>{carregando ? 'Criando conta...' : 'Criar conta'}</button></form>}
  </section></main>
}

export default App
