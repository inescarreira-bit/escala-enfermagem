from datetime import datetime, timedelta
import holidays

def calcular_horas_trabalho_avancado(data_inicio_str, data_fim_str, horas_semanais=35, cod_pais="PT"):
    """
    Calcula as horas de trabalho necessárias num período, descontando fins de semana
    e feriados oficiais do país selecionado.
    """
    # 1. Conversão das datas de texto para objetos datetime
    data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
    data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
    
    if data_inicio > data_fim:
        raise ValueError("A data de início não pode ser posterior à data de fim.")

    # 2. Cálculo da carga horária diária padrão (semana de 5 dias)
    horas_diarias = horas_semanais / 5
    
    # 3. Inicializar o calendário de feriados do país (ex: Portugal "PT")
    anos_no_periodo = list(range(data_inicio.year, data_fim.year + 1))
    feriados_oficiais = holidays.CountryHoliday(cod_pais, years=anos_no_periodo)
    
    # Contadores
    dias_uteis = 0
    dias_fim_semana = 0
    lista_feriados_encontrados = []
    
    # 4. Iteração dia a dia no período selecionado
    data_atual = data_inicio
    while data_atual <= data_fim:
        # LINHA CORRIGIDA: Sábado é 5 e Domingo é 6. Se for maior ou igual a 5, é fim de semana.
        if data_atual.weekday() >= 5:
            dias_fim_semana += 1
        elif data_atual in feriados_oficiais:
            # Guarda o nome do feriado encontrado para o relatório
            nome_feriado = feriados_oficiais.get(data_atual)
            lista_feriados_encontrados.append(f"{data_atual.strftime('%d/%m/%Y')} - {nome_feriado}")
        else:
            dias_uteis += 1
            
        data_atual += timedelta(days=1)
        
    # 5. Cálculo do total de horas efetivas
    total_horas = dias_uteis * horas_diarias
    total_dias_calendario = (data_fim - data_inicio).days + 1
    
    # 6. Relatório formatado e limpo
    print("=" * 60)
    print(f"       RELATÓRIO DE HORAS DE TRABALHO - {cod_pais}")
    print("=" * 60)
    print(f" Período analisado:  {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    print(f" Total de dias:      {total_dias_calendario} dias de calendário")
    print(f" Carga horária:      {horas_semanais}h semanais ({horas_diarias:.1f}h/dia útil)")
    print("-" * 60)
    print(f" Fim de semanas:     {dias_fim_semana} dias")
    print(f" Feriados em dias:   {len(lista_feriados_encontrados)} dias")
    
    if lista_feriados_encontrados:
        for f in lista_feriados_encontrados:
            print(f"   • {f}")
            
    print(f" Dias de trabalho:   {dias_uteis} dias efetivos")
    print("-" * 60)
    print(f" TOTAL A TRABALHAR:  {total_horas:.1f} horas")
    print("=" * 60)

# ==========================================
# EXECUÇÃO DO EXEMPLO
# ==========================================
if __name__ == "__main__":
    calcular_horas_trabalho_avancado(
        data_inicio_str="2026-11-23", 
        data_fim_str="2026-12-20", 
        horas_semanais=35
    )
