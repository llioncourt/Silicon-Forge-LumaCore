# UVTools-Scripts — código de terceiros (AGPL-3.0)

## Origem e licença

- Projeto de origem: https://github.com/aaron1138/UVTools-Scripts
- Titular/repositório: [aaron1138](https://github.com/aaron1138)
- Licença disponibilizada pelo autor: **GNU Affero General Public License, versão 3**.
- Licença original copiada integralmente em [LICENSE](LICENSE).
- Os scripts nesta pasta foram copiados **sem modificações** da branch `main` do projeto de origem em 2026-11-21.
- Os scripts foram arquivados separadamente para estudo, comparação e futura integração. **Não estão acoplados automaticamente ao executável nem ao pipeline Python do LumaCore**.

## Arquivos preservados

| Arquivo | SHA Git original | Aplicação em estudo |
| --- | --- | --- |
| `scripts/ApplyLUTandFSDithering.cs` | `25a9b6c96e9de1efb7aa3ac13073e76bf76d2f0d` | LUT e dithering em cinza corrigido por gamma |
| `scripts/ExposureCalibrationMasking.cs` | `20548085193857d14f6dbbb1b7dd7a96e68f2b54` | Particionamento de exposições para calibração |
| `scripts/VerticalSuperSampler-LUT-FSDithering.cs` | `8a75b52f9bcccce6d139902f9d19ba1a748befd0` | Superamostragem Z, LUT e quantização |

## Limites operacionais e científicos

Esses scripts são desenvolvidos para a API de **scripting do UVtools**, não para rodar sozinhos num Python portátil. A técnica do autor busca principalmente suavização de geometria/AA por cura parcial, e não demonstra fabricação de guias de onda GRIN em resina azul translúcida. Os valores pré-definidos de gamma/LUT são provenientes de outras impressoras e materiais, portanto **não são calibração da Anycubic Photon Mono M7 Pro**.

Não imprimir arquivos obtidos com multi-exposição na mesma altura Z antes de confirmar que o firmware suporta a sequência e o movimento de plataforma. O arquivo `.pwsz` atual não é prova de dose radiométrica calibrada.

## Condições de reutilização

A AGPL-3.0 permite acesso, cópia, modificação e redistribuição conforme sua licença, sem autorização individual separada. Ao modificar/redistribuir versões derivadas, observar avisos, disponibilização de código-fonte e demais condições da AGPL. A inclusão destes arquivos não deve ser interpretada como relicenciamento automático dos módulos independentes do LumaCore; se forem integrados num programa combinado, será necessário determinar e cumprir as obrigações de licenciamento desse programa. Se o futuro LumaCore precisar ser distribuído sob uma licença incompatível, procurar uma autorização/licença alternativa do detentor dos direitos ou reimplementar independentemente.

Consulte também o código/README dos autores e a licença: https://www.gnu.org/licenses/agpl-3.0.html
