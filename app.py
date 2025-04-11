import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import matplotlib.pyplot as plt


def load_data(uploaded_file, sheet_name=None):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        if sheet_name is None:
            return pd.read_excel(uploaded_file, sheet_name=0)
        else:
            return pd.read_excel(uploaded_file, sheet_name=sheet_name)


def compare_data(df1, df2, ignore_case=False, ignore_spaces=False, numeric_tolerance=0.0):
    diffs = pd.DataFrame(False, index=df1.index, columns=df1.columns)
    comparison = df1.copy().astype(str)
    explanation_col = []

    for col in df1.columns:
        series1 = df1[col].astype(str)
        series2 = df2[col].astype(str)

        if ignore_case:
            series1 = series1.str.lower()
            series2 = series2.str.lower()
        if ignore_spaces:
            series1 = series1.str.strip()
            series2 = series2.str.strip()

        if pd.api.types.is_numeric_dtype(df1[col]) and pd.api.types.is_numeric_dtype(df2[col]):
            diffs[col] = ~np.isclose(df1[col], df2[col], atol=numeric_tolerance)
            comparison[col] = df1[col].astype(str) + ' / ' + df2[col].astype(str)
        else:
            diffs[col] = series1 != series2
            comparison[col] = df1[col].astype(str) + ' / ' + df2[col].astype(str)

    return diffs, comparison


def get_diff_summary(diffs):
    return diffs.sum().reset_index().rename(columns={0: 'Differences', 'index': 'Column'})


def to_excel_download(df, filename="comparison.xlsx", key_columns=None):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Create a copy of the dataframe without explanation columns for the main sheet
        main_df = df.copy()
        explanation_cols = [col for col in df.columns if col.startswith('Explicacion_')]
        main_df = main_df.drop(columns=explanation_cols)
        
        # Ensure key columns are first in the Excel output
        if '_temp_key' in main_df.columns:
            key_col = ['_temp_key']
            other_cols = [col for col in main_df.columns if col != '_temp_key']
            main_df = main_df[key_col + other_cols]
        
        main_df.to_excel(writer, sheet_name='Comparison', index=False)
        
        # Create a separate dataframe for explanations
        explanation_df = pd.DataFrame()
        
        # Ensure key column is first
        if '_temp_key' in df.columns:
            explanation_df['_temp_key'] = df['_temp_key']
        
        for col in [c for c in df.columns if not c.startswith('Explicacion_') and c != '_temp_key']:
            explanation_df[col] = df[col]
            if f'Explicacion_{col}' in df.columns:
                explanation_df[f'Explicacion_{col}'] = df[f'Explicacion_{col}']
        
        explanation_df.to_excel(writer, sheet_name='Explanations', index=False)
        
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Comparison']
        
        # Add a yellow fill format for highlighting differences
        highlight_format = workbook.add_format({'bg_color': '#FFFF00'})
        
        # Iterate through the dataframe to highlight cells with differences
        for i, col in enumerate(main_df.columns):
            if col != '_temp_key':  # Skip the key column
                # Check if there's an explanation for this column
                explanation_col = f'Explicacion_{col}'
                if explanation_col in df.columns:
                    # Apply conditional formatting based on whether there's an explanation
                    col_idx = list(main_df.columns).index(col)
                    for row_idx in range(len(df)):
                        if df.iloc[row_idx].get(explanation_col, "") != "":  # If there's an explanation
                            worksheet.write(row_idx + 1, col_idx, df.iloc[row_idx][col], highlight_format)
    
    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download Excel File</a>'
    return href


def generate_explanation(value_a, value_b, column):
    try:
        # Simple heuristics for demo purposes
        if value_a.lower() == value_b.lower():
            return "Solo diferencia de mayúsculas"
        elif value_a.replace(" ", "") == value_b.replace(" ", ""):
            return "Diferencia de espacios"
        elif value_a.replace(",", ".").replace(" ", "").isdigit() and value_b.replace(",", ".").replace(" ", "").isdigit():
            return "Diferencia numérica o de formato"
        elif "/" in value_a and "/" in value_b:
            return "Posible diferencia de formato de fecha"
        elif len(value_a) > 3 and len(value_b) > 3 and value_a.lower() in value_b.lower() or value_b.lower() in value_a.lower():
            return "Nombre similar con sufijos/prefijos"
        else:
            return "Cambio de contenido significativo"
    except:
        return "Sin explicación"


st.title("Comparador de Ficheros o Pestañas Excel")

st.sidebar.header("Configuraciones")
ignore_case = st.sidebar.checkbox("Ignorar mayúsculas/minúsculas", value=True)
ignore_spaces = st.sidebar.checkbox("Ignorar espacios", value=True)
numeric_tolerance = st.sidebar.number_input("Tolerancia numérica", min_value=0.0, value=0.0, step=0.001)

uploaded_file1 = st.file_uploader("Sube el primer fichero o pestaña", type=["csv", "xlsx"])
uploaded_file2 = st.file_uploader("Sube el segundo fichero o pestaña", type=["csv", "xlsx"])

if uploaded_file1 and uploaded_file2:
    if uploaded_file1.name.endswith(".xlsx"):
        sheet_names1 = pd.ExcelFile(uploaded_file1).sheet_names
        selected_sheet1 = st.selectbox("Selecciona una pestaña del primer archivo:", sheet_names1)
        df1 = load_data(uploaded_file1, sheet_name=selected_sheet1)
    else:
        df1 = load_data(uploaded_file1)
        
    if uploaded_file2.name.endswith(".xlsx"):
        sheet_names2 = pd.ExcelFile(uploaded_file2).sheet_names
        selected_sheet2 = st.selectbox("Selecciona una pestaña del segundo archivo:", sheet_names2)
        df2 = load_data(uploaded_file2, sheet_name=selected_sheet2)
    else:
        df2 = load_data(uploaded_file2)

    # Normalize column names if ignore_case is enabled
    if ignore_case:
        df1.columns = [col.lower() for col in df1.columns]
        df2.columns = [col.lower() for col in df2.columns]
    
    # Verificar duplicados en ambos dataframes
    common_columns = list(set(df1.columns).intersection(set(df2.columns)))
    
    if common_columns:
        st.subheader("Selección de claves para comparación")
        key_columns = st.multiselect("Selecciona columnas como claves de comparación:", common_columns)
        
        if key_columns:
            # Verificar duplicados en las claves seleccionadas
            duplicates_df1 = df1[df1.duplicated(subset=key_columns, keep=False)]
            duplicates_df2 = df2[df2.duplicated(subset=key_columns, keep=False)]
            
            if not duplicates_df1.empty:
                st.warning(f"¡Hay {len(duplicates_df1)} filas con valores duplicados en las claves seleccionadas del primer archivo!")
                with st.expander("Ver duplicados del primer archivo"):
                    st.dataframe(duplicates_df1)
            
            if not duplicates_df2.empty:
                st.warning(f"¡Hay {len(duplicates_df2)} filas con valores duplicados en las claves seleccionadas del segundo archivo!")
                with st.expander("Ver duplicados del segundo archivo"):
                    st.dataframe(duplicates_df2)
            
            # Crear una columna compuesta para indexación
            df1['_temp_key'] = df1[key_columns].astype(str).agg('-'.join, axis=1)
            df2['_temp_key'] = df2[key_columns].astype(str).agg('-'.join, axis=1)
            
            # Realizar comparación basada en las claves
            df1_indexed = df1.set_index('_temp_key')
            df2_indexed = df2.set_index('_temp_key')
            
            # Encontrar claves comunes
            common_keys = set(df1_indexed.index).intersection(set(df2_indexed.index))
            only_in_df1 = set(df1_indexed.index) - set(df2_indexed.index)
            only_in_df2 = set(df2_indexed.index) - set(df1_indexed.index)
            
            st.write(f"Claves comunes: {len(common_keys)}")
            st.write(f"Claves solo en el primer archivo: {len(only_in_df1)}")
            st.write(f"Claves solo en el segundo archivo: {len(only_in_df2)}")
            
            # Filtrar para comparar solo las filas con claves comunes
            df1_common = df1_indexed.loc[list(common_keys)].reset_index()
            df2_common = df2_indexed.loc[list(common_keys)].reset_index()
            
            # Continuar con la comparación normal pero solo con las filas comunes
            cols1 = set(df1_common.columns)
            cols2 = set(df2_common.columns)
            
            # Mostrar información sobre las diferencias en columnas
            if len(cols1) != len(cols2):
                st.write(f"Número de columnas: Archivo 1 ({len(cols1)}), Archivo 2 ({len(cols2)})")
            
            cols_only_in_1 = cols1 - cols2
            if cols_only_in_1:
                st.write("Columnas solo en el primer archivo:", ", ".join(cols_only_in_1))
                
            cols_only_in_2 = cols2 - cols1
            if cols_only_in_2:
                st.write("Columnas solo en el segundo archivo:", ", ".join(cols_only_in_2))
            
            st.success("Archivos filtrados cargados correctamente. Comparando...")
            
            # Asegurarse de que ambos dataframes tienen las mismas columnas para comparación
            common_cols = list(set(df1_common.columns).intersection(set(df2_common.columns)))
            common_cols = [col for col in common_cols if col != '_temp_key']
            
            df1_to_compare = df1_common[common_cols]
            df2_to_compare = df2_common[common_cols]
            
            # Realizar la comparación
            diffs, comparison = compare_data(df1_to_compare, df2_to_compare, ignore_case, ignore_spaces, numeric_tolerance)
            
            # Añadir la columna de clave para mantener la referencia
            comparison['_temp_key'] = df1_common['_temp_key']
            
            # Añadir explicaciones
            explanations = []
            for idx in comparison.index:
                row_expl = []
                for col in comparison.columns:
                    if col != '_temp_key' and diffs.at[idx, col]:
                        val_a, val_b = comparison.at[idx, col].split(" / ", 1)
                        explanation = generate_explanation(val_a, val_b, col)
                        row_expl.append(explanation)
                    else:
                        row_expl.append("")
                explanations.append(row_expl)
            
            explanation_df = pd.DataFrame(explanations, columns=comparison.columns)
            combined_df = comparison.copy()
            for col in comparison.columns:
                if col != '_temp_key':
                    combined_df[f"Explicacion_{col}"] = explanation_df[col]
            
            # Crear pestañas para organizar la información
            tab1, tab2, tab3, tab4 = st.tabs(["Resumen", "Gráfico", "Detalles por Columna", "Datos Completos"])
            
            with tab1:
                summary = get_diff_summary(diffs)
                st.subheader("Resumen de Diferencias por Columna")
                st.dataframe(summary)
                st.markdown(to_excel_download(combined_df, key_columns=key_columns), unsafe_allow_html=True)
            
            with tab2:
                st.subheader("Visualización de Diferencias")
                fig, ax = plt.subplots()
                ax.bar(summary['Column'], summary['Differences'])
                plt.xticks(rotation=45, ha='right')
                plt.title("Cantidad de Diferencias por Columna")
                st.pyplot(fig)
            
            with tab3:
                st.subheader("Detalles por Columna")
                selected_column = st.selectbox("Selecciona una columna para ver detalles:", [col for col in df1_to_compare.columns if col != '_temp_key'])
                filtered = combined_df[diffs[selected_column]]
                st.dataframe(filtered[['_temp_key', selected_column, f"Explicacion_{selected_column}"]])
            
            with tab4:
                st.subheader("Datos Completos")
                st.dataframe(combined_df)
        else:
            st.warning("Por favor, selecciona al menos una columna como clave para la comparación.")
    else:
        st.error("No hay columnas comunes entre los archivos para usar como claves.")
else:
    st.info("Sube ambos ficheros para comenzar la comparación.")