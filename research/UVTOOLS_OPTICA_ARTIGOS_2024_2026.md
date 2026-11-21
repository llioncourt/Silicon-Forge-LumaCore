# Evidências adicionais: MATLAB + UVtools em lentes ópticas e M7 Pro (2026-11-21)

## 1. Não somos os primeiros a associar UVtools e óptica
**3D Printing of Optical Lenses Assisted by Precision Spin Coating** — *Advanced Functional Materials* (2024), DOI https://doi.org/10.1002/adfm.202407165.
No texto metodológico, pesquisadores descrevem:
- impressora LCD modificada com módulo 8K da Phrozen, pixel ~22 µm;
- 405 nm e intensidade UV **medida** de 3,09 mW/cm² por medidor Chitu (não usar como valor da M7 Pro);
- camadas ~20 µm;
- fatiamento e impressão programados em **MATLAB e UVtools**;
- defocus da projeção e tratamento por spin coating para reduzir imperfeições de superfície.

**Implicação:** integrar UVtools ao LumaCore tem precedente prático direto em fabricação óptica. Não basta, porém, usar UVtools para produzir guias volumétricos: esse estudo produziu lentes por controle geométrico/superficial e acabamento.

## 2. Um estudo de Anycubic High Clear com superfícies ópticas
**Exploration of 3D-printed lenses in a confocal MEMS microscope concept** (Christopher et al., 2024): Phrozen Sonic Mini 8K S e **Anycubic High Clear**, n ≈ 1,50–1,51 (na resina específica), camada 10 µm, difusor de 0,1 mm e spin coating com segunda resina de índice próximo.
https://strathprints.strath.ac.uk/91803/1/Christopher-etal-IEEE-OMN-2024-Exploration-of-3D-printed-lenses-in-a-confocal-MEMS-microscope.pdf

Importante: **Unipega** pode suavizar superfície e mudar transmissão, mas sua formulação/índice não são conhecidos nem demonstrados equivalentes ao verniz/resina do artigo.

## 3. A relação entre máscara e cura varia no próprio painel
**Characterizing light engine uniformity and its influence on LCD-based vat photopolymerization printing** (2023; acesso gratuito PMC).
https://pmc.ncbi.nlm.nih.gov/articles/PMC9890382/

Autores mediram variações de irradiância, espectro e divergência óptica em função da posição num motor LCD nominal de 405 nm; as heterogeneidades afetaram conversão e textura. Isso justifica mapear a M7 Pro por posição, não somente um valor de gamma global.

A orientação correta para projeto de máscara óptica é:
\`I405(x,y,G,t)\` + PSF/crosstalk UV + história de cura \`C(x,y,z)\` → índice/atenuação/espalhamento no visível.

## 4. A estabilidade após UV posterior merece acompanhamento
**Tu et al. (2025)** https://doi.org/10.1021/acsaom.5c00143 mostram que conversão pode ultrapassar previsão por calor e que GRIN baseado em conversão parcial pode se modificar com exposição à luz/temperatura; lentes guardadas no escuro tiveram distância focal estável por 3 meses.

**Bennett et al.** https://pmc.ncbi.nlm.nih.gov/articles/PMC5828039/ mediram curvas de trabalho de resinas comerciais a 365/405 nm e encontraram grande dependência espectral. Valores de Dp/Ec não podem ser transplantados para nossa Standard Resin azul.

## 5. Novo precedente para dose-programada com resina do fabricante
**Liu et al. (2026)** DOI https://doi.org/10.1016/j.addma.2026.105406: Phrozen Sonic Mini 8K LCD 22µm, resina **Anycubic UV-sensitive Clear** a 405 nm, DOE de fase codificada por exposição e compensação cumulativa; a pagina publica informa patente provisoria. Não é a M7 Pro nem a Standard Resin azul.

**Conclusão de produto:** LumaCore deve admitir o objetivo de luz visível por regiões semânticas, mas o motor inverso de dose só pode ser desenvolvido depois de medir ganho óptico real e estabilidade. Simulação sem dados do material não justifica fabricar a estátua.

## 6. Plano sem retrabalho

**A. Infraestrutura concluída em software:** integração \`integrations/uvtools\` com Windows portable v7.1.2 verificado por SHA e smoke test no GitHub Actions.
**B. Pendente:** teste das rotinas \`print-properties\`, \`print-issues\`, \`compare\` sobre PWSZ real; fotos sem e com Unipega; controle de uniformidade e orientação das amostras.
**C. Próxima implementação de software (após medições):** biblioteca de curva \`I(G)\`, curvas de dose-vs-conversão, \`Dp\`, \`Ec\`, compensação longitudinal, e separação entre transporte UV de cura e transporte de luz visível.
**D. Nenhuma nova peça maciça deve ser enviada à impressora antes de confirmação de cura integral e efeitos ópticos persistentes.**
