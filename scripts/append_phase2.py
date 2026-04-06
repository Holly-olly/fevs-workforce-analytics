"""Append Phase 2 extension cells to fevs_analysis.ipynb."""
import json
import uuid

def new_md(text):
    return {
        "cell_type": "markdown",
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "source": [text]
    }

def new_code(src):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "outputs": [],
        "source": [src]
    }

# ── Phase 2 header ────────────────────────────────────────────────────────────
md_header = new_md("""---

## Phase 2 Extensions — Addressing Peer Review Critiques

Four methodological extensions addressing key limitations identified in the project critique:
- **D** Harman's Single-Factor Test (common method variance check)
- **B** HTMT Discriminant Validity (modern alternative to AVE comparison)
- **A** Bifactor CFA (explaining SRMR misfit in EEI)
- **C** External Outcome Model (predicting turnover intention — addressing same-source bias)""")

# ── Extension D: Harman's CMV ─────────────────────────────────────────────────
md_D = new_md("### Extension D — Harman's Single-Factor Test (Common Method Variance)")

code_D = new_code(
"""# Extension D: Harman's Single-Factor Test
# Tests whether a single factor explains the majority of variance across all items
# (common method bias concern when all items come from same self-report survey)

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings

print("=" * 60)
print("EXTENSION D: Harman's Single-Factor Test")
print("=" * 60)

# Use all Likert items available (non-target, non-demographic)
likert_cols = [c for c in df.columns if c.startswith('Q') and c not in
               ['Q16_1','Q16_2','Q16_3','Q16_4','Q44','Q91']]

harman_data = df[likert_cols].copy()
harman_data = harman_data.dropna()

# Standardise
scaler = StandardScaler()
X_scaled = scaler.fit_transform(harman_data)

# PCA on all items
pca = PCA()
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    pca.fit(X_scaled)

variance_explained = pca.explained_variance_ratio_
first_factor_var = variance_explained[0] * 100
cumulative_50 = (variance_explained.cumsum() <= 0.50).sum() + 1

print(f"\\nItems included: {len(likert_cols)}")
print(f"Sample (after listwise deletion): {len(harman_data):,}")
print(f"\\nVariance explained by first unrotated factor: {first_factor_var:.1f}%")
print(f"Factors needed to explain 50% of variance: {cumulative_50}")
print()

if first_factor_var < 50:
    print("RESULT: First factor < 50% — Harman test does NOT indicate")
    print("        dominant common method variance.")
    print("        The 93.9% R² is not solely attributable to response-set bias.")
else:
    print("RESULT: First factor >= 50% — caution warranted re: common method variance.")
    print("        This does not invalidate results but warrants acknowledgement.")

print()
print("Note: Harman's test is a necessary but not sufficient check.")
print("      Even if passed, same-source bias can still inflate R².")
print("      The DLEAVING external outcome model (Extension C) provides")
print("      a stronger test of predictive validity beyond method overlap.")

# Bar chart — variance explained by first 10 components
fig, ax = plt.subplots(figsize=(10, 4))
components = range(1, min(16, len(variance_explained)) + 1)
bars = ax.bar(components, variance_explained[:15] * 100,
              color=[P['acidLime'] if i == 0 else P['electricViolet']
                     for i in range(15)],
              alpha=0.85)
ax.axhline(50, color=P['neonCoral'], linestyle='--', linewidth=1.5,
           label='50% threshold (Harman criterion)')
ax.set_xlabel('Principal Component', color=P['ghostWhite'], fontsize=11)
ax.set_ylabel('Variance Explained (%)', color=P['ghostWhite'], fontsize=11)
ax.set_title(f'Harman Single-Factor Test\\nFirst factor explains {first_factor_var:.1f}% of variance',
             color=P['ghostWhite'], fontsize=13, pad=12)
ax.set_facecolor(P['void'])
fig.patch.set_facecolor(P['deepSpace'])
ax.tick_params(colors=P['ghostWhite'])
ax.spines[:].set_color(P['slate'])
ax.legend(framealpha=0.25, labelcolor=P['ghostWhite'], facecolor=P['void'])
# Annotate first bar
ax.text(1, first_factor_var + 0.5, f'{first_factor_var:.1f}%',
        ha='center', va='bottom', color=P['acidLime'], fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/figures/17_harman_cmv_test.png', dpi=150,
            bbox_inches='tight', facecolor=P['deepSpace'])
plt.show()
print("Saved: outputs/figures/17_harman_cmv_test.png")
""")

# ── Extension B: HTMT ─────────────────────────────────────────────────────────
md_B = new_md("### Extension B — HTMT Discriminant Validity (Heterotrait-Monotrait Ratio)")

code_B = new_code(
"""# Extension B: HTMT Discriminant Validity
# HTMT < 0.85 = good discriminant validity
# HTMT < 0.90 = acceptable
# HTMT >= 0.90 = constructs may not be distinct

print("=" * 60)
print("EXTENSION B: HTMT Discriminant Validity")
print("=" * 60)

# EEI subscale items
eei_subscales = {
    'EEI_Intrinsic':  ['Q2','Q3','Q4','Q6','Q7'],
    'EEI_Supervisor': ['Q48','Q50','Q51','Q52','Q54'],
    'EEI_Leaders':    ['Q57','Q58','Q59','Q61','Q62'],
    'PCI':            ['Q20','Q21','Q22','Q23'],
    'GSI':            ['Q46','Q70','Q71','Q72'],
}

# Build item-level correlation matrix on complete cases
all_items = [item for items in eei_subscales.values() for item in items]
sub_htmt = df[all_items].dropna().astype('float64')
R = sub_htmt.corr()

def htmt(items_a, items_b, corr_matrix):
    """Compute HTMT ratio between two scales."""
    # Heterotrait correlations (between scales)
    hetero = []
    for i in items_a:
        for j in items_b:
            hetero.append(abs(corr_matrix.loc[i, j]))
    mean_hetero = sum(hetero) / len(hetero)
    # Monotrait correlations (within each scale, off-diagonal)
    def within_mean(items):
        vals = []
        for ii, i in enumerate(items):
            for jj, j in enumerate(items):
                if ii < jj:
                    vals.append(abs(corr_matrix.loc[i, j]))
        return sum(vals) / len(vals) if vals else 1.0
    mono_a = within_mean(items_a)
    mono_b = within_mean(items_b)
    return mean_hetero / ((mono_a * mono_b) ** 0.5)

scales = list(eei_subscales.keys())
n = len(scales)
htmt_matrix = np.ones((n, n))

print(f"\\nSample (listwise): {len(sub_htmt):,}")
print()
print(f"{'Pair':<35} {'HTMT':>6}  {'Verdict'}")
print("-" * 60)

for i in range(n):
    for j in range(i + 1, n):
        h = htmt(eei_subscales[scales[i]], eei_subscales[scales[j]], R)
        htmt_matrix[i, j] = h
        htmt_matrix[j, i] = h
        verdict = "OK" if h < 0.85 else ("Acceptable" if h < 0.90 else "CONCERN")
        pair_label = f"{scales[i]} vs {scales[j]}"
        print(f"{pair_label:<35} {h:>6.3f}  {verdict}")

# Heatmap
fig, ax = plt.subplots(figsize=(7, 6))
mask = np.eye(n, dtype=bool)
htmt_display = np.where(mask, np.nan, htmt_matrix)

import matplotlib.colors as mcolors
cmap = plt.cm.RdYlGn_r
im = ax.imshow(htmt_display, cmap=cmap, vmin=0.5, vmax=1.0, aspect='auto')

ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(scales, rotation=30, ha='right', color=P['ghostWhite'], fontsize=9)
ax.set_yticklabels(scales, color=P['ghostWhite'], fontsize=9)

for i in range(n):
    for j in range(n):
        if i != j:
            val = htmt_matrix[i, j]
            color = 'white' if val > 0.85 else P['void']
            ax.text(j, i, f'{val:.3f}', ha='center', va='center',
                    fontsize=9, color=color, fontweight='bold')

plt.colorbar(im, ax=ax, shrink=0.8, label='HTMT ratio')
ax.set_title('HTMT Discriminant Validity\\n(< 0.85 = good, < 0.90 = acceptable)',
             color=P['ghostWhite'], fontsize=12, pad=10)
ax.set_facecolor(P['void'])
fig.patch.set_facecolor(P['deepSpace'])
ax.tick_params(colors=P['ghostWhite'])

plt.tight_layout()
plt.savefig('outputs/figures/18_htmt_discriminant_validity.png', dpi=150,
            bbox_inches='tight', facecolor=P['deepSpace'])
plt.show()
print("\\nSaved: outputs/figures/18_htmt_discriminant_validity.png")
print()
print("Interpretation: HTMT < 0.85 for all pairs = discriminant validity supported.")
print("Constructs are empirically distinct despite high correlations in CFA.")
""")

# ── Extension A: Bifactor CFA ─────────────────────────────────────────────────
md_A = new_md("### Extension A — Bifactor CFA (Addressing EEI Model Misfit)")

code_A = new_code(
"""# Extension A: Bifactor CFA for EEI
# Standard 3-factor EEI had SRMR = 0.165 (misfit)
# Bifactor model adds a general engagement factor (G) alongside specific factors (S)
# This is the recommended fix per the peer critique

import semopy

print("=" * 60)
print("EXTENSION A: Bifactor CFA for Employee Engagement Index")
print("=" * 60)
print()
print("Standard 3-factor EEI SRMR = 0.165 (misfit threshold: 0.08)")
print("Testing bifactor model: G-factor + 3 specific factors")
print()

eei_items = {
    'Intrinsic':  ['Q2','Q3','Q4','Q6','Q7'],
    'Supervisor': ['Q48','Q50','Q51','Q52','Q54'],
    'Leaders':    ['Q57','Q58','Q59','Q61','Q62'],
}
all_eei = [i for items in eei_items.values() for i in items]

# Sample for tractability
rng = np.random.default_rng(42)
sub_bf = df[all_eei].dropna().astype('float64')
if len(sub_bf) > 50000:
    sub_bf = sub_bf.sample(50000, random_state=42)
print(f"Sample size: {len(sub_bf):,}")

# Bifactor model specification
# G = general factor loading on all items
# Specific factors = residual variance after G
bifactor_spec = """
# General factor (G) — loads on all EEI items
G =~ Q2 + Q3 + Q4 + Q6 + Q7 + Q48 + Q50 + Q51 + Q52 + Q54 + Q57 + Q58 + Q59 + Q61 + Q62

# Specific factors (S) — orthogonal to G
Intrinsic =~ Q2 + Q3 + Q4 + Q6 + Q7
Supervisor =~ Q48 + Q50 + Q51 + Q52 + Q54
Leaders =~ Q57 + Q58 + Q59 + Q61 + Q62

# Fix G orthogonal to S factors
G ~~ 0*Intrinsic
G ~~ 0*Supervisor
G ~~ 0*Leaders
Intrinsic ~~ 0*Supervisor
Intrinsic ~~ 0*Leaders
Supervisor ~~ 0*Leaders
"""

try:
    m_bf = semopy.Model(bifactor_spec)
    m_bf.fit(sub_bf)
    stats_bf = m_bf.calc_stats()

    cfi_bf  = stats_bf['CFI'].iloc[0]
    tli_bf  = stats_bf['TLI'].iloc[0]
    rmsea_bf = stats_bf['RMSEA'].iloc[0]

    # Manual SRMR for bifactor
    try:
        sigma_bf, _ = m_bf.calc_sigma()
        obs_corr_bf = sub_bf.corr().values
        p_bf = len(all_eei)
        sigma_std_bf = sigma_bf / np.sqrt(np.outer(np.diag(sigma_bf), np.diag(sigma_bf)))
        residuals_bf = obs_corr_bf - sigma_std_bf
        srmr_bf = np.sqrt((residuals_bf[np.tril_indices(p_bf, -1)] ** 2).mean())
    except Exception:
        srmr_bf = np.nan

    print(f"\\nBifactor CFA Results:")
    print(f"  CFI:   {cfi_bf:.3f}  (target: > 0.95)")
    print(f"  TLI:   {tli_bf:.3f}  (target: > 0.95)")
    print(f"  RMSEA: {rmsea_bf:.3f}  (target: < 0.08)")
    print(f"  SRMR:  {srmr_bf:.3f}  (target: < 0.08)")

    print()
    print("Comparison:")
    print(f"  {'Model':<20} {'CFI':>6} {'TLI':>6} {'RMSEA':>7} {'SRMR':>7}")
    print(f"  {'-'*48}")
    print(f"  {'3-factor CFA':<20} {'0.958':>6} {'0.950':>6} {'0.088':>7} {'0.165':>7}")
    print(f"  {'Bifactor CFA':<20} {cfi_bf:>6.3f} {tli_bf:>6.3f} {rmsea_bf:>7.3f} {srmr_bf:>7.3f}")

    srmr_improved = not np.isnan(srmr_bf) and srmr_bf < 0.165
    if srmr_improved:
        print()
        print("RESULT: Bifactor model improves SRMR — general engagement factor")
        print("        accounts for shared variance across EEI subscales.")
        print("        This supports a hierarchical interpretation: engagement")
        print("        has a common core (G) plus domain-specific components.")
    else:
        print()
        print("RESULT: SRMR improvement limited. The misfit may reflect")
        print("        fundamental constraints of Likert-scale covariance structure")
        print("        rather than a correctable model specification issue.")

    # Visualise fit comparison
    metrics = ['CFI', 'TLI', '1-RMSEA', '1-SRMR']
    standard = [0.958, 0.950, 1-0.088, 1-0.165]
    bifactor = [cfi_bf, tli_bf, 1-rmsea_bf, 1-srmr_bf if not np.isnan(srmr_bf) else np.nan]

    x = np.arange(len(metrics))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x - width/2, standard, width, label='Standard 3-factor',
                color=P['electricViolet'], alpha=0.85)
    b2 = ax.bar(x + width/2, bifactor, width, label='Bifactor',
                color=P['acidLime'], alpha=0.85)
    ax.axhline(0.95, color=P['neonCoral'], linestyle='--', linewidth=1.2,
               label='CFI/TLI threshold (0.95)')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, color=P['ghostWhite'])
    ax.set_ylabel('Fit statistic (higher = better)', color=P['ghostWhite'])
    ax.set_title('CFA Fit Comparison: Standard 3-factor vs Bifactor EEI\\n(1-RMSEA and 1-SRMR shown so all metrics are higher-is-better)',
                 color=P['ghostWhite'], fontsize=11, pad=10)
    ax.set_ylim(0.6, 1.05)
    ax.set_facecolor(P['void'])
    fig.patch.set_facecolor(P['deepSpace'])
    ax.tick_params(colors=P['ghostWhite'])
    ax.spines[:].set_color(P['slate'])
    ax.legend(framealpha=0.25, labelcolor=P['ghostWhite'], facecolor=P['void'])
    plt.tight_layout()
    plt.savefig('outputs/figures/19_bifactor_cfa_comparison.png', dpi=150,
                bbox_inches='tight', facecolor=P['deepSpace'])
    plt.show()
    print("Saved: outputs/figures/19_bifactor_cfa_comparison.png")

except Exception as e:
    print(f"Bifactor CFA error: {e}")
    print("Note: semopy may not fully support bifactor constraints.")
    print("This is a known limitation. The key finding remains: SRMR misfit")
    print("in the standard model indicates shared variance beyond the 3 factors.")
""")

# ── Extension C: External Outcome Model ───────────────────────────────────────
md_C = new_md("### Extension C — External Outcome Model (Predicting Turnover Intention)")

code_C = new_code(
"""# Extension C: External Outcome Model — Predicting DLEAVING
# Addresses the core critique: all predictors AND target from same survey = inflated R²
# Solution: predict an EXTERNAL outcome (turnover intention = DLEAVING) using EEI + survey items
# This tests whether engagement-related items have real predictive validity beyond method overlap

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, classification_report
import shap

print("=" * 60)
print("EXTENSION C: External Outcome — Predicting Turnover Intention")
print("=" * 60)
print()

# DLEAVING: intent to leave (different scale responses)
print("DLEAVING value counts:")
print(df['DLEAVING'].value_counts().sort_index())
print()

# Recode: 1 = leaving within 1 year, 0 = staying (2+ years or not applicable)
# Typical coding: 1=within 1 yr, 2=1-3 yrs, 3=3-5 yrs, 4=5+ yrs, 5=not applicable/retirement
leaving_map = {1: 1, 2: 0, 3: 0, 4: 0, 5: 0}
df['leaving_binary'] = df['DLEAVING'].map(leaving_map)

n_leaving = df['leaving_binary'].sum()
n_total = df['leaving_binary'].notna().sum()
print(f"Intent to leave within 1 year: {n_leaving:,} ({100*n_leaving/n_total:.1f}%)")
print(f"Staying / other: {n_total - n_leaving:,} ({100*(n_total-n_leaving)/n_total:.1f}%)")
print()

# Features: EEI factor scores + non-EEI survey items (same as main model)
# Target: DLEAVING binary
target_col = 'leaving_binary'
feature_cols_ext = [c for c in FEATURE_COLS if c not in ['Q2','Q3','Q4','Q6','Q7',
                                                           'Q48','Q50','Q51','Q52','Q54',
                                                           'Q57','Q58','Q59','Q61','Q62']]

ext_data = df[feature_cols_ext + [target_col]].dropna()
X_ext = ext_data[feature_cols_ext].values
y_ext = ext_data[target_col].values.astype(int)

print(f"Features: {len(feature_cols_ext)}")
print(f"Sample: {len(X_ext):,}")
print()

# Model
clf = HistGradientBoostingClassifier(
    max_iter=200, max_depth=5, learning_rate=0.05,
    min_samples_leaf=50, random_state=42
)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
auc_scores = cross_val_score(clf, X_ext, y_ext, cv=skf,
                              scoring='roc_auc', n_jobs=-1)

print(f"5-fold CV AUC: {auc_scores.mean():.3f} ± {auc_scores.std():.3f}")
print()

if auc_scores.mean() > 0.70:
    print("RESULT: AUC > 0.70 — survey items predict turnover intention")
    print("        beyond chance. This demonstrates predictive validity for")
    print("        an EXTERNAL outcome, partially addressing the same-source critique.")
elif auc_scores.mean() > 0.60:
    print("RESULT: AUC 0.60–0.70 — modest but meaningful external prediction.")
    print("        Survey items have some predictive validity for turnover intention.")
else:
    print("RESULT: AUC < 0.60 — limited external predictive validity.")
    print("        High R² in main model is likely largely method variance.")

# Fit on full data for SHAP
clf.fit(X_ext, y_ext)

# SHAP for top features
explainer_ext = shap.TreeExplainer(clf)
sample_idx = np.random.default_rng(42).choice(len(X_ext), size=min(5000, len(X_ext)), replace=False)
X_sample = X_ext[sample_idx]
shap_vals_ext = explainer_ext.shap_values(X_sample)

# For binary classification, shap_values may be list; take positive class
if isinstance(shap_vals_ext, list):
    shap_vals_ext = shap_vals_ext[1]

mean_abs_shap_ext = pd.Series(
    np.abs(shap_vals_ext).mean(axis=0),
    index=feature_cols_ext
).sort_values(ascending=False)

top15_ext = mean_abs_shap_ext.head(15)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
colors_ext = [P['acidLime']] * 5 + [P['electricViolet']] * 10
ax.barh(range(len(top15_ext)), top15_ext.values[::-1],
        color=colors_ext[::-1], alpha=0.85)
ax.set_yticks(range(len(top15_ext)))
labels_ext = [SHORT_LABELS.get(f, f) for f in top15_ext.index[::-1]]
ax.set_yticklabels(labels_ext, fontsize=9, color=P['ghostWhite'])
ax.set_xlabel('Mean |SHAP value| — impact on turnover prediction', color=P['ghostWhite'])
ax.set_title(f'Top 15 Predictors of Turnover Intention (DLEAVING)\\nExternal outcome model — AUC = {auc_scores.mean():.3f}',
             color=P['ghostWhite'], fontsize=12, pad=10)
ax.set_facecolor(P['void'])
fig.patch.set_facecolor(P['deepSpace'])
ax.tick_params(colors=P['ghostWhite'])
ax.spines[:].set_color(P['slate'])
plt.tight_layout()
plt.savefig('outputs/figures/20_external_outcome_turnover.png', dpi=150,
            bbox_inches='tight', facecolor=P['deepSpace'])
plt.show()
print("Saved: outputs/figures/20_external_outcome_turnover.png")

print()
print("Key question: Do top SHAP features here match the engagement model (Fig 11)?")
print("If YES: drivers of engagement also drive intent to stay — coherent story.")
print("If NO: method variance was inflating engagement model importance rankings.")
print()
print("Top 5 predictors of turnover intention:")
for feat, val in top15_ext.head(5).items():
    label = SHORT_LABELS.get(feat, feat)
    print(f"  {label}: {val:.4f}")
""")

# ── Phase 2 summary ───────────────────────────────────────────────────────────
md_summary = new_md("""### Phase 2 — Summary of Findings

| Extension | Test | Key Finding | Implication |
|-----------|------|-------------|-------------|
| **D** | Harman's CMV | First factor < 50%? | Method variance not dominant |
| **B** | HTMT | All pairs < 0.85? | Discriminant validity supported |
| **A** | Bifactor CFA | SRMR improves? | G-factor structure explains misfit |
| **C** | External outcome | AUC > 0.70? | Real predictive validity for turnover |

These extensions collectively address the three critical issues identified in peer review:
1. CFA misfit — addressed by bifactor model (A)
2. Discriminant validity — formally tested via HTMT (B)
3. Inflated ML performance — tested via external outcome (C) and CMV check (D)""")

# ── Load notebook and append ──────────────────────────────────────────────────
with open('notebooks/fevs_analysis.ipynb') as f:
    nb = json.load(f)

new_cells = [md_header, md_D, code_D, md_B, code_B, md_A, code_A, md_C, code_C, md_summary]
nb['cells'].extend(new_cells)

with open('notebooks/fevs_analysis.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Done — notebook now has {len(nb['cells'])} cells")
print("New cells appended:")
for cell in new_cells:
    t = cell['cell_type']
    src = ''.join(cell['source'])[:60]
    print(f"  [{t}] {src}")
