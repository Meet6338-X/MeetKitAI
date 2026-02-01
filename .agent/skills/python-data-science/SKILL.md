---
name: python-data-science
description: Python Data Science & Machine Learning patterns. Pandas, NumPy, Scikit-learn, and visualization best practices.
---

# Python Data Science Mastery

> **Goal**: Write efficient, reproducible, and clean data science code.

## 1. Core Libraries & Patterns

### NumPy (Numerical Python)
- **Vectorization**: Avoid loops. Use array operations.
    ```python
    # Bad
    [x * 2 for x in array]
    # Good
    array * 2
    ```
- **Broadcasting**: Understand how arrays of different shapes interact.

### Pandas (Data Analysis)
- **Chaining**: Use method chaining (`.assign`, `.pipe`, `.query`) for readable transformations.
- **Vectorized String Operations**: Use `.str` accessor.
- **Dates**: Convert to `datetime` objects immediately (`pd.to_datetime`).
- **Memory**: Use `category` dtype for string columns with few unique values.

### Scikit-Learn (Machine Learning)
- **Pipelines**: ALWAYS use `Pipeline` to bundle preprocessing and modeling. Prevents data leakage.
    ```python
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('imputer', SimpleImputer()),
        ('model', RandomForestClassifier())
    ])
    ```
- **Evaluation**: Use `cross_val_score` and stratified splits.

## 2. Visualization (Matplotlib & Seaborn)

- **Object-Oriented Interface**: Use `fig, ax = plt.subplots()`. Avoid `plt.plot()`.
- **Style**: Use `sns.set_style("whitegrid")` / `plt.style.use('fivethirtyeight')`.
- **Labels**: Always label axes and titles. `ax.set_xlabel()`.

## 3. Jupyter Notebook Best Practices

- **Imports at Top**: All imports in the first cell.
- **Restart & Run All**: Code must run linearly from top to bottom.
- **Extract to Scripts**: Move complex functions/classes to `.py` files and import them.
- **Version Control**: Don't commit output (or use `jupytext` / `nbstripout`).

## 4. Project Structure

```
project/
├── data/
│   ├── raw/            # Immutable original data
│   ├── processed/      # Cleaned data
│   └── external/       # Third-party data
├── notebooks/          # Exploration
│   ├── 01_exploration.ipynb
│   └── 02_modeling.ipynb
├── src/                # Reusable source code
│   ├── __init__.py
│   ├── data.py         # Scripts to download or generate data
│   ├── features.py     # Scripts to turn raw data into features
│   └── models.py       # Scripts to train models
├── models/             # Serialized models (pickles)
└── reports/            # Generated analysis as HTML, PDF, LaTeX
```

## 5. Environment & Reproducibility

- **Dependencies**: Use `requirements.txt` or `pyproject.toml` (Poetry/Rye is better).
- **Virtual Env**: Always use `venv` or `conda`.
- **Seeds**: Set random seeds for NumPy, PyTorch, TensorFlow for reproducibility.
