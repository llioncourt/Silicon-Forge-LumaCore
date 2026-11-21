# UVtools, M7 Pro, grayscale e óptica — investigação aprofundada (2026-11-21)

## Resposta curta: o que é UVtools?
UVtools é um aplicativo open-source **AGPL-3.0** de Tiago M. F. Conceição, com versão portátil Windows x64, interface gráfica, CLI e biblioteca .NET `UVtools.Core`. É um **editor, auditor e conversor de arquivos JÁ FATIADOS para impressoras de resina**, não um programa de GRIN óptico e não o firmware de qualquer impressora. Pode ler PWSZ, extrair e editar camadas, inspeccionar ilhas, overhangs, resin traps, sucção, revisar parâmetros, testes de grayscale e executar scripts de transformação.

Página de origem: https://github.com/sn4k3/UVtools  
Última versão verificada: **v7.1.2, 2026-10-26**, via API de releases do GitHub.  
Portable Windows x64 (ZIP): https://github.com/sn4k3/UVtools/releases/download/v7.1.2/UVtools_win-x64_v7.1.2.zip  
Formato do ZIP: extrair para uma pasta e executar localmente, sem instalação global.

## Engenharia reversa da M7 Pro: descoberta mais útil
Discussão iniciada junho/2024: https://github.com/sn4k3/UVtools/discussions/892

- Os arquivos M7 Pro são `.pwsz`, contêineres ZIP com metadados e imagens por fatia.
- As camadas podem usar **`.pwszImg` vetorial (contornos)** ou **`.pw0Img` raster / RLE**. O formato de imagem declarado no JSON interno pode divergir do formato encontrado na pasta de camadas. Verificar **conteúdo real**.
- No tópico de dez/2024, desenvolvedor UVtools observou `.pwszImg` preferido em alguns modos com baixo antialiasing e `.pw0Img` com AA maior, portanto não usar a extensão externa `.pwsz` como indicadora da capacidade de escala de cinza.
- O código atual `UVtools.Core/FileFormats/AnycubicZipFile.cs` seleciona decoder conforme extensão da imagem no ZIP. A M7 Pro do nosso laboratório já abriu a variante PWM raster e imprimiu o cupom.
- Este precedente justifica substituir nosso decodificador ad hoc por implementação bem testada e manter função de auditoria binária/hash sobre o arquivo gerado.

## Problemas REAIS da M7 Pro e por que usar versão nova
1. Issue #983 (jan/2025, encerrada maio/2025): após salvar, certas versões modificavam incorretamente o volume de resina no job. O usuário relatou avisos na impressora. https://github.com/sn4k3/UVtools/issues/983
2. Issue #1108 (abr/2026, encerrada junho/2026): UVtools v6.0.3 exportava `.pwsz` rejeitado no Photon Workshop. Comentários identificaram campo omitido em `lcd_function.json` / `partition_exposure_array`; o comportamento diferia por release. https://github.com/sn4k3/UVtools/issues/1108
3. Issue #1155 (out/2026, encerrada outubro/2026): regressão em campos opcionais da resina que podia tornar PWSZ importado ilegível; a correção consta na release **v7.1.0**, 16/10/2026. https://github.com/sn4k3/UVtools/issues/1155
4. v7.0.3 (09/10/2026): correção em contornos PWSZ sobrepostos/tangentes interpretados erroneamente como furos; particularmente importante para nossa regra de **nunca pedir ao slicer reparar malha**.
5. v7.1.0: correção de memória para camadas grandes PWSZ / PW0. v7.1.2 (26/10/2026): melhorias adicionais em problemas de reparo de ilhas.
   
**Conclusão:** reabrir no Photon Workshop e inspecionar preview não substitui teste do firmware, sobretudo ao editar um job grande. Preservar sempre PWSZ original e comparar metadados/camadas antes de liberar a impressão.

## UVtools já tem ferramentas que o LumaCore não deveria reinventar
- `Calibration > Grayscale`: padrão de teste de intensidades; apenas taxa de cura, não mede índice de refração.
- `Calibration > Exposure Time Finder`, **Multiple Brightness** com **gamma configurável**; issue #1104 implementada na linha v7. Teste de unidade comprova cálculo dos coeficientes de correção (por exemplo `(204/255)^3=0,512`). https://github.com/sn4k3/UVtools/issues/1104
- `Tools > Pixel arithmetic`, filtros de imagens, operações por camada e scripts (C#).
- `UVtoolsCmd` e `UVtools.Core` para automatizar abertura, operações e verificação de arquivos.
- O próprio wiki ressalta que tons escuros demais podem gerar resíduos parcialmente curados, sobretudo com grupos contíguos de pixels escuros, e que a faixa segura depende de resina, tempo, temperatura e UV. https://github.com/sn4k3/UVtools/wiki/Anti-aliasing
- Scripts do autor externo Aaron Baca em `third_party/` permitem LUT, dithering, calibração e supersampling Z; já copiados sob licença AGPL v3, **não integrados automaticamente**.

## Gama 3: exemplo de matemática, não calibração M7 Pro
A proposta comunitária #1104 reporta curva de gamma ~3 em painéis mono 8/12/16K DE OUTROS equipamentos. O teste de unidade de UVtools v7 usa expoente 3 e comprova a conta numérica. **Não há medição da curva I(G) na nossa M7 Pro.** Portanto, no exemplo:
- 15/15 → 100%
- 14/15 → (14/15)^3 ≈ 81,3%
- 13/15 → (13/15)^3 ≈ 65,1%

Esses percentuais **não são fatos experimentais para a M7 Pro**. Precisamos caracterizar irradiância local e penetração na Standard Resin azul. Além disso, 4 bits codificados no PW0 não garantem 16 níveis físicos distintos e estáveis.

## O achado experimental novo mais importante: guias de luz monolíticos e acabamento
Artigo **Ansert et al. (2026)**, *ACS Materials Au*, DOI https://doi.org/10.1021/acsmaterialsau.5c00251, publicado em 13/04/2026.

O grupo usou impressora **Formlabs Form 3 SLA** e **Clear Resin V4** (não Anycubic nem Standard Resin azul), para fabricar guias de onda Y e redes de ramificações. Testou geometria, comprimentos, ângulos de separação e acabamento de superfície. A transmissão espectral de amostras de 1 mm elevou-se em média **3,6 vezes** com lixamento e revestimento acrílico, de cerca de 12–21% para 52–67% no visível, nas condições experimentais específicas. A formulação do revestimento foi **Krylon Crystal Clear** e não Unipega; a camada aplicada tinha menos de 50 µm no protocolo.

Superfícies polidas/revestidas reduziram espalhamento e perdas na interface polímero/ar. Menores comprimentos, curvas suaves, separações menores e ramificações com ângulo reduzido melhoraram o transporte, nas geometrias Y do artigo. Não se pode extrapolar diretamente o 3,6x para a nossa estátua ou para o Unipega. **Guia óptico com superfície polímero/ar NÃO equivale automaticamente a guia enterrado dentro de uma peça uniforme e completamente maciça.** Mas confirma a importância do acabamento e otimização de acoplamento/extracção de luz em regiões determinadas.

Pontos relevantes para o LumaCore:
- validar o verniz **Unipega** como parte do sistema óptico, antes/depois com controle;
- priorizar geometria do acoplamento LED ↔ resina;
- não criar no STL original canais ou bolsões que prendam resina;
- projetar controle de luz com transmissão, espalhamento e refração separadamente; microdosagem só se mostrar ∆n de fato.

## Fatos físicos adicionais
- 2026 Liu et al., *Additive Manufacturing*, doi https://doi.org/10.1016/j.addma.2026.105406 — óptica de fase feita por exposição programada em LCD-VPP, calculando efeitos acumulados; **é a família de tecnologia mais próxima do GRIN desejado**, mas depende de material calibrado.
- Dissertação Valia (2026), https://repository.tudelft.nl/record/uuid:143dd67f-c0b9-4546-86b3-838070dcf293 — resinas de consumo testadas apresentaram pouca variação n com UV isolada; formulações dual-cure customizadas conseguiram variação maior. Apenas resumo público; texto completo embargado.
- Estudos do UVtools e óptica **não comprovam** efeito de grau de cura em Anycubic Standard Resin azul pós-curada com Unipega. O cupom LumaCore mostrou compatibilidade de arquivo e possível variação fotográfica, ainda confundida com iluminação do iPad.

## Proposta de arquitetura recomendada
1. **UVtools como ferramenta de referência e validação de arquivos**: portable, dentro da pasta do projeto, sem instalação global, arquivos originais preservados. Se for redistribuir UVtools ou vincular suas bibliotecas, respeitar AGPL e avisos. Não forçar dependências ocultas no LumaCore.
2. **LumaCore como motor óptico distinto**: mapa semântico da estátua, espectro LED, transferência na resina azul e Unipega, inversão de dose a partir do resultado óptico desejado e impressão com limites de cura.
3. **Validação em cascata**: PWSZ original → modificar cópia → reabrir UVtools → comparar conteúdo e parâmetros → Photon Workshop → teste físico controlado → medição material → somente então estátua inteira.
4. **Sem promessas** de guias de luz por pixel desligado ou de transmissividade melhor sem medições.

## Fontes diretas
- https://github.com/sn4k3/UVtools
- https://github.com/sn4k3/UVtools/discussions/892
- https://github.com/sn4k3/UVtools/releases/tag/v7.1.2
- https://github.com/sn4k3/UVtools/issues/983
- https://github.com/sn4k3/UVtools/issues/1108
- https://github.com/sn4k3/UVtools/issues/1155
- https://github.com/sn4k3/UVtools/issues/1104
- https://github.com/sn4k3/UVtools/wiki/Anti-aliasing
- https://github.com/sn4k3/UVtools/blob/master/UVtools.Core/Operations/OperationCalibrateExposureFinder.cs
- https://github.com/sn4k3/UVtools/blob/master/tests/UVtools.Tests/OperationCalibrateExposureFinderGammaTests.cs
- https://doi.org/10.1021/acsmaterialsau.5c00251
- https://doi.org/10.1016/j.addma.2026.105406
