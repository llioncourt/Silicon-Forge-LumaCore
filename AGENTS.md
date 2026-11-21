# AGENTS.md — Silicon Forge LumaCore

## Politica de edicao
- Trabalhar **exclusivamente na branch `main`**. Nunca criar branch, fork, PR ou repositorio paralelo sem autorizacao explicita do proprietario.
- Ao concluir uma entrega, commitar arquivos, registrar o SHA e listar o que ainda nao foi migrado. Nao declarar sucesso antes de verificar o commit remoto.
- Nenhuma ferramenta pode sobrescrever STL ou PWSZ original; todo resultado derivado usa novo nome + log.
- Evitar dependencias globais, venv global, caches dispersos. Aplicativos e recursos portateis residem em `runtime/`, ignorado pelo Git.
- Scripts Windows com BAT amigavel, tratamento de caminhos com espacos/acentos, logs em `runtime/logs/`. Se baixar de terceiro, fixar versao e SHA-256, documentar licenca e procedencia. Nao fingir que o binario foi commitado quando o repositorio contem apenas um bootstrap.

## Objetivo fisico
- Principal: iluminar **toda a escultura**, priorizando rosto, maos, tronco e destaque artistico da base cristalina, sem modificar a superficie artistica salvo autorizacao.
- Conjunto previsto: **Anycubic Photon Mono M7 Pro**, Standard Resin Anycubic azul translucida, ACF, Normal Print, 0,050 mm, 1,800 s normais; cupom original de 80 camadas, 5 de base, 25 s base.
- Acabamento **Unipega alto brilho** faz parte do projeto optico. Nunca substituir por Tekbond.
- Sem ilhas, bolhas de resina nao curada, cavidades internas lacradas, furos, frestas, malha nao-manifold, faces invertidas ou dependencia de reparo do slicer.
- A integridade geometrica deve ser verificada por mais que apenas `is_watertight`.

## Criterios de evidencias
- Nao chamar grayscale digital de dose fisica medida; `15/15`, `14/15`, `13/15` so sao codigos PW0.
- Nao chamar pads/padroes internos de guias opticos antes de medir desviacao/indice; fotos com iPad nao medem ∆n.
- Diferenciar UV de fabricacao (~405 nm) da luz visivel do LED; absorcao/pigmento/espectro/importancia do indice e Unipega precisam ser calibrados.
- Fazer controle sem microdose na mesma geometria e mesmas condicoes; registrar orientacao da peca e exposicao da camera. Controlar pos-cura e secagem do verniz.
- Nao promover projeto para PWSZ da escultura inteira antes de confirmar resposta reprodutivel do material e dose acumulada.
- Usar `UVtools` (integracao `integrations/uvtools`) para auditoria read-only de PWSZ gerado; manual de impressora e previsualizacao nao substituem validacao material.
- Codigo de terceiros permanece identificado, com licenca e creditos.

## Referencias obrigatorias
- `research/REVISAO_CIENTIFICA_GRIN_GMSLA_2026-11-21.md`
- `research/ANYCUBIC_M7PRO_COMUNIDADE_GRAYSCALE_2026-11-21.md`
- `research/ANYCUBIC_CLEAR_LIU_2026_EXPOSICAO_CUMULATIVA.md`
- `research/UVTOOLS_M7PRO_WAVEGUIDES_DEEPDIVE_2026-11-21.md`
- `integrations/uvtools/README.md`
- `ARTIFACTS_MANIFEST.md`

## Proximas entregas
- Acompanhar `issues/2` nos gates: irradiancia real, cura/persistencia do indice, simulacao de transporte, otimizacao e QA.
- `issues/1`: arquivos STL/PWSZ binarios ainda faltantes no repositorio; nunca fechar ate verificar download direto.

## Suportes / cena editavel antes da microdosagem (correcao obrigatoria)
- Um `.pwsz` salvo diretamente e um arquivo **ja fatiado**, nao um projeto nativo editavel com suportes. O Photon Workshop nao consegue necessariamente voltar a uma cena apos abrir apenas `Slice File Preview`.
- Para qualquer escultura, seguir **STL aprovado -> Photon Workshop -> orientacao e suportes -> salvar cena editavel `.pwscene` -> fatiamento `.pwsz` NATIVO -> aplicar mapa UV SOMENTE na copia do fatiado com suportes -> UVtools/Photon Workshop QA**.
- Nunca entregar um PWSZ final sem que suportes tenham sido adicionados/verificados e a cena editavel do slicer esteja preservada. Se nao for possivel gerar/validar uma cena `.pwscene`, declarar pendente e entregar o STL para edicao; nao chamar o PWSZ experimental de imprimivel.
- Ao modificar grayscale em camadas ja fatiadas, separar pixels de suportes dos pixels do modelo (ou preservar toda a estrutura dos suportes com valores originais), validar ilhas e integridade com UVtools.
- Regra especifica deste projeto: **plinto LED da escultura ja estava aprovado**. Nao criar outro plinto e nao alterar qualquer geometria sem permissao.
