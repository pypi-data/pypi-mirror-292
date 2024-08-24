import pandas as pd
import polars as pl
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from IPython.display import HTML


class descriptivo:
    @staticmethod
    def dataframe_info(df, include=None, exclude=None, return_format='dataframe', display_table = True, texto = None, Numero = None, Espacial = None, Time=None):
        """
        Muestra información sobre las variables del DataFrame.

        Parameters:
        -----------
        df : pandas.DataFrame o polars.DataFrame
            El DataFrame a analizar.
        include : list, optional
            Lista de tipos de datos a incluir.
        exclude : list, optional
            Lista de tipos de datos a excluir.
        return_format : str, optional
            Formato de retorno ('dataframe', 'dict', 'string'). Por defecto 'dataframe'.

        Returns:
        --------
        DataFrame, dict, o string dependiendo del return_format especificado.

        Examples:
        ---------
        >>> import pandas as pd
        >>> df_pandas = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
        >>> descriptivo.dataframe_info(df_pandas)

        >>> import polars as pl
        >>> df_polars = pl.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
        >>> descriptivo.dataframe_info(df_polars)
        """
        # Convertir a Polars DataFrame si es necesario
        if isinstance(df, pd.DataFrame):
            df = pl.from_pandas(df)
        elif not isinstance(df, pl.DataFrame):
            raise TypeError("El argumento debe ser un pandas DataFrame o un polars DataFrame")

        # Filtrar columnas si se especifica include o exclude
        if include is not None:
            df = df.select(pl.col(df.columns).filter(lambda x: x.dtype in include))
        elif exclude is not None:
            df = df.select(pl.col(df.columns).filter(lambda x: x.dtype not in exclude))

        # Obtener información
        total_rows = df.height
        info = pl.DataFrame({
            'Variable': df.columns,
            'Tipo': df.dtypes,
            'Conteo No Nulos': df.null_count().pipe(lambda x: total_rows),
        })

        info = info.with_columns([
            pl.col('Conteo No Nulos').cast(pl.Int64),
            (pl.col('Conteo No Nulos') / total_rows * 100).alias('% No Nulos').round(2),
        ])
        
        if display_table == True:
                html = "<div style='font-family: Garamond, serif; padding: 8px; background-color: #ffffff; border-radius: 0px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1), 0 6px 20px rgba(0, 0, 0, 0.1), 0 10px 30px rgba(0, 0, 0, 0.1); transition: box-shadow 0.3s ease-in-out;'>"
                html += "<h2 style='text-align:center;'> Análisis Descriptivo </h2>"

                # ---------- Datos Categóricos -----
                objetos = df.select([pl.col(pl.Utf8), pl.col(pl.Object)])
                data_categóricos = [["Variable","Tipo",	"Número de Clases",	"Ejemplo",	"Conteo"]] + [[i, objetos[i].dtype, objetos[i].n_unique(), objetos[i].unique().to_list(), objetos[i].drop_nulls().len()] for i in objetos.columns]

                tabla_categorica = f"<h4> Variables Categóricas: se identificaron un total de {len(objetos.columns)} variables </h4>"
                tabla_categorica += "<table style='border-collapse: separate; border-spacing: 0.5px; width: 95%; border: 0px solid red; margin-left:2.5%''>"
                for i, row in enumerate(data_categóricos):
                    if i == 0:
                        tabla_categorica += "<tr style='background-color: #3D405B; text-align:center; color: white;'>"
                    else:
                        tabla_categorica += "<tr>"
                    for cell in row:
                        tabla_categorica += f"<td style='border: 1px solid black; padding: 4px; text-align: center;'>{cell}</td>"
                    tabla_categorica += "</tr>"
                tabla_categorica += "</table>"
                html += tabla_categorica



                # ----- datos Numéricos ----------------------
                data_numericos = np.array(["Variable", "Promedio", "Std", "Min", "25%", "50%", "75%", "Max", "Asimetría", "Conteo"])
                tabla_numericos = df.select([pl.col(pl.Int64), pl.col(pl.Float64)])
                for i in tabla_numericos.columns:
                    metrics = tabla_numericos.select([
                            pl.col(i).mean().alias("mean"),
                            pl.col(i).std().alias("std"),
                            pl.col(i).min().alias("min"),
                            pl.col(i).quantile(0.25).alias("25%"),
                            pl.col(i).quantile(0.50).alias("50%"),
                            pl.col(i).quantile(0.75).alias("75%"),
                            pl.col(i).max().alias("max"),
                            pl.col(i).skew().alias("skew"),
                            pl.col(i).count().alias("count")
                        ])

                    stats_list = np.append([i], np.around(np.array(metrics)[0],4))
                    data_numericos = np.vstack([data_numericos, stats_list])

                tabla_numerica = f"<h4> Variables Numéricas: se identificaron un total de {len(tabla_numericos.columns)} variables </h4>"
                tabla_numerica += "<table style='border-collapse: separate; border-spacing: 0.5px; width: 95%; border: 0px solid red; margin-left:2.5%''>"
                for i, row in enumerate(data_numericos):
                    if i == 0:
                        tabla_numerica += "<tr style='background-color: #81B29A; text-align:center; color: white;'>"
                    else:
                        tabla_numerica += "<tr>"
                    for cell in row:
                        tabla_numerica += f"<td style='border: 1px solid black; padding: 4px; text-align: center;'>{cell}</td>"
                    tabla_numerica += "</tr>"
                tabla_numerica += "</table>"
                html += tabla_numerica


                if Time != None:
                    # Datos de ejemplo
                    data = [
                        [ "Variable",     "Inicio",     "Fin",     "Periodo",     "Tendencia",     "Estacionalidad",     "Autocorrelacion",     "Estacionariedad",     "Volatilidad",     "Funcion_autocorrelacion"],
                        ["Variable J", "2023-01-01", "2023-03-31", 3, "ascendente", "media", 0.72, "sí", 0.27, 0.62],
                        ["Variable K", "2022-01-01", "2022-03-31", 3, "descendente", "alta", 0.67, "no", 0.37, 0.52],
                        ["Variable L", "2021-01-01", "2021-03-31", 3, "estable", "baja", 0.82, "sí", 0.17, 0.72]
                    ]

                    tabla_temporal = "<h4> Variables de Series de Tiempo: se identificaron un total de 81 variables </h4>"
                    tabla_temporal += "<table style='border-collapse: separate; border-spacing: 2px; width: 95%; border: 2px solid; margin-left:2.5%''>"
                    for i, row in enumerate(data):
                        if i == 0:
                            tabla_temporal += "<tr style='background-color: #E07A5F; text-align:center; color: white;'>"
                        else:
                            tabla_temporal += "<tr>"
                        for cell in row:
                            tabla_temporal += f"<td style='border: 1px solid black; padding: 4px; text-align:center; '>{cell}</td>"
                        tabla_temporal += "</tr>"
                    tabla_temporal += "</table>"
                    html += tabla_temporal

                if Espacial != None:
                    # Datos de ejemplo
                    data = [
                        ["Variable", "Media","Mediana",  "Moda", "Varianza", "Std","Autocorrelacion","Indice_geary","Semivariograma",     "Anisotropia" ],
                        ["Variable D", 14.2, 14.0, 15, 4.7, 2.2, 0.6, 1.4, 0.4, 0.5],
                        ["Variable E", 19.8, 19.5, 20, 5.3, 2.4, 0.8, 1.0, 0.6, 0.7],
                        ["Variable F", 11.1, 11.0, 10, 3.6, 1.8, 0.7, 1.5, 0.3, 0.4]
                    ]

                    tabla_espacial = "<h4> Variables Espaciales: se identificaron un total de 81 variables </h4>"
                    tabla_espacial += "<table style='border-collapse: separate; border-spacing: 2px; width: 95%; border: 0px solid red; margin-left:2.5%'>"
                    for i, row in enumerate(data):
                        if i == 0:
                            tabla_espacial += "<tr style='background-color: #F4F1DE; text-align:center; color: black;'>"
                        else:
                            tabla_espacial += "<tr>"
                        for cell in row:
                            tabla_espacial += f"<td style='border: 1px solid black; padding: 4px; text-align: center;'>{cell}</td>"
                        tabla_espacial += "</tr>"
                    tabla_espacial += "</table>"
                    html += tabla_espacial
                    html += "</div>"
                display(HTML(html))

        return

        # Retornar en el formato especificado
        #if return_format == 'dataframe':
        #    return info
        #elif return_format == 'dict':
        #    return info.to_dicts()
        #elif return_format == 'string':
        #    return info.to_pandas().to_string(index=False)
        #else:
        #    raise ValueError("Formato de retorno no válido. Use 'dataframe', 'dict' o 'string'.")

    @staticmethod
    def normality_test(data, column, alpha=0.05, plot=True):
        """
        Perform normality tests and create visualizations for a specified column.

        Parameters:
        -----------
        data : polars.DataFrame or pandas.DataFrame
            The DataFrame containing the data.
        column : str
            The name of the column to test for normality.
        alpha : float, optional
            The significance level for the tests. Default is 0.05.
        plot : bool, optional
            Whether to create and show plots. Default is True.

        Returns:
        --------
        dict
            A dictionary containing the test results and statistics.
        """
        # Convert to polars if it's a pandas DataFrame
        if isinstance(data, pd.DataFrame):
            data = pl.from_pandas(data)
        
        # Extract the column data as a numpy array
        col_data = data[column].to_numpy()
        
        # Remove NaN values
        col_data = col_data[~np.isnan(col_data)]

        # Perform normality tests
        shapiro_test = stats.shapiro(col_data)
        ks_test = stats.kstest(col_data, 'norm')
        jb_test = stats.jarque_bera(col_data)

        results = {
            'Shapiro-Wilk Test': {
                'statistic': shapiro_test.statistic,
                'p-value': shapiro_test.pvalue,
                'normal': shapiro_test.pvalue > alpha
            },
            'Kolmogorov-Smirnov Test': {
                'statistic': ks_test.statistic,
                'p-value': ks_test.pvalue,
                'normal': ks_test.pvalue > alpha
            },
            'Jarque-Bera Test': {
                'statistic': jb_test.statistic,
                'p-value': jb_test.pvalue,
                'normal': jb_test.pvalue > alpha
            }
        }

        if plot:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Histogram
            ax1.hist(col_data, bins='auto', density=True, alpha=0.7, color='skyblue')
            ax1.set_title(f'Histogram of {column}')
            ax1.set_xlabel(column)
            ax1.set_ylabel('Density')

            # Add a best fit line
            xmin, xmax = ax1.get_xlim()
            x = np.linspace(xmin, xmax, 100)
            p = stats.norm.pdf(x, np.mean(col_data), np.std(col_data))
            ax1.plot(x, p, 'k', linewidth=2)

            # Q-Q plot
            stats.probplot(col_data, dist="norm", plot=ax2)
            ax2.set_title(f'Q-Q plot of {column}')

            plt.tight_layout()
            plt.show()

        return results

    @staticmethod
    def detect_outliers(data, column, method='iqr', threshold=1.5):
        """
        Detect outliers in a specified column using either IQR or Standard Deviation method.

        Parameters:
        -----------
        data : polars.DataFrame or pandas.DataFrame
            The DataFrame containing the data.
        column : str
            The name of the column to check for outliers.
        method : str, optional
            The method to use for outlier detection. Either 'iqr' for Interquartile Range
            or 'std' for Standard Deviation. Default is 'iqr'.
        threshold : float, optional
            The threshold for outlier detection. For IQR method, this is the IQR multiplier.
            For STD method, this is the number of standard deviations. Default is 1.5.

        Returns:
        --------
        dict
            A dictionary containing the outliers, their indices, and summary statistics.
        """
        # Convert to polars if it's a pandas DataFrame
        if isinstance(data, pd.DataFrame):
            data = pl.from_pandas(data)
        
        # Extract the column data as a numpy array
        col_data = data[column].to_numpy()
        
        # Remove NaN values
        col_data = col_data[~np.isnan(col_data)]

        if method == 'iqr':
            Q1 = np.percentile(col_data, 25)
            Q3 = np.percentile(col_data, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            outlier_indices = np.where((data[column] < lower_bound) | (data[column] > upper_bound))[0]
        elif method == 'std':
            mean = np.mean(col_data)
            std = np.std(col_data)
            lower_bound = mean - threshold * std
            upper_bound = mean + threshold * std
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            outlier_indices = np.where((data[column] < lower_bound) | (data[column] > upper_bound))[0]
        else:
            raise ValueError("Method must be either 'iqr' or 'std'")

        results = {
            'outliers': outliers.tolist(),
            'outlier_indices': outlier_indices.tolist(),
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'num_outliers': len(outliers),
            'percent_outliers': (len(outliers) / len(col_data)) * 100,
            'summary_stats': {
                'mean': np.mean(col_data),
                'median': np.median(col_data),
                'std': np.std(col_data),
                'min': np.min(col_data),
                'max': np.max(col_data)
            }
        }

        return results