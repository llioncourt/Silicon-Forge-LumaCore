# Revisão científica: gMSLA, GRIN e modulação de dose UV para LumaCore

Data: 2026-11-21. Status: revisão de literatura e inspeção de código público; **não é validação experimental do LumaCore**.

## Sumário executivo

A ideia de fabricar um gradiente de índice de refração dentro de um polímero sólido usando dose UV espacialmente modulada já possui precedentes demonstrados. gMSLA/g-DLP e LCD-VPP são os processos de fabricação; Gradient-Index Optics (GRIN) é a classe de estruturas ópticas; *inverse design* é a otimização de um padrão de exposição para atingir uma resposta óptica desejada. **Nenhum desses termos deve ser confundido com garantia de que uma resina azul comercial responde da mesma forma.**

LumaCore procura usar exposição espacial em uma impressão MSLA para modificar o transporte de luz VISÍVEL dentro de uma escultura maciça e ressaltar rosto, mãos e torso sem destruir a base cristalina. Isso difere de lentes GRIN de imagem e DOEs para feixe coerente em vários aspectos: a fonte LED é extensa, policromática e incoerente; a resina pigmentada pode absorver/espalhar fortemente; a geometria é irregular; a qualidade do acabamento com Unipega afeta a interface de saída. Necessitamos caracterizar o material antes de otimizar um campo 3D.

## Prior art, de mais diretamente aplicável a menos direto

### 1. Liu et al. (2026), *Additive Manufacturing*, 105406
DOI: https://doi.org/10.1016/j.addma.2026.105406

**Evidência verificada por resumo do artigo:** plataforma de fotopolimerização em cuba com LCD; índice de refração programável pela exposição; efeitos acumulados entre múltiplas camadas; compensação de interfaces e *physics-aware differentiable inverse design*; produziram DOEs (Dammann, espiral etc.) com resposta experimental próxima ao modelo.

**Atenção:** o texto integral não estava livremente acessível nesta revisão, portanto nenhum detalhe de fórmula, resina, faixa Δn ou parâmetros de dose é atribuído a este artigo sem verificação.

**Aplicação:** maior precedente conceitual da arquitetura LumaCore; demonstrar a existência de trabalhos LCD-VPP de óptica interna, e justificar modelo inverso com restrições de imprimibilidade.

### 2. Tu et al. (2025), ACS Applied Optical Materials 3(6), 1197–1207
DOI: https://doi.org/10.1021/acsaom.5c00143
Código: https://github.com/pcl-hub/3DPrintGRINOptics
Dados: https://doi.org/10.5281/zenodo.10667945

**Evidência:** usaram resina específica de Bis-EMA + iniciador TPO, DLP com gradação de cinzas e modelo calibrado de conversão; obtiveram lentes GRIN poliméricas com mudança de índice de até aproximadamente 0,01. Índices usados na configuração pública de exemplo: n1 = 1,565 e n2 = 1,555. Importante: não é Standard Resin azul da Anycubic. O procedimento usa **várias projeções por camada física**, com durações e intensidades distintas; o algoritmo leva em conta cura das camadas anteriores devido à penetração da luz UV.

**Limite relatado pelos autores:** calor de polimerização elevou conversão acima da meta; gradientes decorrentes de cura parcial podem se alterar com tempo, temperatura e luz solar. As lentes estudadas se mantiveram sem alteração detectável da distância focal em 3 meses no escuro (esse teste não demonstra estabilidade de todos os materiais nem condições de uso).

#### Inspeção do código MATLAB dos autores, feita em 2026-11-21

- startGRIN.m: exemplo com índice 1,565→1,555, 12 regiões; lente 6,35 mm de diâmetro externo e 3 mm de espessura; carrega BisEMA.mat e parâmetros discretos candidatos; modelo roda com amostragem Z de 20 µm.
- functions/printerinfo.m: existe uma calibração **específica de outro equipamento**. Para MonoPrinter1-246, intensidade vs valor digital dada por 0,004007 * g - 0,177702; não transferir essa curva para Anycubic.
- functions/isoimages.m: discretiza campo GRIN em regiões espaciais, gerando máscaras por região.
- scripts/zconversionprofile_matrixcalculation.m: computa contribuições de cada exposição ao longo de Z com penetração atenuada exp(-z/Dp), energia efetiva, inibição por oxigênio, acúmulo por múltiplos estágios e mapeamento efetivo da dose para conversão.
- scripts/calculateprintparams_uniformconversion.m: busca combinações de espessura, tempo de exposição e cinza para aproximar conversão alvo ao longo da espessura; objetivo de erro quadrático, não de transporte de luz na escultura.
- scripts/recreatemonoimagesandbuildscript.m: ordena várias exposições por estágio e gera imagens/microprogramação de impressão específicas da MonoPrinter. Não produz PWSZ da M7 Pro.
- Materiais BisEMA.mat dependem de estruturas de MATLAB e funções de ajuste; o código usa toolboxes/funções auxiliares do MATLAB. Precisamos traduzir o princípio matemático, não copiar diretamente os valores nem supor portabilidade.

### 3. Engelhardt e colaboradores (2025), comparativo Raman × interferometria
DOI: https://doi.org/10.1021/acsaom.5c00084

**Evidência:** mapas ópticos impressos exibiram Δn frequentemente **abaixo da meta 0,01**. Os autores relatam RGRIN ~0,0030 (Raman) vs ~0,0020 (Mach-Zehnder), FLF ~0,0042 vs ~0,0066, com discrepâncias entre técnicas, influência de heterogeneidade entre amostras e artefatos das projeções. Raman informa conversão superficial/local; interferometria mede efeito integrado através da espessura. Fotografias de transmissão em JPEG **não são** medidas de Δn.

**Aplicação:** uma variação visível em fotos das três janelas não prova GRIN. Precisamos de ensaio de desvio de raios/fase/índice, preferivelmente contrastado com controle impresso na mesma leva.

### 4. Valizadeh et al. (2025), *Progress in Additive Manufacturing*
DOI: https://doi.org/10.1007/s40964-025-01326-8

**Evidência:** gMSLA com LCD monocromático comercial (Prusa SL1S) para propriedades mecânicas graduadas. Mediram intensidade na tela e obtiveram **naquela impressora** aproximadamente I(G) = Imax G² com G normalizado; sua resina tinha faixa útil segura de cinzas entre 0,6 e 1,0, e dose reduzida alterou módulo e escoamento.

**Aplicação:** não assumir que nível digital 14/15 aplica exatamente 14/15 da potência UV ou que o comportamento Prusa vale na M7 Pro. O mínimo de cura depende da resina. Não transportar o limite 0,6 para a Standard Resin.

### 5. Urness et al. (2015), *Optics Express* 23, 264–273
DOI: https://doi.org/10.1364/OE.23.000264

**Evidência:** GRIN com projeção em 8 bits e fotopolímero difusivo personalizado; perfil não linear compensado previamente. Demonstra GRIN óptico de superfície/plano, NÃO prova fabricação de estátuas volumétricas com impressora comercial.

### 6. Leites et al. (2026), *ACS Photonics*, DOEs baratos por grayscale
DOI: https://doi.org/10.1021/acsphotonics.5c02622

**Evidência:** DLP de uma única exposição produz um perfil de ALTURA na resina, completado com óleo de imersão e vidro próximos ao casamento de índice. Validaram phase masks e difração. É **física diferente do GRIN volumétrico**; não atribuir o resultado ao verniz Unipega. Útil como referência para o uso de estruturas de teste de fase/difração e calibração de ponta a ponta.

### 7. Valia (2026), dissertação TU Delft sobre resina dual-cure
https://repository.tudelft.nl/record/uuid:143dd67f-c0b9-4546-86b3-838070dcf293

**Evidência limitada ao resumo; texto integral embargado até 2028:** resinas comerciais isoladas apresentaram pouca mudança de n com UV; mistura UV + epóxi térmico produziu alterações maiores, Δn ~0,01–0,04 em formulações próprias. Isso reforça que o comportamento é específico da composição química, e não uma propriedade universal de toda resina translúcida.

## Física necessária: cadeia causal correta

valor digital de cinza G(x,y,k)
→ intensidade UV real na M7 Pro I_405(G,x,y,t) e difusão espacial/PSF
→ dose através da profundidade e exposições posteriores
→ cinética de cura / grau de conversão C(x,y,z,t,T)
→ n(λ,x,y,z), absorção μa(λ,x,y,z) e espalhamento μs(λ,x,y,z)
→ transporte de fótons visíveis (LED branco) na geometria REAL
→ potência e contraste visíveis em regiões de interesse.

Isso é um **problema inverso com restrições**; não basta desenhar microcélulas em x,y,z e supor que os fótons seguirão esses caminhos.

Modelo reduzido de dose (ponto de partida; não calibrado):

E(x,y,z) = sum_k t_k * I_405[G_k(x,y)] * exp[-(distancia_atingida_na_etapa_k)/Dp].

Versão mais fiel de cura radicalar: resposta depende de soma de contribuições de dose EFETIVA com expoente de intensidade, limiar de inibição por oxigênio e estado de conversão; a aproximação E = I*t nem sempre vale.

**Não usar a equação como código de impressão até medir Dp, Ecrit, I(G) e dinâmica da cura.** A luz de 405 nm que fabrica o polímero é diferente do espectro visível que ilumina a estátua; é preciso medir ambos separadamente.

## O que já foi validado no LumaCore e o que não foi

**Verificado:**
- A M7 Pro aceitou e executou o PWSZ do cupom de 80 camadas.
- Photon Workshop mostrou três cinzas digitais nas imagens da camada 40.
- A peça foi impressa, lavada e pós-curada; fotografada com o gabarito ScanNCut.
- Fotografias exibiram diferenças de luminosidade no JPEG entre as três janelas, mas o controle sem peça mostrou influência importante da tela do iPad.

**Não comprovado:**
- intensidade real entregue pelo LCD em cada nível 15/14/13;
- conversão química, índice de refração e espalhamento locais após pós-cura;
- existência de guias ópticos funcionais;
- garantia de cura em qualquer volume interno de objeto grande;
- melhora objetiva de rosto/mãos/torso na escultura;
- papel quantitativo do Unipega na transmissão/reflexão.

**Correção interpretativa:** padrões visíveis após impressão não são evidência suficiente de índice gradiente. Diferença de brilho de JPEG ≠ índice de refração; alteração de grayscale no PWSZ ≠ alteração material calibrada.

## Particularidades desta aplicação (LumaCore)

- Impressora: Anycubic Photon Mono M7 Pro, LCD 13312 x 5120.
- Resina/perfil usado: Anycubic Standard Resin azul translúcida, 0,050 mm, 1,800 s, ACF, Normal Print. Bottom do cupom original: 5 camadas, 25 s.
- PWSZ experimental utiliza PW0 com valores digitais 4 bits; 15/15, 14/15 e 13/15 não equivalem a potência relativa conhecida.
- LED USB é espectralmente diferente do UV 405 nm de fabricação; temperaturas de cor 3000/6000 K não determinam espectro.
- Unipega alto brilho é o acabamento final exigido. Só aplicar depois dos controles sem acabamento; a interface verniz/ar e verniz/resina pode reduzir espalhamento ou modificar reflexão interna, mas não corrige perda UV/visível do volume. Não substituir por Tekbond.
- A escultura original deve preservar malha e superfície, não desenvolver ilhas de cura, vazios encapsulados ou resina líquida por subcura; o slicer não deve ter de reparar geometria.

## Resultados de engenharia / correções de rumo

1. Trocar campos de dose arbitrários por modelo calibrado da máquina e material. Os campos anteriores em tools/sf_optical_masker.py são só uma hipótese espacial, NÃO um projeto GRIN.
2. Testar resposta real da resina após pós-cura normal, porque o mecanismo mais promissor envolve diferenças de conversão que podem se reduzir com pós-exposição.
3. Separar transporte de luz em material pigmentado: μa, μs e n. Não presumir que todo contraste observado vem de refração.
4. Usar controles na MESMA plataforma e mesmos pós-processos: uniforme 15/15, faixa 14, faixa 13, replicações e inversão posicional; registrar orientação A/B.
5. Medir efeitos ópticos capazes de detectar fase/desvio de feixe, não só claridade sob iluminação difusa do iPad. Um ensaio de luz colimada/grating, com segurança ocular, pode funcionar depois de controle de geometria.
6. Otimização espacial deve usar como restrição cura mínima estável e integridade; objetivo de priorizar regiões semânticas do STL (rosto > mãos/objeto > tronco > base cristalina, a validar com vistas).
7. Calcular ganho sobre **mesma geometria e mesmo LED** comparando controle uniforme vs modulado e repetir pós-Unipega.
8. Não criar PWSZ experimental de uma estátua de 150 mm até medir se ∆n ou μs variam de forma reprodutível e persistente nessa resina.

## Próximo marco recomendável

**Gate A: efeito de material**: comprovar diferença estável de fase/desvio de feixe ou índice entre zonas de dose e controle em amostras replicadas, mantendo pós-cura padrão. Se n for quase constante, abandonar GRIN como caminho principal com esta resina e explorar apenas controle superficial, LEDs/óptica externa ou formulação de material (esta última fora do escopo sem consentimento).

**Gate B: efeito volumétrico**: demonstrar que a diferença se sustenta ao longo de múltiplas camadas, evitando cura cruzada, zonas não curadas e interações de interface.

**Gate C: impacto visual na escultura**: somente então inverse design para luz distribuída em zonas semânticas, simulação espectral com absorção/espalhamento, e arquivo nativo cuja integridade seja comprovada em software e na impressão.

## Referências adicionais

- https://pmc.ncbi.nlm.nih.gov/articles/PMC8388578/ — cinética de dose efetiva e modulação 3D de módulo através de espessura.
- https://doi.org/10.1016/j.addma.2026.105406 — artigo LCD-VPP mais próximo do problema de programação interna.
- https://doi.org/10.1021/acsaom.5c00084 — medições independentes de Δn por Raman/interferometria.
- https://wiki.anycubic.com/en/resin-3d-printer/photon-mono-m7-pro — documentação da impressora.
