# Aprofundamento — hardware, Anycubic Clear e variabilidade da cura (2026-11-21)

## Descoberta principal: GRIN/difratacao com resina ANYCUBIC na literatura
**Yizhuo Liu et al. (2026), Additive Manufacturing 105406, 25/08/2026**
DOI https://doi.org/10.1016/j.addma.2026.105406  
Pagina: https://www.sciencedirect.com/science/article/pii/S2214860426003325

Secao publicamente indexada "3D printer and resin" indica:
- Hardware **Phrozen Sonic Mini 8K** LCD 22 µm, portanto nao M7 Pro.
- Resina **Anycubic 3D printing UV-sensitive resin (clear)**, 405 nm, portanto nao a Standard Resin azul usada no LumaCore.
- Cortes no CHITUBOX a partir de modelo Fusion 360.
- O contraste de indice de refracao foi gerado predominantemente por **controle de tempo de exposicao local** em multiplas camadas, nao simplesmente uma unica mascara de grayscale menor em todas as camadas.
- O metodo compensa penetração UV nas camadas anteriores, usa multiplas exposicoes e planarizacao de interfaces por imersao em liquido casado em indice.
- Fez grades de Dammann e mascaras de fase; modelo inverso diferenciavel ligado a processo e resposta optica.
- Autores declararam um pedido provisório de patente. Isso e fato publicado, nao uma interpretacao de liberdade de operacao.

**Conclusao:** existe precedente com fabricante da resina que usamos, mas NAO em cor azul nem M7. O fato de usar Anycubic Clear justifica estudar essa formulacao como eventual MATERIAL REFERENCIA, sem trocar a resina do usuario ou mudar metas sem autorização.

## Livro de evidencias para UVtools
1. V7.1.2 pin na integracao: release oficial 26/10/2026, ZIP SHA-256 GitHub \`8ed807737242738c8772c966f8bd302a214764e439e1e24893fbf9b65a542f41\`. O downloader PowerShell foi escrito mas ainda nao testado em Windows.
2. Console UVtoolsCmd oferece \`print-properties\`, \`print-issues\`, \`compare\` oficialmente, nao chamadas inventadas. Documentacao https://github.com/sn4k3/UVtools/blob/master/README.md
3. Formato M7 Pro \`.pwsz\` encoda camadas como \`.pwszImg\` ou \`.pw0Img\` (revisao de discussao https://github.com/sn4k3/UVtools/discussions/892). Conservar metadata \`lcd_function.json\`; erros ja ocorreram em versoes antigas.
4. \`UVtools.Core\` e scripts externos sao AGPLv3: executavel oficial separado no runtime permite uso sem incorporar codigo no core LumaCore, sujeito aos termos de redistribuicao.

## O que os trabalhos sobre resina ajudam a medir
- Jacobs working curve: profundidade curada \`C_d = D_p ln(E/E_c)\`; \`D_p\` e \`E_c\` mudam com **comprimento de onda** e resina.
- Bennett et al., "Measuring UV Curing Parameters of Commercial Photopolymers used in Additive Manufacturing" (2017/2018): em cinco resinas testadas, alguns parametros variaram mais de 200% entre 365 e 405 nm; logo medir proprio \`D_p\` e \`E_c\` ao redor do UV da impressora. https://pmc.ncbi.nlm.nih.gov/articles/PMC5828039/
- A investigacao da Formlabs Clear e outras resinas NAO demonstra valores numericos para a Anycubic Standard Resin azul.
- Tu et al., *ACS Applied Optical Materials* (2025): modelos mostraram overshoot de conversao por exotermia e potenciais mudancas com temperatura e exposicao solar; lentes de teste no escuro mantiveram distancia focal estavel por 3 meses, sem provar estabilidade universal. https://doi.org/10.1021/acsaom.5c00143
- Jang et al. (2025) modificaram indice e absorcao na faixa **terahertz** por dose UV: \`n=1.65..1.80\` nessa faixa. **Nao usar valores THz para luz visivel ou para a resina azul**. https://doi.org/10.1016/j.optcom.2024.131262

## Encontramos pesquisa com ANYCUBIC HIGH CLEAR para fabricacao de lentes
**Christopher et al. (2024), "Exploration of 3D-printed lenses in a confocal MEMS microscope concept"**: LCD Phrozen Sonic Mini 8K S + Anycubic High Clear (n ≈ 1,50–1,51), pixel 22 µm, camadas 10 µm, filme difusor 0,1 mm entre tela e tanque e **spin-coating** com resina secundaria de indice proximo para obter superficie optica.
https://strathprints.strath.ac.uk/91803/1/Christopher-etal-IEEE-OMN-2024-Exploration-of-3D-printed-lenses-in-a-confocal-MEMS-microscope.pdf

Existe tambem pedido de patente US20260048562A1 para tecnica de spin-coating de lentes impressas com Anycubic High Clear e difusao da imagem LCD; nao assumir que direitos de uso comercial estao livres:
https://patents.google.com/patent/US20260048562A1/en

**Implicacao para Unipega:** a optica superficial da aplicacao comercial depende de indice de refracao do verniz, espessura, espalhamento e aderencia. O Unipega aprovado pode aumentar clareza visual, mas NAO e automaticamente index-matched como o spin-coating do estudo.

## Possivel metodologia de calibração sem medidor UV no inicio
1. Para comparar energia por tempo, explorar o arquivo **R_E_R_F.pwsz oficial M7 Pro** (8 regioes de tempo) e a calibracao de grayscale no UVtools. O RERF so demonstra a resposta a exposicao temporal e qualidade/adesao, **nao mede delta-n diretamente**.
2. Repetir a calibracao em artefatos **geometricamente identicos, marcados e randomizados na mesma plate**, com uma serie de exposicoes curtas e verificacao da cura interna.
3. **Antes da otimizacao inversa**, medir n ou desvio de frente de onda com instrumento confiavel ou ensaio comparativo de grid/laser com controle posicional; camera de celular so indica transmissao aparente, nao fase.
4. Separar resposta fisica \`UV 405 nm -> cura\` de resposta \`LED branco -> luz visivel\`.
5. Comparar transmitancia/espectro da Standard Resin azul com formulação Anycubic Clear como referencia APENAS se o usuario optar por investigar outro material; nao trocar a resina do projeto em silencio.
6. O PWSZ da M7 Pro grava \`lcd_function.json\` com blocos como \`rerf_function\`. Original de controle tem \`rerf_function.enable=false\`. Nao ligar esse flag sem reproduzir teste autorizado e validado.

## Limites e pendencias
- A curva radiometrica 15/14/13 nao foi medida na M7 Pro.
- O arquivo \`pwsz\` que imprimimos mostrou tonalidades no preview e criou uma amostra com padroes internos, mas nao sabemos se eles correspondem a \`∆n\` ou a scattering.
- O cupom ficou lavado e pos-curado. A pos-cura pode reduzir diferenças de conversao; o efeito GRIN nao esta estabelecido.
- A literatura com 2026 Anycubic Clear constitui progresso, nao validacao da resina azul.
- O potencial conflito de patente deve ser avaliado antes de qualquer comercializacao, nao impeditivo da pesquisa/estudo no repositorio.
