# Contribuindo com o LocaMaq

Obrigado pelo interesse em contribuir! 🎉

## Como Contribuir

1. Faça um fork do repositório
2. Crie uma branch para sua feature: `git checkout -b feature/minha-feature`
3. Faça commit das mudanças: `git commit -m "feat: descrição da feature"`
4. Push para a branch: `git push origin feature/minha-feature`
5. Abra um Pull Request

## Convenção de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — Nova funcionalidade
- `fix:` — Correção de bug
- `docs:` — Documentação
- `style:` — Formatação (sem alteração de lógica)
- `refactor:` — Refatoração de código
- `test:` — Testes
- `chore:` — Tarefas de manutenção

## Setup de Desenvolvimento

```bash
git clone https://github.com/leopesi/locamaq.git
cd locamaq
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Padrões de Código

- Python: PEP 8
- Django: seguir convenções do framework
- Templates: Tailwind CSS utility classes
- Princípios SOLID
- Toda view com `@login_required`
- Toda query filtrada por `tenant`

## Reportando Bugs

Abra uma [issue](https://github.com/leopesi/locamaq/issues) com:

- Descrição do problema
- Passos para reproduzir
- Comportamento esperado vs. atual
- Screenshots (se aplicável)
