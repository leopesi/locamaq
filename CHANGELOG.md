# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] — 2026-08-05

### Adicionado

- Sistema multi-tenant com isolamento completo por empresa
- CRUD de clientes (PF/PJ) com campos completos (endereço, referências, limite de crédito)
- Gestão de equipamentos com patrimônio individual, estados e histórico
- Sistema de locações com formulário único, cálculo automático e formas de pagamento
- Fluxo de caixa básico (entradas/saídas com filtro por período)
- Geração de comprovante PDF com cláusulas legais
- Integração WhatsApp via Evolution API (envio manual de comprovantes e mensagens)
- Canal de promoções (broadcast para clientes)
- Motor de alertas automáticos (atraso, pagamento pendente, estoque baixo)
- Dashboard com mapa interativo (Leaflet.js + OpenStreetMap)
- Ícones SVG customizados por tipo de equipamento no mapa
- Geocodificação automática de endereços (Nominatim)
- Layout responsivo (mobile + desktop)
- Sistema de logs (auditoria, erros, segurança, integrações)
- Tratamento de erros com páginas customizadas (403, 404, 500)
- Painel de configurações (empresa, cláusulas, WhatsApp)
- Docker + Nginx + Gunicorn para produção
- Documentação completa
