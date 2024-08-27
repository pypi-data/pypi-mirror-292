

def plot_correlation(df, min_threshold=-0.9, max_threshold=0.9, figsize=(6, 6)):
    corr_matrix = df.corr()
    filtered_corr_matrix = corr_matrix[(corr_matrix > max_threshold) | (corr_matrix < min_threshold)]
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(filtered_corr_matrix, annot=True, cmap='coolwarm', ax=ax)
    return fig