# LumaCore — primeira medição fotográfica do cupom impresso

Data: 2026-11-21. Amostra: cupom de dose Anycubic M7 Pro em resina azul translúcida, perfil Standard Resin / ACF / 0,050 mm / 1,800 s. O usuário informou que a amostra foi lavada e pós-curada. Sem Unipega neste teste. Fotos: IMG_0060.jpeg (horizontal), IMG_0059.jpeg (vertical), recebidas na conversa.

## Método

As fotografias mostram a máscara preta ScanNCut de três janelas, sobre a amostra iluminada por trás. Amostragem numérica de pixels JPEG RGB em regiões internas centrais de 80 x 80 pixels, longe das bordas desfocadas; luminosidade codificada estimada por `Y' = 0.2126 R + 0.7152 G + 0.0722 B`. A escala é 0–255, não linear e **não deve ser chamada de transmitância, irradiância ou potência óptica**. Não há confirmação independente de que exposição ISO, obturador, processamento HDR, balanço de branco e brilho da tela foram fixados.

## Dados

| Foto | Janela | RGB médio | Luminância codificada Y' aproximada | Relativo ao centro |
|---|---|---|---:|---:|
| IMG_0060 horizontal | Esquerda | 134.3, 210.2, 210.7 | 194.1 | 89,0% |
| IMG_0060 horizontal | Centro | 156.9, 234.2, 237.4 | 218.0 | 100% |
| IMG_0060 horizontal | Direita | 147.4, 227.9, 230.6 | 211.0 | 96,8% |
| IMG_0059 vertical | Superior | 150.5, 224.6, 226.4 | 209.0 | 99,8% |
| IMG_0059 vertical | Centro | 146.6, 226.1, 229.7 | 209.5 | 100% |
| IMG_0059 vertical | Inferior | 127.2, 202.3, 202.8 | 186.4 | 89,0% |

Foram examinadas ROIs menores/maiores (40, 80, 120 px); a tendência de uma extremidade mais escura permanece.

## Interpretação

Uma extremidade do cupom se apresenta cerca de **10% mais escura no sinal de brilho codificado do JPEG**, relativo ao centro em ambas as tomadas, após a mudança de orientação. Há variação espacial aparente reprodutível, mas:

- As três faixas digitais (15/15, 14/15, 13/15) **não estão associadas de modo seguro às extremidades reais da amostra**, porque o cupom não tem marca de orientação de impressão.
- Variações de espessura local, posição na tela, textura e geometria superficial, luz de fundo, exposição automática e processamento da câmera ainda podem explicar diferenças.
- Uma diferença fotográfica **não demonstra** modulação intencional do índice de refração, nem guia óptico, nem segurança de cura em toda a seção.
- As três regiões não apresentam uma sequência monotônica simples de intensidade.
- A fonte, a lente e o processamento cromático tornam estes números inadequados para converter diretamente em transmitância.

## Próximo teste de controle simples

Sem mover o iPad nem a máscara, **rotacionar somente o cupom 180° no plano** e recolocá-lo centralizado; fotografar de cima novamente, sem flash. Se a região escura trocar de janela, o contraste provavelmente acompanha a peça; se permanecer na mesma janela, provavelmente acompanha iluminação/posição. Sempre manter o Unipega fora até conclusão do controle.

## Status

**Primeira observação fotográfica com diferença detectável, mecanismo físico não demonstrado.** A pesquisa continua experimental.
