import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="SmartCalc",  # Título da página
    page_icon="🧮",  # Ícone de calculadora
    layout="wide",  # Layout da página (wide ou centered)
    initial_sidebar_state="expanded",  # Estado inicial da barra lateral
)

if 'oxigenoterapia' not in st.session_state:
    st.session_state.oxigenoterapia = {}
if 'forca_inspiratoria' not in st.session_state:
    st.session_state.forca_inspiratoria = {}
if 'ventilacao_mecanica' not in st.session_state:
    st.session_state.ventilacao_mecanica = {}



def calculate_height_chumlea(gender, age, aj):
    if gender == "Homem":
        return 64.19 - (0.04 * age) + (2.02 * aj)
    else:
        return 84.88 - (0.24 * age) + (1.83 * aj)

def calculate_ideal_weight(gender, height):
    if gender == "Homem":
        return 50 + 0.91 * (height - 152.4)
    else:
        return 45.5 + 0.91 * (height - 152.4)

def calculate_time_constant(rva, cst):
    return (rva * cst) / 1000

def calculate_driving_pressure(plateau_pressure, peep):
    return plateau_pressure - peep

def calculate_static_compliance(tidal_volume, plateau_pressure, peep):
    return tidal_volume / (plateau_pressure - peep)

def calculate_resistance(peak_pressure, plateau_pressure, flow):
    return (peak_pressure - plateau_pressure) / flow

def calculate_mechanical_power(fr, vc, ppico, dp):
    return 0.098 * fr * vc * (ppico - dp / 2)

def calculate_muscular_pressure(delta_pocc):
    return delta_pocc * 0.75

def calculate_irrs(fr, vt):
    return fr / vt

def calculate_predicted_pimax(gender, age):
    if gender == "Homem":
        return 155.3 - (0.80 * age)
    else:
        return 110.4 - (0.49 * age)

def calculate_predicted_pemax(gender, age):
    if gender == "Homem":
        return 165.3 - (0.81 * age)
    else:
        return 115.6 - (0.61 * age)

def calculate_rox_index(spo2, fio2, fr):
    return (spo2 / fio2) / fr

def calculate_pao2_fio2(pao2, fio2):
    """
    Calcula a relação PaO2/FiO2.

    Parâmetros:
        pao2 (float): Pressão arterial de oxigênio (PaO2).
        fio2 (float): Fração inspirada de oxigênio (FiO2).

    Retorna:
        float: Relação PaO2/FiO2 calculada.
        str: Mensagem de erro, caso os valores sejam inválidos.
    """
    try:
        # Verifica se PaO2 e FiO2 são válidos
        if pao2 is None or fio2 is None:
            return None, "Os valores de PaO2 e FiO2 não podem estar vazios."
        if fio2 <= 0:
            return None, "O valor de FiO2 deve ser maior que zero."

        # Calcula a relação PaO2/FiO2
        relacao = pao2 / fio2
        return relacao, None
    except Exception as e:
        return None, f"Ocorreu um erro: {str(e)}"


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

    /* Configurações gerais */
    body {
        font-family: 'Roboto', sans-serif;
    }

    /* Layout responsivo */
    .main {
        padding-top: 10px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }

    /* Sidebar estilizada */
    [data-testid="stSidebar"] {
        background-color: #f0f4f7;
        color: #333333;
        border-right: 1px solid #e0e0e0;
    }
    [data-testid="stSidebar"] * {
        color: #004080 !important;
    }
    [data-testid="stSidebar"] a {
        color: #007BFF !important;
        text-decoration: none;
    }
    [data-testid="stSidebar"] a:hover {
        color: #0056b3 !important;
        text-decoration: underline;
    }

    /* Header com gradiente */
    .header {
        background: linear-gradient(to right, #09184D, #004080);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-family: 'Roboto', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header com gradiente
st.markdown(
    """
    <style>
    .header {
        background-color: #333333; /* Cor de fundo alterada */
    }
    </style>
    <div class="header">
        <h1>Facilite sua Análise</h1>
        <p>Cálculos práticos e rápidos no seu atendimento</p>
    </div>
    """,
    unsafe_allow_html=True
)


st.sidebar.title("Menu")

# Abas para organizar as fórmulas
menu = st.sidebar.radio(
    "Escolha uma categoria:",
    ("Oxigenoterapia de Alto Fluxo", "Força Muscular Respiratória", "Ventilação Mecânica")
)
st.text("")

if menu == "Oxigenoterapia de Alto Fluxo":
    # Centralizando o título
    st.markdown(
        """
        <h2 style="text-align: center;">Oxigenoterapia de Alto Fluxo</h2>
        """,
        unsafe_allow_html=True
    )
    col1 = st.columns([1])[0]

    with col1:
        left_spacer, col1, right_spacer = st.columns([0.25, 0.5, 0.25])  # Centraliza e ajusta largura
        with col1:
            st.subheader("ROX Index")
            with st.expander("ℹ️  Fórmula    "):
                st.write(""" (SpO2 / FiO2)/ FR
                       """)

            # Campo SpO2 com opção de vazio
            spo2_options = [""] + list(range(0, 101))  # Opções de SpO2: vazio e números inteiros de 0 a 100
            spo2 = st.selectbox(
                "SpO2 (%):",
                options=spo2_options,
                format_func=lambda x: "" if x == "" else x,  # Exibe "Selecione" para vazio
                key="rox_spo2"
            )

            # Campo FiO2 com opção de vazio
            fio2_options = [""] + [round(i * 0.01, 2) for i in range(21, 101)]
            fio2 = st.selectbox(
                "FiO2 (fração):",
                options=fio2_options,
                format_func=lambda x: "" if x == "" else x,  # Exibe "Selecione" para vazio
                key="rox_fio2"
            )

            # Campo Frequência Respiratória com opção de vazio
            fr_rox_options = [""] + list(range(0, 101))
            fr_rox = st.selectbox(
                "Frequência Respiratória (FR):",
                options=fr_rox_options,
                format_func=lambda x: "" if x == "" else x,  # Exibe "Selecione" para vazio
                key="rox_fr"
            )

            # Botão para calcular
            if st.button("Calcular", key="rox_button"):
                if spo2 == "" or fio2 == "" or fr_rox == "":
                    st.error("Por favor, preencha todos os campos antes de calcular.")
                else:
                    rox_index = calculate_rox_index(spo2, fio2, fr_rox)
                    st.write(f"**ROX Index:** {rox_index:.2f}")

if menu == "Força Muscular Respiratória":
    # Centralizando o título
    st.markdown(
        """
        <h2 style="text-align: center;">Força Muscular Respiratória</h2>
        """,
        unsafe_allow_html=True
    )
    col2, col3 = st.columns([1, 1])

    spacer1, col2, spacer2, col3, spacer3 = st.columns([0.5, 1, 0.25, 1, 0.5])

    with col2:
        st.subheader("Pimáx Predita")
        # Importa a biblioteca necessária
        import streamlit as st

        # Subheader com ícone interativo
        with st.expander("ℹ️ Fórmula de Neder"):
            st.write("""
            **Fórmulas de PImáx**:
            - **Masculino** = 155,3 - (0,80 x idade)
            - **Feminino** = 110,4 - (0,49 x idade)
            """)

        # Seleção de gênero e idade
        gender_pimax = st.selectbox("Gênero:", [""] + ["Masculino", "Feminino"], key="pimax_gender")
        age_pimax = st.selectbox("Idade (anos):", [""] + list(range(18, 101)), key="pimax_age")


        # Função para cálculo de PImáx
        def calculate_pimax(gender, age):
            if gender == "Masculino":
                return 155.3 - (0.80 * age)
            elif gender == "Feminino":
                return 110.4 - (0.49 * age)


        # Botão para calcular
        if st.button("Calcular PImáx", key="pimax_button"):
            if gender_pimax and age_pimax != "":
                age_pimax = int(age_pimax)  # Converte a idade para inteiro
                pimax = calculate_pimax(gender_pimax, age_pimax)
                st.write(f"**PImáx Predita:** {pimax:.2f} cmH2O")
            else:
                st.warning("Por favor, selecione o gênero e a idade.")

    with col3:
        # Subheader com ícone interativo
        st.subheader("PEmáx Predita")
        with st.expander("ℹ️ Fórmula de Neder"):
            st.write(""" 
            **Fórmulas de PEmáx**:
            - **Masculino** = 165,3 - (0,81 x idade)
            - **Feminino** = 115,6 - (0,61 x idade)
            """)

        # Seleção de gênero e idade
        gender_pemax = st.selectbox("Gênero:", [""] + ["Masculino", "Feminino"], key="pemax_gender")
        age_pemax = st.selectbox("Idade (anos):", [""] + list(range(18, 101)), key="pemax_age")


        # Função para cálculo de PEmáx
        def calculate_pemax(gender, age):
            if gender == "Masculino":
                return 165.3 - (0.81 * age)
            elif gender == "Feminino":
                return 115.6 - (0.61 * age)


        # Botão para calcular
        if st.button("Calcular PEmáx", key="pemax_button"):
            if gender_pemax and age_pemax != "":
                age_pemax = int(age_pemax)  # Converte a idade para inteiro
                pemax = calculate_pemax(gender_pemax, age_pemax)
                st.write(f"**PEmáx Predita:** {pemax:.2f} cmH₂O")
            else:
                st.warning("Por favor, selecione o gênero e a idade.")

if menu == "Ventilação Mecânica":
    # Centralizando o título
    st.markdown(
        """
        <h2 style="text-align: center;">Ventilação mecânica</h2>
        """,
        unsafe_allow_html=True
    )
    st.text("")
    st.text("")
    col4, spacer1, col5, spacer2, col6 = st.columns([1, 0.4, 1, 0.4, 1])
    col7, spacer3, col8, spacer4, col9 = st.columns([1, 0.4, 1, 0.4, 1])
    col10, spacer5, col11, spacer6, col12 = st.columns([1, 0.4, 1, 0.4, 1])
    col13, spacer7, col14, spacer8 = st.columns([1, 0.4, 1, 0.4])

    with col4:
        st.subheader("Altura estimada")
        with st.expander("ℹ️ Fórmula de Chumlea"):
            st.write("""
            **Masculino**	(2,02 x AJ) - (0,04 x I) + 64,19
            **Feminino** (1,83 x AJ) - (0,24 x I) + 84,88
                   """)


        def calculate_height_chumlea(gender, age, aj):
            if gender == "Masculino":
                return (2.02 * aj) - (0.04 * age) + 64.19
            elif gender == "Feminino":
                return (1.83 * aj) - (0.24 * age) + 84.88
            else:
                return None


        gender_chumlea = st.selectbox("Gánero:", ["", "Masculino", "Feminino"], key="chumlea_gender")
        age_chumlea = st.selectbox("Idade (anos):", [""] + list(range(0, 105)), key="chumlea_age")
        aj_chumlea = st.selectbox("AJ (cm):", [""] + [round(i * 1, 1) for i in range(0, 101)], key="chumlea_aj")

        if st.button("Calcular", key="chumlea_button"):
            if gender_chumlea and age_chumlea != "" and aj_chumlea != "":
                height = calculate_height_chumlea(gender_chumlea, float(age_chumlea), float(aj_chumlea))
                st.write(f"**Altura Calculada:** {height:.2f} cm")
            else:
                st.warning("Por favor, preencha todos os campos para realizar o cálculo.")

    with col5:
        st.subheader("Peso predito")
        with st.expander("ℹ️ Fórmula"):
            st.write("""
            **Masculino**	50 + 0,91 x (Altura - 152,4 cm)
            **Feminino**  45,5 + 0,91 x (Altura - 152,4 cm)
                   """)


        def calculate_ideal_weight(gender, height):
            if gender == "Masculino":
                return 50 + 0.91 * (height - 152.4)
            elif gender == "Feminino":
                return 45.5 + 0.91 * (height - 152.4)
            else:
                return None


        gender_weight = st.selectbox("Género:", ["", "Masculino", "Feminino"], key="weight_gender")
        height_weight = st.selectbox("Altura (cm):", [""] + [round(i * 1, 1) for i in range(130, 211)],
                                     key="weight_height")

        if st.button("Calcular", key="weight_button"):
            if gender_weight and height_weight != "":
                ideal_weight = calculate_ideal_weight(gender_weight, float(height_weight))
                st.write(f"**Peso Ideal:** {ideal_weight:.2f} kg")
            else:
                st.warning("Por favor, preencha todos os campos para realizar o cálculo.")

    with col6:
        st.subheader("Constante de Tempo")
        with st.expander("ℹ️ Fórmula "):
            st.write(""" 
            (Rva x Cst) / 1000
                   """)

        # Opções para os dropdowns
        rva_options = [""] + list(range(1, 81))  # Adiciona uma opção vazia antes dos valores de 1 a 100
        cst_options = [""] + list(range(1, 201))  # Adiciona uma opção vazia antes dos valores de 1 a 100

        # Campos de entrada com dropdown
        rva = st.selectbox("Rva (cmH2O/L.s):", options=rva_options, key="time_constant_rva")
        cst = st.selectbox("Cst (L/cmH2O):", options=cst_options, key="time_constant_cst")

        # Botão para calcular a constante de tempo
        if st.button("Calcular", key="time_constant_button"):
            time_constant = calculate_time_constant(rva, cst)
            st.write(f"**Constante de Tempo:** {time_constant:.2f} s")

    with col7:
        st.subheader("Driving Pressure (ΔP)")
        with st.expander("ℹ️ Fórmula "):
            st.write("""
            ΔP = Pressão de platô - PEEP
            \n OBS: Manter DP < 15 cmH2O
                   """)
        plateau_pressure = st.selectbox("Pressão de Platô (cmH2O):", [""] + [round(i * 1, 1) for i in range(0, 501)], key="dp_plateau")
        peep = st.selectbox("PEEP (cmH2O):", [""] + [round(i * 1, 1) for i in range(0, 301)], key="dp_peep")
        if st.button("Calcular", key="dp_button"):
            driving_pressure = calculate_driving_pressure(plateau_pressure, peep)
            st.write(f"**Driving Pressure:** {driving_pressure:.2f} cmH2O")
            if driving_pressure > 15:
                st.error("Resultado maior que o permitido. Tome medidas de ventilação protetora.")

    with col8:
        st.subheader("Complacência Estática (Cst)")
        with st.expander("ℹ️ Fórmula "):
            st.write("""
            Volume corrente / (Platô - PEEP)
                   """)
        tidal_volume = st.selectbox("Volume Corrente (ml):", [""] + list (range(0, 1501, 10)), key="cst_tidal_volume")
        plateau_pressure_cst = st.selectbox("Pressão de Platô (cmH2O):", [""] + [round(i * 1, 1) for i in range(0, 51)], key="cst_plateau")
        peep_cst = st.selectbox("PEEP (cmH2O):", [""] + [round(i * 1, 1) for i in range(0, 31)], key="cst_peep")
        if st.button("Calcular", key="cst_button"):
            compliance = calculate_static_compliance(tidal_volume, plateau_pressure_cst, peep_cst)
            st.write(f"**Complacência Estática:** {compliance:.2f} ml/cmH2O")


    with col9:
        st.subheader("Resistência de Vias Aéreas (Rva)")
        with st.expander("ℹ️ Fórmula"):
            st.write("""
            (Pressão de pico - Pressão de platô) / Fluxo

                   """)


        def calculate_resistance(peak_pressure, plateau_pressure, flow_lmin):
            flow_ls = flow_lmin / 60  # Converter fluxo de L/min para L/s
            return (peak_pressure - plateau_pressure) / flow_ls if flow_ls > 0 else None


        peak_pressure = st.selectbox("Pressão de Pico (cmH2O):", [""] + [round(i * 1, 1) for i in range(0, 101)],
                                     key="rva_peak")
        plateau_pressure_rva = st.selectbox("Pressão de Platô (cmH2O):", [""] + [round(i * 1, 1) for i in range(0, 51)],
                                            key="rva_plateau")
        flow = st.selectbox("Fluxo (L/min):", [""] + [round(i * 1, 1) for i in range(0, 601)], key="rva_flow")

        if st.button("Calcular", key="rva_button"):
            if peak_pressure != "" and plateau_pressure_rva != "" and flow != "":
                resistance = calculate_resistance(float(peak_pressure), float(plateau_pressure_rva), float(flow))
                if resistance is not None:
                    st.write(f"**Resistência de Vias Aéreas:** {resistance:.2f} cmH2O/L/s")
                else:
                    st.warning("O fluxo deve ser maior que zero para realizar o cálculo.")
            else:
                st.warning("Por favor, preencha todos os campos para realizar o cálculo.")

    with col10:
        st.subheader("Relação PaO2/FiO2")
        with st.expander("ℹ️ Fórmula:"):
            st.write(""" PaO2 / FiO2
                               """)

        # Campos de entrada
        pao2 = st.selectbox(
            "Pressão arterial de oxigênio (PaO2):",
            [""] + list(range(0, 1001)),  # Valores de 0 a 1000
            key="pao2"
        )
        fio2 = st.selectbox(
            "Fração inspirada de oxigênio (FiO2):",
            [""] + [round(x, 2) for x in [i * 0.01 for i in range(21, 101)]],  # Valores de 0.21 a 1.0
            key="fio2"
        )

        # Botão para calcular
        if st.button("Calcular"):
            # Converte os valores para float
            pao2 = float(pao2) if pao2 != "" else None
            fio2 = float(fio2) if fio2 != "" else None

            # Calcula a relação usando a função
            resultado, erro = calculate_pao2_fio2(pao2, fio2)

            # Exibe o resultado ou a mensagem de erro
            if erro:
                st.error(erro)
            else:
                st.write(f"**Relação PaO2/FiO2:** {resultado:.2f}")

    with col11:
        st.subheader("Pressão Muscular (Pmus)")
        with st.expander("ℹ️ Fórmula "):
            st.write("""
            -0,75 x ΔPocc
            \n OBS: Utilize o valor absoluto da ΔPocc
                   """)
        delta_pocc = st.selectbox("ΔPocc:", [""] + [round(i * 1, 1) for i in range(0, 101)], key="pmus_delta_pocc")
        if st.button("Calcular", key="pmus_button"):
            pmus = calculate_muscular_pressure(delta_pocc)
            st.write(f"**Pressão Muscular:** {pmus:.2f} cmH2O")

    with col12:
        st.subheader("Índice de respiração rápida e superficial")
        with st.expander("ℹ️ Fórmula "):
            st.write("""
            FR / VC (L)
                   """)
        fr_irrs = st.selectbox("Frequência Respiratória (FR):", [""] + list(range(0, 81)), key="irrs_fr")
        vt_irrs = st.selectbox("Volume Corrente (L):", [""] + [round(i * 0.01, 2) for i in range(10, 101)],
                               key="irrs_vt")

        if st.button("Calcular IRRS", key="irrs_button"):
            if fr_irrs != "" and vt_irrs != "":
                irrs = calculate_irrs(float(fr_irrs), float(vt_irrs))
                st.write(f"**IRRS:** {irrs:.2f}")
            else:
                st.warning("Por favor, preencha todos os campos para realizar o cálculo.")

    with col13:
        st.subheader("R/I Ratio")
        st.write("")
        with st.expander("ℹ️ Fórmula de Pan e col.:"):
            st.write("""
            R/I ratio = {[(VTeH →L – VTeH) / VTi x (PplatL – PEEPL) / (PEEPH – PEEPL)] – 1}
                   """)
        vteh_l = st.text_input("VTeH →L (mL):", value="", key="vteh_l")
        vteh = st.text_input("VTeH (mL):", value="", key="vteh")
        vti = st.text_input("VTi (mL):", value="", key="vti")
        pplatl = st.text_input("PplatL (cmH2O):", value="", key="pplatl")
        peepl = st.text_input("PEEPL (cmH2O):", value="", key="peepl")
        peeph = st.text_input("PEEPH (cmH2O):", value="", key="peeph")

        if st.button("Calcular", key="calculate_button"):
            try:
                # Converter os valores para float, se possível
                vteh_l = float(vteh_l) if vteh_l else 0.0
                vteh = float(vteh) if vteh else 0.0
                vti = float(vti) if vti else 1.0  # Evitar divisão por zero
                pplatl = float(pplatl) if pplatl else 0.0
                peepl = float(peepl) if peepl else 0.0
                peeph = float(peeph) if peeph else 0.0

                # Cálculo
                delta_vt = (vteh_l - vteh) / vti
                delta_p = (pplatl - peepl) / (peeph - peepl)
                ri_ratio = (delta_vt * delta_p) - 1

                st.write(f"**R/I Ratio:** {ri_ratio:.2f}")

            except ValueError:
                st.error("Por favor, insira valores numéricos válidos.")
            except ZeroDivisionError:
                st.error(
                    "Certifique-se de que o valor de PEEP alto seja diferente do PEEP baixo e que VTi não seja zero.")

        with col14:
            st.subheader("Mechanical Power")
            with st.expander("ℹ️ Fórmula (Gattinoni)"):
                st.write("""
                        0.098 x FR x VC x (Ppico - DP/2)
                               """)

            fr = st.text_input("Frequência Respiratória (FR):", value="", key="mp_fr")
            vc = st.text_input("Volume Corrente (ml):", value="", key="mp_vc")
            ppico = st.text_input("Pressão Pico (cmH2O):", value="", key="mp_ppico")
            dp = st.text_input("Driving Pressure (cmH2O):", value="", key="mp_dp")

            if st.button("Calcular", key="mp_button"):
                try:
                    # Conversão para float
                    fr = float(fr)
                    vc = float(vc) / 1000  # Converter para litros
                    ppico = float(ppico)
                    dp = float(dp)

                    # Cálculo da Mechanical Power
                    mechanical_power = 0.098 * fr * vc * (ppico - dp / 2)
                    st.write(f"**Mechanical Power:** {mechanical_power:.2f} J/min")

                except ValueError:
                    st.error("Por favor, insira valores numéricos válidos.")

# Rodapé
st.markdown(
    """
    <hr style="border:1px solid #e1e1e1;margin-top:20px;">
    <div style="text-align: center;">
        <p style="font-size:14px;color:grey;">
            Desenvolvido por Dyego Tavares de Lima - Fisioterapeuta Intensivista | 2025 <br> Qualquer sugestão, entre em contato conosco.
        </p>
        <p style="font-size:14px;color:grey;">
            <a href="https://www.instagram.com/fisioterapeuta.dyegotavares" target="_blank" style="text-decoration:none;color:#3f729b;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram" style="width:20px;height:20px;vertical-align:middle;margin-right:5px;">
                Instagram
            </a> 
            |
            <a href="https://wa.me/5583998113637" target="_blank" style="text-decoration:none;color:#25d366;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" style="width:20px;height:20px;vertical-align:middle;margin-right:5px;">
                WhatsApp
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
