# UVtools portatil integrado ao Silicon Forge LumaCore

## O que foi integrado

- **UVtools 7.1.2** (publicado em 2026-10-26), versao Windows x64 **portable ZIP**, diretamente do release oficial. Nao usa Winget, Chocolatey, instalador MSI ou configuracao global.
- **Download automatico na primeira execucao**, para \`runtime/uvtools/downloads\` com verificacao de SHA-256 ANTES da extracao.
- **Extracao local** para \`runtime/uvtools/v7.1.2\`. Arquivos temporarios, perfis do processo e logs sao direcionados a \`runtime/\`.
- Interface grafica normal, auditoria de propriedades/issues e comparacao de dois arquivos PWSZ.
- Guardas de integridade: os comandos de auditoria sao **somente leitura** e calculam SHA-256 do original antes/depois. Nao chama "repair", "run", "convert" ou "save" automaticamente.
- Codigo de integracao proprIo (PowerShell); o binario original UVtools **nao foi commitado** no GitHub. O primeiro uso exige rede para baixar o ZIP oficial.
- Os avisos AGPL-3.0 e os arquivos fornecidos pelo autor ficam com a distribuicao original.

### Abrir pela primeira vez (Windows)

Abra [INSTALAR_UVTOOLS.bat](INSTALAR_UVTOOLS.bat) ou execute [ABRIR_UVTOOLS.bat](ABRIR_UVTOOLS.bat). O ZIP oficial (aproximadamente 122 MiB) sera obtido automaticamente. Nao e necessario instalar Python ou .NET globalmente para usar o pacote Windows x64 distribuido pelo autor.

**Para abrir arquivo de impressao:** arraste um \`.pwsz\` para \`ABRIR_UVTOOLS.bat\`.

**Para auditar sem modificar o original:** arraste um \`.pwsz\` para \`AUDITAR_PWSZ.bat\`. O programa executa:
1. \`UVtoolsCmd print-properties arquivo.pwsz\`
2. \`UVtoolsCmd print-issues arquivo.pwsz\`
3. Compara hashes SHA-256 antes/depois.
4. Grava resultados em \`runtime/logs/uvtools/\`.

**Comparar dois arquivos:**
\`\`\`bat
COMPARAR_PWSZ.bat "C:\Impressao\cupom_original.pwsz" "C:\Impressao\cupom_microdose.pwsz"
\`\`\`

**Na interface gráfica:** abra e percorra camadas, use os validadores de impressao (ilhas, resin traps, overhangs), compare contornos e valores de grayscale. Se desejar alterar algo, sempre trabalhe numa **copia com nome novo**. O launcher de auditoria nao altera arquivos.

## Integridade e reproducibilidade

| Propriedade | Valor |
|---|---|
| Fonte | https://github.com/sn4k3/UVtools/releases/tag/v7.1.2 |
| Artifact | \`UVtools_win-x64_v7.1.2.zip\` |
| Versao fixada | 7.1.2 (sem "latest" silencioso) |
| SHA-256 oficial | \`8ed807737242738c8772c966f8bd302a214764e439e1e24893fbf9b65a542f41\` |
| Tamanho ZIP | 127.583.593 bytes |
| Licenca do UVtools | AGPL-3.0 |
| Sistema alvo | Windows x64 |
| Local dos downloads/extracao | \`runtime/uvtools\` (ignorado pelo Git) |
| Logs e arquivos temporarios | \`runtime/logs/uvtools\`, \`runtime/tmp/uvtools\` |

A versao e hash foram confirmados no manifesto oficial de release do GitHub. **Validacao realizada:** GitHub Actions Windows runner baixou o pacote oficial, conferiu SHA-256, extraiu, localizou UVtools.exe, executou o comando de versao e gerou logs com sucesso: https://github.com/llioncourt/Silicon-Forge-LumaCore/actions/runs/44934364389 . **Ainda nao testado no computador do usuario nem auditado um PWSZ real no runner.** O primeiro uso local precisa de acesso ao dominio GitHub e nao constitui instalacao offline.

O wrapper modifica variaveis TEMP, TMP, APPDATA, LOCALAPPDATA e DOTNET_CLI_HOME apenas no seu processo e filhos. Pode haver preferencias adicionais armazenadas pelo proprio Windows/UVtools fora da arvore do app; isso nao foi verificado. Nenhuma instalacao global e realizada pelo wrapper.

### Erros

- Falhou download: verifique internet, bloqueios de rede e o \`runtime/logs/uvtools/bridge.log\`.
- Falhou hash: ZIP descartado; nao sera executado.
- UVtools detectou defeito no arquivo: o log \`..._issues.log\` indica o problema. **Nao reparar automaticamente.**
- Photon Workshop rejeitou PWSZ: versoes antigas do UVtools tiveram regressoes especificas M7 Pro (#1108, #1155). A versao fixada inclui as correcoes documentadas. Isso nao dispensa teste real no Photon Workshop e na propria impressora.
- UVtools falhou com codigo nao zero: o script para e deixa o arquivo intacto.

## Integracao na metodologia LumaCore

\`\`\`text
Photon Workshop original.pwsz
            |
            v
LumaCore: modificar uma COPIA (nunca sobrescrever)
            |
            v
UVtools: print-properties + print-issues + compare
            |
            v
Checagem independente de mascaras / grayscale / checksum
            |
            v
Photon Workshop: abrir e inspecionar camadas
            |
            v
Validacao material: M7 Pro + Standard Resin azul + Unipega
\`\`\`

**UVtools nao cria automaticamente um mapa GRIN:** validacao de arquivos é uma etapa, e nao prova de potencia UV real, resposta espectral do material, dose acumulada ou controle de trajetoria da luz.

## Codigo de terceiros

UVtools foi criado por Tiago M. F. Conceicao e colaboradores, distribuido sob **GNU AGPL v3**. O LumaCore faz download oficial sob demanda; nao altera o UVtools nesta integracao. A incorporacao direta de partes de \`UVtools.Core\` no software LumaCore exigiria revisao de compatibilidade de licencas e atendimento aos avisos de origem, publicacao de codigo e termos de redistribuicao.

Fontes: https://github.com/sn4k3/UVtools/blob/master/README.md, https://github.com/sn4k3/UVtools/blob/master/LICENSE, https://github.com/sn4k3/UVtools/releases/tag/v7.1.2
