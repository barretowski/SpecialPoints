# SpecialPoints — Manual do Usuário

> Sistema de pontos e recompensas para famílias

---

## O que é o SpecialPoints?

O SpecialPoints é uma plataforma digital que transforma a rotina das crianças em um jogo de conquistas. Os pais criam tarefas, os filhos completam e ganham pontos, e trocam esses pontos por recompensas escolhidas pela própria família.

Simples para os pais. Divertido para os filhos. Efetivo para todos.

---

## Para quem é?

- **Famílias** que querem engajar os filhos em responsabilidades do dia a dia
- **Pais** que buscam uma forma estruturada de recompensar bons hábitos
- **Filhos** que se motivam mais com metas visuais, pontos e prêmios

---

## Níveis de acesso

O sistema possui quatro perfis distintos, cada um com sua área e permissões:

| Perfil | Quem é | O que pode fazer |
|---|---|---|
| **CEO / Admin** | Você (o gestor da plataforma) | Gerencia todos os grupos de famílias, cria os primeiros acessos |
| **Super Responsável** | Primeiro pai/mãe de cada família | Cria outros responsáveis e filhos da família |
| **Responsável** | Pai, mãe ou tutor | Cria tarefas, aprova conclusões, gerencia recompensas e resgates |
| **Filho** | A criança | Conclui tarefas, acumula pontos, resgata recompensas |

---

## Fluxo básico de uso

```
CEO cria a família
    └─▶ CEO cria o Super Responsável (com senha temporária)
            └─▶ Super Responsável troca a senha no primeiro acesso
                    └─▶ Super Responsável cria filhos e outros responsáveis
                            └─▶ Responsável cria tarefas e recompensas
                                    └─▶ Filho conclui tarefas e ganha pontos
                                            └─▶ Filho resgata recompensas
                                                    └─▶ Responsável aprova o resgate
```

---

## Área do CEO / Admin

### Dashboard
Visão geral de toda a plataforma: total de famílias, usuários, tarefas, transações, resgates e notificações não lidas. Inclui gráfico de distribuição e ranking de famílias por número de membros.

### Gerenciamento de Grupos (Famílias)
- Criar um novo grupo com nome personalizado
- Renomear ou desativar grupos existentes
- Ver todos os membros de um grupo com seus papéis e pontos
- Adicionar o primeiro responsável diretamente pelo painel, definindo nome, e-mail e senha temporária

> **Nota:** O membro criado pelo CEO receberá uma senha temporária e será obrigado a trocá-la no primeiro acesso.

---

## Área do Responsável

### Dashboard
Resumo da família: tarefas por status (gráfico de rosca), pontos de cada filho (barras comparativas), membros ativos e tarefas pendentes de aprovação.

### Tarefas

#### Criar uma tarefa
1. Clique em **+ Nova tarefa**
2. Preencha o título, pontos, atribuição ao filho e, opcionalmente:
   - **Recorrência**: a tarefa se renova automaticamente após ser aprovada (diária, semanal ou mensal)
   - **Data de vencimento**: prazo para o filho concluir
   - Descrição detalhada
3. Clique em **Criar**

O filho é notificado imediatamente.

#### Aprovação de tarefas
Quando o filho marca uma tarefa como feita, ela aparece com status **Aguardando** na lista. O responsável pode:
- **Aprovar**: os pontos são creditados automaticamente ao filho
- **Rejeitar**: com ou sem observação; o filho é notificado com o motivo

#### Tarefas recorrentes
Se a tarefa for recorrente, uma nova cópia é criada automaticamente no momento da aprovação, com o próximo prazo calculado. Não é preciso recriar manualmente.

#### Indicadores visuais nos cards
| Badge | Significado |
|---|---|
| 🔄 Diária / Semanal / Mensal | Tarefa recorrente |
| 📅 data | Prazo definido |
| ⚠️ Atrasada | Prazo já passou e tarefa ainda está aberta |
| Aguardando | Filho concluiu, esperando aprovação |

### Recompensas

#### Criar uma recompensa
1. Clique em **+ Nova recompensa**
2. Defina título, custo em pontos, estoque (deixe vazio para ilimitado) e descrição
3. Salve

#### Seções da tela
- **Disponíveis**: recompensas ativas com estoque. Filhos podem resgatar.
- **Esgotadas / Desativadas**: recompensas sem estoque ou desativadas. Invisíveis para os filhos.

> Ao desativar uma recompensa, ela some da loja dos filhos instantaneamente.

### Resgates
Painel com todos os pedidos de resgate dos filhos. Filtre por status: Todos, Pendentes, Aprovados, Entregues, Recusados.

- **Aprovar**: confirma o resgate (pontos já foram descontados no momento do pedido)
- **Recusar**: os pontos são devolvidos automaticamente ao filho
- **Marcar como entregue**: registra que a recompensa física foi entregue

### Membros
Lista de todos os integrantes da família com papel, pontos (somente filhos) e status. Super Responsáveis podem adicionar novos membros diretamente por aqui.

---

## Área do Filho

A interface do filho é otimizada para celular, com navegação por aba na parte inferior.

### Início (Dashboard)
- **Seus pontos**: saldo atual em destaque, com animação
- **Pontos essa semana**: bônus acumulado nos últimos 7 dias
- **Metas ativas**: barra de progresso para cada meta em andamento
- **Para fazer**: tarefas pendentes com botão "Feito!" para marcar como concluída
- **Avisos**: notificações recentes (aprovações, rejeições, metas atingidas)

### Tarefas
Lista de todas as tarefas atribuídas ao filho, com filtros por status. Cada tarefa mostra os pontos, prazo (se houver) e um indicador visual de urgência.

### Prêmios

#### Aba Loja
Todas as recompensas disponíveis. Para cada uma:
- Barra de progresso mostrando quantos pontos faltam
- Badge **✓ Pode resgatar** quando o saldo é suficiente
- Botão **🎉 Resgatar** habilitado automaticamente ao atingir o saldo

Ao resgatar, os pontos são descontados e o pedido fica **Pendente** até o responsável aprovar.

#### Aba Resgates
Histórico de todos os pedidos feitos pelo filho. Cada item mostra o nome da recompensa, data, pontos gastos e status com cor:

| Cor | Status |
|---|---|
| Amarelo | Pendente (aguardando aprovação) |
| Roxo | Aprovado |
| Verde | Entregue |
| Vermelho | Recusado (pontos devolvidos) |

#### Aba Histórico
Extrato completo de todas as movimentações de pontos: cada tarefa aprovada, bônus recebido e resgate feito, com data e valor.

### Conquistas
Galeria de badges desbloqueáveis. Os bloqueados aparecem como desafios a alcançar; os desbloqueados mostram a data em que foram conquistados.

| Badge | Como desbloquear |
|---|---|
| 🌟 Primeira tarefa! | Concluir a primeira tarefa |
| 🔥 Dedicado | Concluir 10 tarefas |
| 🏆 Campeão | Concluir 50 tarefas |
| 🎯 Meta atingida! | Concluir a primeira meta |
| 🎁 Primeiro prêmio! | Fazer o primeiro resgate |
| 💯 Centenário | Acumular 100 pontos |
| 💎 Explorador | Acumular 500 pontos |
| 👑 Lendário | Acumular 1000 pontos |

---

## Notificações

Todos os eventos importantes geram notificações automáticas:

| Evento | Quem recebe |
|---|---|
| Tarefa atribuída | Filho |
| Tarefa concluída (aguardando aprovação) | Responsável |
| Tarefa aprovada | Filho |
| Tarefa rejeitada (com motivo) | Filho |
| Meta atingida | Filho |
| Resgate solicitado | Responsável |
| Resgate aprovado / recusado | Filho |

---

## Segurança e acesso

- Autenticação por e-mail e senha com token JWT
- Cada família é completamente isolada das outras
- Membros só visualizam dados da própria família
- Troca de senha obrigatória no primeiro acesso para usuários criados pelo administrador
- Senhas armazenadas com hash bcrypt

---

## Perguntas frequentes

**Os pontos expiram?**
Não. Os pontos acumulados ficam no histórico para sempre.

**O que acontece se um resgate for recusado?**
Os pontos são devolvidos automaticamente ao saldo do filho.

**Posso desativar uma tarefa sem excluí-la?**
Sim. O botão Ativa/Inativa oculta a tarefa do filho sem apagá-la. Você pode reativá-la a qualquer momento.

**Uma tarefa recorrente pode ter prazo?**
Sim. Defina a data de vencimento na criação; a cada renovação, o prazo avança automaticamente pelo período configurado (1 dia, 7 dias ou 30 dias).

**O filho pode ver recompensas sem estoque?**
Não. Recompensas esgotadas ou desativadas são invisíveis para os filhos.

**Como adicionar mais membros à família?**
O Super Responsável (primeiro responsável da família) acessa a aba **Membros** e clica em **+ Adicionar membro**, definindo nome, e-mail, papel e senha temporária.
