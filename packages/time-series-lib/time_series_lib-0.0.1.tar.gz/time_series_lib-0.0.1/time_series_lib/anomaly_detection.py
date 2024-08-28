import numpy as np

def detect_anomalies_iqr(series):
    """
    Обнаружение аномалий с использованием межквартильного размаха (IQR)

    series: временной ряд
    """

    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    anomalies = series[(series < lower_bound) | (series > upper_bound)]

    return anomalies

def detect_anomalies_z_score(series, threshold=3):
    """
    Обнаружение аномалий с использованием Z-оценки

    series: временной ряд
    threshold: порог для Z-оценки
    """

    mean = series.mean()
    std = series.std()
    z_scores = (series - mean) / std
    anomalies = series[np.abs(z_scores) > threshold]

    return anomalies
