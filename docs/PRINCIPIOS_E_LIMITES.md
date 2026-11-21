# Principios de engenharia e limites experimentais

## Objetivo
Desenvolver microdosagem espacial da exposicao UV para alterar localmente resposta optica da resina translucida azul durante fabricacao MSLA. A otimizacao envolve a estatua inteira, NAO apenas o plinto. Priorizar rosto, maos, torso, silhueta e base cristalina de acordo com a composicao.

## Hipotese fisica
Variacoes de exposicao podem modificar grau de conversao e espalhamento/indice de refracao de uma resina; isto precisa ser caracterizado. O controle de grayscale por software nao demonstra indice de refracao graduado. Indice n(lambda), absortividade, espalhamento, espessura do filme Unipega e espectro do LED precisam ser medidos.

## Restrições de integridade
- Preservar o STL artistico original e a superficie externa sem deformacoes.
- Nenhuma nova ilha, cavidade estanque, bolsao de resina liquida ou fratura por subcura.
- Manter pixels de fundo desligados; nao desligar pixels internos previamente ligados.
- Conservar margem externa da mascara intacta.
- Nao tratar uma checagem `is_watertight` como auditoria suficiente da malha: checar orientacao, validade volumetrica e autointersecoes.
- Sem afirmar ganho optico sem comparacao com controles e medicoes.
- Sem inferir comportamento real do LCD a partir de tons de cinza no preview.

## Resultados preliminares de modelo
Estudo hipotetico da geometria original (150 mm de altura, ~1,6M triangulos, ~386,6 cm3) indicou que a base cristalina domina a fuga luminosa nas condicoes simuladas. O resultado nao e uma calibracao do material; simulacao nao prova que um padrao de microdosagem melhorara a iluminacao do rosto.

## Caminho de validacao
1. Cupons controle e com microdosagem, com base/pos-cura equivalentes.
2. Checagem da integridade mecanica/quimica, sem resina liquida encapsulada.
3. Medicao radiometrica/fotografica: mesma fonte USB e geometria de acoplamento, camera manual sem ajustes automaticos.
4. Comparacao antes/depois do Unipega, somente apos secagem completa.
5. Recalibracao e validacao de hipoteses contra medidas.
6. Somente entao projetar e verificar um arquivo nativo PWSZ da estatua inteira.
