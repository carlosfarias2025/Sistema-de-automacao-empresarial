import { useState, useEffect } from 'react';

function App() {
  const [respostaApi, setRespostaApi] = useState(null);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState(null);


  const API_URL = 'http://127.0.0.1:8000/';

  useEffect(() => {
    async function checarStatus() {
      try {
        setLoading(true);
        const resposta = await fetch(API_URL);

        if (!resposta.ok) {
          throw new Error(`Erro na requisição: ${resposta.status}`);
        }

        const dados = await resposta.json();
        // Armazena o JSON recebido, ex: {"status": "ok"}
        setRespostaApi(dados);
      } catch (err) {
        setErro(err.message);
      } finally {
        setLoading(false);
      }
    }

    checarStatus();
  }, []);

  return (
      <div style={{padding: '20px', fontFamily: 'sans-serif'}}>
            <h1>Status da API</h1>

            {loading && <p>Verificando conexão com a API...</p>}

            {erro && (
                <p style={{color: 'red'}}>
                    <strong>Falha ao conectar</strong> {erro}
                </p>
            )}

            {respostaApi && (
                <div>
                    <p>
                        <strong>Status recebido:</strong> {respostaApi.status}
                    </p>
                    <p
                        style={{
                            color: respostaApi.status === 'ok' ? 'green' : 'orange',
                            fontWeight: 'bold'
                        }}
                    >
                        {respostaApi.status === 'ok'
                            ? '✅ API está funcionando perfeitamente!'
                            : '⚠️ A API respondeu, mas o status não é OK.'}
                    </p>
                </div>
            )}
        </div>
    );
}

export default App;