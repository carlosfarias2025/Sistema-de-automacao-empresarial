# Segurança da aplicação

Este documento descreve o comportamento de segurança implementado no backend e no frontend, além de destacar configurações importantes para implantação. Ele reflete o código atual; recomendações e limitações estão identificadas como tais.

## Autenticação e ciclo de vida do JWT

1. **Cadastro:** `POST /registrar` recebe nome, usuário, e-mail e senha. O backend cria o usuário e, em seguida, emite um token de acesso.
2. **Login:** `POST /login` recebe `username` e `password` como formulário OAuth2. O serviço busca o usuário pelo nome e compara a senha informada com o hash persistido. Em caso de sucesso, retorna `access_token` e `token_type: bearer`.
3. **Conteúdo e assinatura:** os tokens são JWT assinados com HMAC-SHA256 (`HS256`). O payload contém `sub` (nome do usuário), `role` (`user`) e `exp` (data/hora de expiração). O payload de um JWT assinado não é criptografado: não inclua nele senhas ou outros dados secretos.
4. **Duração:** a validade é de **15 minutos**, definida pelo padrão `access_token_expire_minutes=15` em `customer_service.py`. Não há configuração por variável de ambiente nem fluxo de renovação implementado.
5. **Validação e carregamento do usuário:** as rotas protegidas extraem um token `Bearer` com `OAuth2PasswordBearer`. O backend verifica assinatura, algoritmo e expiração; depois lê `sub` e busca o usuário atual no banco. Token expirado ou inválido, `sub` ausente ou usuário inexistente resulta em resposta não autorizada (401).
6. **Encerramento e revogação:** não há sessão de servidor, refresh token ou lista de revogação. O botão de sair apenas apaga o token do armazenamento do navegador. Um token copiado ainda pode ser usado até expirar; trocar a `SECRET_KEY` invalida os tokens assinados com a chave anterior.

## Senhas e dados de usuários

- As senhas são transformadas em hash com `bcrypt` antes de serem gravadas na coluna `users.password`; a autenticação usa `bcrypt.checkpw`. O código não foi observado armazenando a senha em texto puro.
- O banco de dados é PostgreSQL, acessado por SQLAlchemy. A tabela de usuários também guarda nome, nome completo, e-mail e data de criação; automações guardam usuário proprietário, nome e datas.
- O frontend envia credenciais ao backend por requisições HTTP. Em produção, publique a API e o frontend somente por HTTPS para proteger credenciais e tokens em trânsito.
- A validação de tamanho mínimo de senha (`minLength=6`) está no formulário do frontend. Ela não é uma regra equivalente aplicada pelo endpoint de cadastro, portanto clientes que chamem a API diretamente podem contorná-la.

## Armazenamento do token no frontend

O frontend guarda o JWT no `localStorage`, sob a chave `sistema-automacao:access-token`, e o envia no cabeçalho `Authorization: Bearer <token>` ao consultar perfil e automações. Ao iniciar, tenta carregar o perfil com o token salvo; se a chamada falhar, remove o token. Sair da conta também remove essa chave.

`localStorage` é acessível a JavaScript da mesma origem. Uma vulnerabilidade de cross-site scripting (XSS) pode permitir que um atacante leia e copie o token. Para aplicações expostas, considere uma estratégia de sessão com cookie `HttpOnly`, `Secure` e `SameSite` e proteção CSRF adequada; além disso, aplique prevenção contra XSS e uma política de segurança de conteúdo.

## Autorização e CORS

As rotas `/perfil`, `/automacao`, `/my_automation` e `/my_automation_delete/{id}` exigem usuário autenticado. A criação de automações associa o registro ao usuário autenticado. A remoção tenta verificar que a automação pertence a esse usuário antes de excluí-la.

**Ponto de atenção:** a consulta de propriedade em `Database/connection.py` combina condições usando o operador Python `and` dentro de `where`. Essa forma não garante que as duas condições sejam incorporadas à consulta SQL. Corrija-a para uma conjunção SQLAlchemy explícita (por exemplo, `and_(...)`) e teste que um usuário não consegue remover automações de outro antes de confiar nessa proteção.

O CORS em `main.py` lê duas origens das variáveis `API_REST_HOST_ORIGIN_LOCALHOST` e `API_REST_HOST_ORIGIN`, mas permite todas as origens configuradas, métodos e cabeçalhos com credenciais. Configure somente origens exatas e confiáveis para o ambiente; não use curingas nem valores controlados por terceiros.

## Configuração e operação seguras

- Defina `SECRET_KEY` com valor aleatório, longo e exclusivo por ambiente. Mantenha-o fora do controle de versão e dos logs; `.env` deve permanecer privado. A aplicação depende dessa chave para assinar e validar JWTs.
- Configure as credenciais de PostgreSQL (`POSTGRES_PASSWORD`) com privilégio mínimo, proteja o tráfego até o banco e restrinja o acesso de rede ao serviço.
- Use HTTPS em produção, mantenha dependências atualizadas e evite registrar senhas, tokens ou outros dados sensíveis.
- Revise também limites e validação de entrada dos endpoints antes de expor a API publicamente.

