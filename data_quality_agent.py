"""
Data Quality Agent - Automated EDA & Quality Checks
Runs pure pandas analysis (no LLM needed) to detect data issues.
"""
import pandas as pd
import numpy as np


def run_data_quality_check(df: pd.DataFrame) -> dict:
    """
    Performs automated data quality analysis on a DataFrame.
    
    Returns:
        dict with keys: shape, memory, missing, duplicates, outliers, dtypes_summary, stats
    """
    report = {}
    
    # 1. Basic Shape
    report['shape'] = {'rows': df.shape[0], 'columns': df.shape[1]}
    report['memory_mb'] = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    
    # 2. Missing Values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        'missing_count': missing,
        'missing_pct': missing_pct
    })
    # Only include columns that have missing values
    missing_df = missing_df[missing_df['missing_count'] > 0].sort_values('missing_pct', ascending=False)
    report['missing'] = missing_df.to_dict('index') if not missing_df.empty else {}
    report['total_missing_pct'] = round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2)
    
    # 3. Duplicates
    report['duplicate_rows'] = int(df.duplicated().sum())
    report['duplicate_pct'] = round(df.duplicated().sum() / len(df) * 100, 2)
    
    # 4. Outliers (IQR method on numeric columns)
    outliers = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
        if outlier_count > 0:
            outliers[col] = {
                'count': outlier_count,
                'pct': round(outlier_count / len(df) * 100, 2),
                'range': f"{lower:.2f} – {upper:.2f}"
            }
    report['outliers'] = outliers
    
    # 5. Data Type Summary
    dtype_counts = df.dtypes.astype(str).value_counts().to_dict()
    report['dtypes_summary'] = dtype_counts
    
    # 6. Quick Stats for numeric columns
    if len(numeric_cols) > 0:
        stats = df[numeric_cols].describe().round(2).to_dict()
        report['numeric_stats'] = stats
    else:
        report['numeric_stats'] = {}
    
    return report


def format_quality_report(report: dict) -> str:
    """
    Formats the quality report dict into a readable markdown string
    for injection into LLM prompts.
    """
    lines = []
    lines.append(f"**Dataset Shape:** {report['shape']['rows']} rows × {report['shape']['columns']} columns")
    lines.append(f"**Memory Usage:** {report['memory_mb']} MB")
    lines.append(f"**Duplicate Rows:** {report['duplicate_rows']} ({report['duplicate_pct']}%)")
    lines.append(f"**Overall Missing Data:** {report['total_missing_pct']}%")
    
    if report['missing']:
        lines.append("\n**Columns with Missing Values:**")
        for col, info in report['missing'].items():
            lines.append(f"  - `{col}`: {info['missing_count']} missing ({info['missing_pct']}%)")
    
    if report['outliers']:
        lines.append("\n**Outlier Detection (IQR):**")
        for col, info in report['outliers'].items():
            lines.append(f"  - `{col}`: {info['count']} outliers ({info['pct']}%) — expected range: {info['range']}")
    
    lines.append(f"\n**Data Types:** {report['dtypes_summary']}")
    
    return "\n".join(lines)
