# M7 Pro, Anycubic e comunidade maker: engenharia reversa do grayscale (2026-11-21)

## Escopo e estatuto
Revisão ampliada e prioritariamente orientada para **Anycubic M7 Pro 14K, Standard Resin azul translúcida, ACF, 0,05 mm, 1,8 s, Unipega alto brilho**. Fontes primárias (Anycubic, código e artigo científico) são separadas de fontes secundárias / relatos de usuários (Reddit). Não presumir que técnicas de outras impressoras ou resinas se aplicam automaticamente.

**Conclusão:** Há soluções consolidadas para ler/manipular PWSZ, calibração física de grayscale em impressora Anycubic comercial, scripts abertos de LUT/dithering e implementação de anti-aliasing vertical. Falta demonstração específica de que a M7 Pro reproduz 13/15 e 14/15 com doses distintas **e** que a Standard Resin azul mantém diferenças de índice de refração pós-cura.

## 1. A comunidade já decifrou PWSZ
- https://github.com/sn4k3/UVtools/discussions/892 — discussão M7 Pro desde 2024, mais de 40 respostas; dois tipos de imagem de camada: contorno vetorial \`.pwszImg\` e raster \`.pw0Img\`.
- https://gist.github.com/Xaymar/26efa376cd39b33a078d0e42895c0b05 — documentação de contêiner ZIP, metadados de exposição, anti-aliasing, níveis de cinza, contornos.
- https://github.com/sn4k3/UVtools — aplicativo/CLI AGPL-3.0 que lê e salva PWSZ, converte camadas e detecta defeitos (ilhas, cavidades e afins).
- Código-fonte: \`UVtools.Core/FileFormats/AnycubicZipFile.cs\` usa \`AnycubicFile.DecodePW0\` para \`.pw0Img\`; carrega \`.pwszImg\` separadamente por decodificador vetorial.

**Conseqüência:** nosso conversor experimental não precisa mais reinventar a interpretação dos contornos da Anycubic. Para novas implementações, comparar com UVtools e documentação do formato; licença AGPL impõe cuidados de redistribuição, portanto não copiar o código sem examinar obrigações.

**Versão verificada da referência externa em 21/11/2026:** UVtools v7.1.2 (26/10/2026); v7.1.0 (16/10) corrigiu uma causa de arquivos PWSZ rejeitados pelo Photon Workshop e a alocação excessiva de memória com raster da Anycubic. v7.0.3 (09/10) corrigiu contornos PWSZ sobrepostos/tangentes classificados como furos.  
Releases: https://github.com/sn4k3/UVtools/releases

## 2. O LCD pode ter gamma, profundidade de cinza e LUT dependentes da placa
- A Anycubic documenta que o Gray Level altera a luminosidade dos pixels *anti-aliased* do Photon Workshop, mas não fornece tabela \`G -> mW/cm²\` para a M7 Pro.
- Manual: https://wiki.anycubic.com/photon-mono-m7-pro/anycubic_photon_workshop-en-v0.2.0-b.pdf
- Questão técnica UVtools #1104, criada em março/2026: https://github.com/sn4k3/UVtools/issues/1104. Um desenvolvedor mediu painéis 8/12/16K de outras máquinas, usando medidor UV Chitu e outro medidor. Obteve exponentes de gamma aproximadamente 2,9 a 3,1 e pede correção do calibrador de grayscale; **NÃO é medida da nossa M7 Pro.**
- Exemplo ilustrativo APENAS: sob um modelo arbitrário \(I/I_{max}=(G/15)^3\): 14/15 -> ~81,3% e 13/15 -> ~65,1%; sob relação linear seriam 93,3% e 86,7%. Resultados reais não podem ser inferidos.
- Reddit (relato não revisado por pares): https://www.reddit.com/r/resinprinting/comments/1nlp5k2/psa_16k_printers_do_not_have_fully_functional/ — alguns painéis 16K têm poucas intensidades úteis, o autor sugere que 14K não sofre necessariamente do mesmo problema mas NÃO calibrou a M7 Pro. Nos comentários, observa que Anycubic pode usar profundidade digital de 4 bits e que as resinas respondem de modo muito diferente.
- A M7 Pro é 14K (13.312x5.120 pixels, 16,8x24,8 µm); e mantém valores PW0 codificados em 4 bits. **Codificação 4-bit != 16 níveis radiométricos distinguíveis garantidos.**

## 3. Ciência validada em UMA impressora Anycubic
Turek et al. (2025), *Applied Sciences* 15(13):7412, DOI 10.3390/app15137412.  
Artigo: https://www.mdpi.com/2076-3417/15/13/7412

- Equipamento: Anycubic Photon M3 Premium, **não** M7 Pro.
- Material: Anycubic ABS-Like Resin Pro 2, **não** Standard Resin azul.
- Usaram medidor UV 405 nm Chitu P405L1 para mapear intensidade sobre o LCD, ajustaram relação não-linear entre cinza e irradiância com regressão, depois geraram máscara de compensação.
- Desvio-padrão de irradiância reduziu de 0,26 para 0,17 mW/cm² após correção.
- Provaram **uniformização UV e melhora geométrica**, NÃO guia de luz visível ou GRIN interno.
- Boa referência de projeto de calibração M7 Pro: medir posições, ajustar \`I(G,x,y)\`, otimizar exposição; não usar a curva da M3 Premium na M7.

## 4. Hacks públicos de grayscale e anti-aliasing em resina
- https://github.com/aaron1138/UVTools-Scripts e https://github.com/aaron1138/Voxel-Stack-Blender
- O criador publicou scripts C# para UVtools: \`VerticalSuperSampler-LUT-FSDithering.cs\`, \`ApplyLUTandFSDithering.cs\`, \`ExposureCalibrationMasking.cs\`, \`ScriptLUTEngine.cs\`, e algoritmos de campo de distância e mistura entre camadas.
- Usa **slicing Z supersampled** (ex. 5 µm para camada 40 µm) para obter ocupação subcamada, mistura em Z, LUT da resposta de voxels e dithering de grayscale com gamma ajustável.
- O autor relata melhores resultados em resinas opacas específicas: Anycubic Texture Gray / Beige / Peach / White, Siraya Tech Fast ABS-like Navy Gray / Gray, AceAddity Standard Elite 8K Gray / White.
- **Relato contrário à nossa hipótese:** o autor recomenda *evitar resinas clear de consumo* para anti-aliasing volumétrico porque observa forte bloqueio UV e baixa resposta de voxel parcial em seus testes. Isso é sobre CRESCIMENTO PARCIAL de voxel para superfície suave, NÃO prova incapacidade de gerar algum gradiente de índice na Standard Resin azul pós-curada. Precisamos medir nossa mistura.
- O script \`ExposureCalibrationMasking.cs\` implementa subdivisão de exposição por zonas, clonando cada camada no mesmo Z e sem levantamento intermediário. Não executar indiscriminadamente na M7 Pro: suporte a múltiplas subexposições por camada nesse firmware **não foi validado**.

## 5. Controles nativos sem software experimental: R_E_R_F
- Manual oficial M7 Pro: https://wiki.anycubic.com/photon-mono-m7-pro/photon_mono_m7_pro-en-v0.0.7.pdf
- Ficheiro \`R_E_R_F.pwsz\`, específico da M7 Pro, contém 8 posições com tempos normais crescentes de 0,25 s por posição.
- Outra interface, \`Calibration -> Resin Exposure Time\` no Photon Workshop, mostra um modo dividido em 6 posições e passo configurável: https://wiki.anycubic.com/photon-mono-m7-pro/Photon%20Mono%20M7%20Pro-EN-V0.1.0.pdf
- Não confundir RERF da M7 Pro com o arquivo de outro modelo; o nome especial ativa calibração no firmware, não deve ser atribuído a impressões normais.
- O modo é útil para calibrar reação do material ao tempo de exposição de uma só vez; não mede efeito óptico nem calibra por si só a curva de gamma do LCD.

## 6. Fabricantes/usuários enfrentam problemas reais de gradiente e anticura
- UVtools Wiki: https://github.com/sn4k3/UVtools/wiki/Anti-aliasing — alerta que tons muito escuros geram pixels subcurados, borrão leitoso, detritos ou falsa sensação de suavização.
- Reddit sobre exposição e cinza 80 amostras no Mono 4K: https://www.reddit.com/r/AnycubicPhoton/comments/wyfsf3/attempt_to_make_antialiasing_work_exposure_time/ — apenas uma combinação reportada como claramente boa; alto risco de exagerar a generalização.
- Reddit, usuário que imprime guias ópticos transparentes: https://www.reddit.com/r/ElegooMars/comments/hrlbg8 — relato de luz UV seguir caminhos internos e curar resina indevida na impressão, sobretudo onde há quinas; é anedótico, mas coerente com a necessidade de controlar penetração UV e reflexão.
- Fórmula geral: \`grayscale digital\` -> \`energia UV real\` -> \`conversão e cura cruzada\` -> \`n, dispersão e absorção\` -> \`transporte de luz visível\`. Nossa versão atual não contém medições para nenhum elo causal após o primeiro.

## 7. A fonte óptica ainda falta caracterizar
M7 Pro: COB + Fresnel + algoritmo de uniformidade; potência de irradiância nominal 5.500 +/- 10% µW/cm² (especificação de fabricante; valor nominal e tolerância não determinam curva G nem a variação local). https://store.anycubic.com/products/photon-mono-m7-pro

Standard Resin, 0,05 mm/1,8 s é também um perfil publicado pelo fabricante para M7 Pro (várias tabelas oficiais diferem por versão; nosso perfil real foi obtido do PWSZ): https://store.anycubic.com/blogs/news/resin-settings-for-anycubic-3d-printers

A luz UV que imprime (aprox. 405 nm) NÃO equivale ao LED branco que ilumina a escultura após cura. É necessário medir a faixa azul visível e a influência do Unipega, não só a dose UV.

## 8. O plano de engenharia concreto

### Gate 0: validação da entrega UV real
1. Usar medidor UV 405 nm apropriado (como Chitu P405L1 citado no artigo), nunca foto de LCD exposto; **não retirar proteções para olhar diretamente a fonte UV**.
2. Medir G=15/15, 14/15, 13/15 com geometria idêntica e tempos iguais em 3 ou mais pontos da tela; ampliar escala se houver empate por quantização.
3. Criar LUT digital-energia específica da M7 Pro e, se necessário, correção de uniformidade \`I(G,x,y)\`.
4. Testar com UVtools, sem alterar original, e controlar se salvar/reabrir preserva os metadados e a nuance do PWSZ. Manter logs e check de hash.

### Gate A: reação da resina
1. Imprimir controlo e réplicas com dose variável na MESMA leva; marcação A/B/níveis externa e geometria repetida. Não usar cavidade encapsulada nem pixels totalmente apagados internos.
2. Repetir com tempos distintos controlados pelo RERF para verificar curva de reação da resina, sem atribuir a ela capacidade GRIN.
3. Pós-cura idêntica; repetir medições para avaliar persistência das propriedades.
4. Teste de transmissão VISÍVEL e teste de desvio/índice separado; o JPEG da máscara sozinho não prova \`Delta n\`.
5. Unipega apenas depois de controles sem acabamento, para distinguir o efeito superficial.

### Gate B: só depois a escultura
1. Segmentar cristais, torso, mãos e rosto; identificar objetivos visuais.
2. Modelo de dose acumulada em Z e dispersão XY com segurança de cura mínima.
3. Medir \`n(lambda), mu_a(lambda), mu_s(lambda)\`; ajustar simulação da fonte LED.
4. Otimização inversa sob malha externa intocada: sem ilhas, furos, resina presa ou reparos no slicer.
5. Comparar iluminância/contraste na escultura inteira com controle não modulado e Unipega equivalente.

## Fatos negativos importantes
- Capturas da prévia PWSZ da camada 40 NÃO provam intensidade UV na tela.
- Cupom íntegro NÃO prova cura completa nas zonas internas.
- Diferença entre três janelas em JPEG, sem correção instrumental rigorosa, NÃO prova Δn.
- Medições em 8/12/16K de outras marcas NÃO definem gamma da M7 Pro 14K.
- Scripts de anti-aliasing vertical em resinas opacas NÃO demonstram guias ópticos em resina azul.
- Tudo acima é pesquisa; nenhum novo PWSZ de estátua inteira foi produzido ou marcado como validado.

## Referências mais diretamente relevantes
1. Anycubic M7 Pro manual e documentação: https://wiki.anycubic.com/photon-mono-m7-pro/photon_mono_m7_pro-en-v0.0.7.pdf
2. Engenharia reversa M7 Pro: https://github.com/sn4k3/UVtools/discussions/892
3. Especificação PWSZ: https://gist.github.com/Xaymar/26efa376cd39b33a078d0e42895c0b05
4. UVtools v7.1.2: https://github.com/sn4k3/UVtools/releases/tag/v7.1.2
5. Gamma, medições e erro da calibração: https://github.com/sn4k3/UVtools/issues/1104
6. Código de LUT e Z supersampling: https://github.com/aaron1138/UVTools-Scripts
7. Turek et al. (2025): https://doi.org/10.3390/app15137412
8. Grayscale UVtools: https://github.com/sn4k3/UVtools/wiki/Anti-aliasing
9. Leitura comunitária (14K x 16K): https://www.reddit.com/r/resinprinting/comments/1nlp5k2/psa_16k_printers_do_not_have_fully_functional/
