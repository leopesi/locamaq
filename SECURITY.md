# Security Policy

## Reportando Vulnerabilidades

Se você encontrar uma vulnerabilidade de segurança, **NÃO** abra uma issue pública.

Envie um e-mail para o mantenedor com:

- Descrição da vulnerabilidade
- Passos para reproduzir
- Impacto potencial
- Sugestão de correção (se possível)

## Práticas de Segurança

- Nunca commitar `.env` ou credenciais
- Usar `SECRET_KEY` forte em produção (50+ caracteres aleatórios)
- Manter `DEBUG=False` em produção
- Configurar `ALLOWED_HOSTS` corretamente
- Usar HTTPS em produção
- Manter dependências atualizadas
