import re
import unicodedata
from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import UploadFile

from app.entities.report import ReportInDTO, ReportFilters, ReportInfoOutDTO, Metric, Section
from app.exceptions.invalid_file_type_exception import InvalidFileTypeException
from app.exceptions.locale_not_found_exception import LocaleNotFoundException
from app.exceptions.profissional_not_found_exception import ProfissionalNotFoundException


class GetReportInfoService:

    def execute(self, report_in_dto: ReportInDTO) -> ReportInfoOutDTO:
        self.__raise_if_file_is_invalid(report_in_dto.file)
        sheets = self.process_xlsx(report_in_dto.file)
        report_info_out_dto = self.get_metrics(sheets, report_in_dto.filters)
        return report_info_out_dto

    @staticmethod
    def __raise_if_file_is_invalid(file: UploadFile):
        if file.headers['content-type'] != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            raise InvalidFileTypeException

    @staticmethod
    def process_xlsx(file: UploadFile) -> dict[Any, pd.DataFrame]:
        file.file.seek(0)
        contents = file.file.read()
        excel_io = BytesIO(contents)
        sheets = pd.read_excel(excel_io, sheet_name=None)
        for nome_planilha, df in sheets.items():
            col_cpf = [col for col in df.columns if 'CPF' in col]
            if col_cpf:
                cpf_col_name = col_cpf[0]
                sheets[nome_planilha][cpf_col_name] = df[cpf_col_name].astype(str).str.zfill(11)
        return sheets

    def get_metrics(self, sheets: dict[Any, pd.DataFrame], filters: ReportFilters) -> ReportInfoOutDTO:
        if filters.type == 'REGIONAL':
            return ReportInfoOutDTO(
                title=f'Relatório Municipal - {filters.value.split("|")[1].title()}/{filters.value.split("|")[0].upper()}',
                sections=self.get_metrics_regional(sheets, filters.value)
            )
        else:
            return ReportInfoOutDTO(
                title=f'Relatório do(a) Médico(a)',
                sections=self.get_metrics_profissional(sheets, filters.value.upper())
            )

    def get_metrics_regional(self, sheets, filter_value) -> list[Section]:
        estado = str(filter_value.split('|')[0]).upper()
        municipio = self.remove_accents(str(filter_value.split('|')[1])).upper()
        regiao = sheets["MQI_Municipios_CGPLAD"][sheets["MQI_Municipios_CGPLAD"]["UF"] == estado]["Região"].iloc[0]

        df_regiao = sheets["MQI_Municipios_CGPLAD"][sheets["MQI_Municipios_CGPLAD"]["Região"] == regiao]
        quantidade_de_estados_regiao = df_regiao["UF"].nunique()
        populacao_total_regiao = df_regiao["População 2021"].sum()
        profissionais_totais_regiao = df_regiao["Total de vagas ocupadas"].sum()

        df_estado = sheets["MQI_Municipios_CGPLAD"][sheets["MQI_Municipios_CGPLAD"]["UF"] == estado]
        populacao_total_estado = df_estado["População 2021"].sum()
        profissionais_totais_estado = df_estado["Total de vagas ocupadas"].sum()
        potencial_cobertura_estado = df_estado["Potencial de cobertura da população pelo Programa "].sum()
        quantidade_de_municipios_estado = df_estado["Município"].nunique()
        total_municipios_contemplatos_estado = df_estado[df_estado["Total de vagas ocupadas"] > 0]["Município"].nunique()
        percentual_municipios_contemplados_estado = (total_municipios_contemplatos_estado / quantidade_de_municipios_estado * 100)
        percentual_potencial_cobertura_estado = (potencial_cobertura_estado / populacao_total_estado * 100)

        df_municipio = sheets["MQI_Municipios_CGPLAD"][
            (sheets["MQI_Municipios_CGPLAD"]["UF"] == estado) &
            (sheets["MQI_Municipios_CGPLAD"]["Município"] == municipio)
        ]

        if df_municipio.empty:
            raise LocaleNotFoundException

        populacao_total_municipio = df_municipio["População 2021"].sum()
        profissionais_totais_municipio = df_municipio["Total de vagas ocupadas"].sum()
        potencial_cobertura_municipio = df_municipio["Potencial de cobertura da população pelo Programa "].sum()
        vulnerabilidade_social_municipio = df_municipio["Categoria de IVS"].unique().tolist()[0]
        percentual_potencial_cobertura_municipio = (potencial_cobertura_municipio / populacao_total_municipio * 100)

        return [
            Section(name=f"Região: {regiao}", metrics=[
                Metric(metric="Quantidade de estados", value=quantidade_de_estados_regiao),
                Metric(metric="População total", value=self.format_number(populacao_total_regiao)),
                Metric(metric="Quantidade de profissionais do PMMB", value=self.format_number(profissionais_totais_regiao))
            ]),
            Section(name=f"Estado: {self.get_nome_estado_by_sigla(estado)}", metrics=[
                Metric(metric="Quantidade de municípios", value=quantidade_de_municipios_estado),
                Metric(metric="Municípios que possuem no mínimo 1 médico",
                       value=f"Total: {total_municipios_contemplatos_estado} ({percentual_municipios_contemplados_estado: .2f}%)"),
                Metric(metric="População total", value=self.format_number(populacao_total_estado)),
                Metric(metric="Total de profissionais do PMMB", value=self.format_number(profissionais_totais_estado)),
                Metric(metric="Potencial de cobertura dos médicos do PMMB",
                       value=f"Total: {self.format_number(potencial_cobertura_estado)} ({percentual_potencial_cobertura_estado: .2f}%)")
            ]),
            Section(name=f"Município: {municipio.title()}", metrics=[
                Metric(metric="População total", value=self.format_number(populacao_total_municipio)),
                Metric(metric="Total de profissionais do PMMB", value=profissionais_totais_municipio),
                Metric(metric="Potencial de cobertura dos médicos do PMMB",
                       value=f"Total: {self.format_number(potencial_cobertura_municipio)} ({percentual_potencial_cobertura_municipio: .2f}%)"),
                Metric(metric="Índice de vulnerabilidade social", value=str(vulnerabilidade_social_municipio))
            ])
        ]

    def get_metrics_profissional(self, sheets, filter_value) -> list[Section]:
        cpf = filter_value
        df_profissional = sheets["MQI_Monitoramento_PMMB"][sheets["MQI_Monitoramento_PMMB"]["CPF"] == cpf]

        if df_profissional.empty:
            raise ProfissionalNotFoundException

        municipio_profissional = df_profissional['Municipio/DSEI'].iloc[0]
        estado_profissional = df_profissional['UF'].iloc[0]
        df_estado = sheets["MQI_Municipios_CGPLAD"][sheets["MQI_Municipios_CGPLAD"]["UF"] == estado_profissional]
        profissionais_totais_estado = df_estado["Total de vagas ocupadas"].sum()
        df_municipio = sheets["MQI_Municipios_CGPLAD"][
            (sheets["MQI_Municipios_CGPLAD"]["UF"] == estado_profissional) &
            (sheets["MQI_Municipios_CGPLAD"]["Município"] == self.remove_accents(municipio_profissional).upper())
        ]
        profissionais_totais_municipio = df_municipio["Total de vagas ocupadas"].sum()

        cpf_profissional = df_profissional['CPF'].iloc[0]
        nome_profissional = df_profissional['Nome do Médico ATIVO'].iloc[0]
        ciclo_profissional = df_profissional['Ciclo'].iloc[0]
        perfil_profissional = df_profissional['Perfil do Médico'].iloc[0]
        foi_para_maav = "NÃO"
        if perfil_profissional.strip().upper() == "INTERCAMBISTA" or perfil_profissional.strip().upper() == "RMS":
            df_maav = sheets["LOG_Maav"]
            df_maav_filtrado = df_maav[df_maav["CPF"] == cpf]
            if not df_maav_filtrado.empty:
                resposta_maav = df_maav_filtrado["FOI PARA O MAAv?"].iloc[0]
                if isinstance(resposta_maav, str) and resposta_maav.strip().upper() == "SIM":
                    foi_para_maav = "SIM"
            perfil_profissional += f' - Foi para o MAAv? {foi_para_maav}'

        sexo_profissional = df_profissional['Gênero'].iloc[0]
        idade_profissional = str(df_profissional['Idade'].iloc[0])
        raca_cor_profissional = df_profissional['Raça / cor'].iloc[0]
        nacionalidade_profissional = df_profissional['Nacionalidade'].iloc[0]

        inicio_atividades_dt = df_profissional['Início das Atividades'].iloc[0]
        fim_atividades_dt = df_profissional['Fim das Atividades'].iloc[0]

        inicio_atividades = inicio_atividades_dt.strftime("%d/%m/%Y") if isinstance(inicio_atividades_dt,
                                                                                    datetime) else str(
            inicio_atividades_dt)
        if isinstance(fim_atividades_dt, datetime):
            if fim_atividades_dt > datetime.now():
                fim_atividades = fim_atividades_dt.strftime("%d/%m/%Y") + ' (previsão)'
            else:
                fim_atividades = fim_atividades_dt.strftime("%d/%m/%Y")
        else:
            fim_atividades = str(fim_atividades_dt)

        df_erario = sheets["ERA_Erario"]
        df_erario_filtrado = df_erario[df_erario["CPF"] == cpf]
        if df_erario_filtrado.empty:
            teve_erario_profissional = 'NÃO'
        else:
            teve_erario_profissional = (
                "SIM" if not df_erario_filtrado.empty and df_erario_filtrado["NECESSÁRIA RESTITUIÇÃO? S/N"].iloc[0] == "SIM"
                else "NÃO"
            )
        metrics_erario = [Metric(metric="Teve erário?", value=teve_erario_profissional)]
        if teve_erario_profissional == 'SIM':
            metrics_erario.append(Metric(metric="Motivo", value="DESLIGAMENTO"))

        especializacao_profissional = df_profissional['Oferta Formativa\nAtual 11/04/2025'].iloc[0]
        instituicao_ensino_especializacao = \
        df_profissional['Instituição de Ensino Superior\nque o Profissional está Vinculado'].iloc[0]

        df_lic_med = sheets["LIC_Licencas_Medicas"]
        df_lic_med_filtrado = df_lic_med[df_lic_med["CPF"] == cpf]

        metrics_licenca = []
        licencas_medicas_profissional = [
            {
                "tipo": "MÉDICA",
                "inicio": row["INICIO DA LICENÇA MÉDICA"],
                "fim": row["TERMINO DA LICENÇA MÉDICA"]
            }
            for _, row in df_lic_med_filtrado.iterrows()
        ]

        df_lic_parental = sheets["LIC_Matern_Patern"]
        df_lic_parental_filtrado = df_lic_parental[df_lic_parental["CPF"] == cpf]
        licencas_parental_profissional = [
            {
                "tipo": row["Tipo de Licença"],
                "inicio": row["INÍCIO DA LICENÇA"]
            }
            for _, row in df_lic_parental_filtrado.iterrows()
        ]

        for licenca_medica in licencas_medicas_profissional:
            inicio = licenca_medica['inicio'].strftime('%d/%m/%Y') if isinstance(licenca_medica['inicio'],
                                                                                 datetime) else str(
                licenca_medica['inicio'])
            fim = licenca_medica['fim'].strftime('%d/%m/%Y') if isinstance(licenca_medica['fim'], datetime) else str(
                licenca_medica['fim'])
            metrics_licenca.append(Metric(metric=licenca_medica['tipo'], value=f"{inicio} - {fim}"))

        for licenca_parental in licencas_parental_profissional:
            inicio = licenca_parental['inicio'].strftime('%d/%m/%Y') if isinstance(licenca_parental['inicio'],
                                                                                   datetime) else str(
                licenca_parental['inicio'])
            metrics_licenca.append(Metric(metric=licenca_parental['tipo'], value=inicio))

        df_avaliacoes = sheets["PED_AvaliaMaisMedicos"]
        df_avaliacoes_filtrado = df_avaliacoes[df_avaliacoes["CPF (Médico)"] == cpf]

        if df_avaliacoes_filtrado.empty:
            profissional_avaliado = "NÃO"
            avaliacoes_profissional = []
        else:
            profissional_avaliado = "SIM"
            avaliacoes_profissional = [
                {
                    "tipo": row["Tipo Avaliação"],
                    "nota": row["Nota Final"]
                }
                for _, row in df_avaliacoes_filtrado.iterrows()
            ]
        metrics_avaliacoes = [Metric(metric="Foi avaliado?", value=profissional_avaliado)]
        if profissional_avaliado == "SIM":
            metrics_avaliacoes.append(Metric(metric="Ano da avaliação", value="2024"))
            for avaliacao in avaliacoes_profissional:
                metrics_avaliacoes.append(Metric(metric=f"Nota - {avaliacao['tipo']}", value=str(avaliacao['nota'])))

        df_processos = sheets["NGA_ProcessosCGPP"]
        df_processos_filtrado = df_processos[df_processos["CPF"] == cpf]

        if df_processos_filtrado.empty:
            tem_processo_administrativo = "NÃO"
            processos_administrativos_profissional = []
        else:
            tem_processo_administrativo = "SIM"
            processos_administrativos_profissional = []
            for _, row in df_processos_filtrado.iterrows():
                causas = [row["CAUSA 1"], row["CAUSA 2"], row["CAUSA 3"]]
                causas_limpa = [c.strip() for c in causas if isinstance(c, str) and c.strip() != "-" and c.strip()]
                causas_str = ", ".join(causas_limpa)
                processos_administrativos_profissional.append({
                    "categoria": row["CATEGORIA"],
                    "causas": causas_str
                })

        metrics_processos_adm = [
            Metric(metric="Profissional possui processos?", value=tem_processo_administrativo)]
        for processo_adm in processos_administrativos_profissional:
            metrics_processos_adm.append(Metric(metric=processo_adm['categoria'], value=processo_adm['causas']))

        return [
            Section(name="Dados do profissional", metrics=[
                Metric(metric="CPF", value=self.hide_cpf(cpf_profissional)),
                Metric(metric="Nome completo", value=nome_profissional),
                Metric(metric="Ciclo", value=ciclo_profissional),
                Metric(metric="Perfil", value=perfil_profissional),
                Metric(metric="Sexo", value=sexo_profissional),
                Metric(metric="Idade", value=idade_profissional),
                Metric(metric="Raça/cor", value=raca_cor_profissional),
                Metric(metric="Município", value=municipio_profissional + "/" + estado_profissional),
                Metric(metric="Nacionalidade", value=nacionalidade_profissional)
            ]),
            Section(name="Período de exercício das atividades", metrics=[
                Metric(metric="Início", value=inicio_atividades),
                Metric(metric="Fim", value=fim_atividades),
            ]),
            Section(name="Licenças", metrics=metrics_licenca),
            Section(name="Erário", metrics=metrics_erario),
            Section(name="Situação acadêmica", metrics=[
                Metric(metric="Especialização", value=str(especializacao_profissional)),
                Metric(metric="Instituição de ensino", value=str(instituicao_ensino_especializacao))
            ]),
            Section(name="Avaliação do profissional", metrics=metrics_avaliacoes),
            Section(name="Processos", metrics=metrics_processos_adm),
            Section(name="Dados Gerais", metrics=[
                Metric(metric=f"Total de profissionais no estado: {estado_profissional}",
                       value=str(profissionais_totais_estado)),
                Metric(metric=f"Total de profissionais no município: {municipio_profissional}",
                       value=str(profissionais_totais_municipio))
            ]),
        ]

    @staticmethod
    def hide_cpf(cpf):
        cleaned_cpf = re.sub(r'\D', '', str(cpf))
        if len(cleaned_cpf) == 11:
            return f"XXX.{cleaned_cpf[3:6]}.XXX-{cleaned_cpf[9:]}"
        return cpf
    
    import unicodedata

    @staticmethod
    def remove_accents(text: str) -> str:
        normalized_text = unicodedata.normalize('NFD', text)
        return ''.join(char for char in normalized_text if unicodedata.category(char) != 'Mn')

    @staticmethod
    def format_number(numero) -> str:
        try:
            numero = float(str(numero).replace(',', '.'))
        except ValueError:
            return "Número inválido"
        if numero.is_integer():
            return f"{int(numero):,}".replace(",", ".")
        else:
            inteiro, decimal = f"{numero:.2f}".split(".")
            inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
            return f"{inteiro_formatado},{decimal}"

    @staticmethod
    def get_nome_estado_by_sigla(sigla: str) -> str | None:
        estados = {
            "AC": "Acre",
            "AL": "Alagoas",
            "AP": "Amapá",
            "AM": "Amazonas",
            "BA": "Bahia",
            "CE": "Ceará",
            "DF": "Distrito Federal",
            "ES": "Espírito Santo",
            "GO": "Goiás",
            "MA": "Maranhão",
            "MT": "Mato Grosso",
            "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais",
            "PA": "Pará",
            "PB": "Paraíba",
            "PR": "Paraná",
            "PE": "Pernambuco",
            "PI": "Piauí",
            "RJ": "Rio de Janeiro",
            "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul",
            "RO": "Rondônia",
            "RR": "Roraima",
            "SC": "Santa Catarina",
            "SP": "São Paulo",
            "SE": "Sergipe",
            "TO": "Tocantins"
        }
        sigla = sigla.strip().upper()
        return estados.get(sigla, None)
