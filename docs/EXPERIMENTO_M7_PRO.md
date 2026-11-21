# Experimento Anycubic Photon Mono M7 Pro

## Estado em 2026-11-21
O cupom experimental com tres faixas digitais foi reconhecido no Photon Workshop e mostrou na camada 40 (2,03 mm) tres tons: branco (15/15), cinza (14/15) e cinza mais escuro (13/15). O usuario iniciou a impressao do cupom na M7 Pro. **Resultado fisico ainda pendente**. A inspecao de preview nao garante curva real de irradiancia, cura integral ou efeito optico.

### Perfil confirmado
- Anycubic Photon Mono M7 Pro
- Standard Resin Anycubic; material usado: translucido azul
- ACF Film, Normal Print
- 0,050 mm por camada
- 1,800 s exposicao normal
- Arquivo cupom fornecido: 80 camadas, 5 bottom layers a 25 s
- Acabamento previsto para estatua: verniz Unipega alto brilho (nao substituir)

## Arquivo de origem
`01_CUPOM_CALIBRACAO_DOSE_UMA_PECA.pwsz`, produzido pelo Photon Workshop, com 80 mascaras `.pwszImg` vetoriais. O arquivo nao transportava niveis de cinza internos suficientes para microdosagem.

## Conversao experimental
A geometria vetorial de um unico retangulo 90 x 24 mm foi rasterizada em grade nativa 13312 x 5120, gerando imagens `.pw0Img` com RLE e 4 bits. O conversor tinha restricoes especificas de retangulo e rejeitava outros formatos.

- Controle: nivel digital 15/15
- Faixa de teste A: 14/15 (~93,3% do valor digital)
- Faixa de teste B: 13/15 (~86,7% do valor digital)
- Margem de 1,5 mm em torno de cada regiao
- Camadas 0-19 e 68-79 preservadas
- Camadas 20-67 modificadas (48 camadas)
- Nao surgiram novos pixels ligados/desligados comparando arquivo raster controle e microdosado
- Auditoria: 131.049.600 amostras de pixel modificadas acumuladas nas 48 camadas
- Parametros de impressao preservados entre controle raster e variante microdosada

Os niveis digitais NAO equivalem automaticamente a percentuais da energia UV. Nenhum arquivo da estatua inteira foi microdosado.

## Verificacoes pendentes
1. Aceitacao e comportamento do arquivo no firmware da M7 Pro
2. Comportamento fisico do cupom, cura completa, ausencia de trincas, bolsos de resina nao curada ou delaminacao
3. Transmitancia e espalhamento na resina azul, controle vs doses
4. Registro de fotografias com LED real e exposicao manual fixa
5. Repeticao do teste apos aplicacao e secagem total do Unipega
6. Medicao do ganho optico antes de aplicar microdosagem na estatua

**Aviso:** manter curadoria de arquivos experimentais para evitar que um arquivo inadequado seja confundido com producao certificada.
