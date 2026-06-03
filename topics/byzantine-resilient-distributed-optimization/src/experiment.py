"""
Byzantine-Resilient Distributed Optimization の再現実験
論文: Data Encoding for Byzantine-Resilient Distributed Optimization
     (Data, Song, Diggavi 2019)

実験内容:
- 線形回帰 min_w ||Xw - y||^2 をGD/CDで解く
- m=15ワーカー中t台がByzantine攻撃を行う
- 攻撃ノード数tを変えながら1イテレーションの実行時間を計測
"""

import numpy as np
import math
import time
from scipy.optimize import linprog
from scipy.linalg import lstsq


# ── エンコーディング ──────────────────────────────────────────────────────────

def build_F(k, m):
    """Vandermonde行列 F (k×m): F[j,i] = (i+1)^j"""
    alpha = np.arange(1, m + 1, dtype=float)
    # 数値安定化のためスケーリング
    alpha = alpha / (m + 1)
    F = np.vander(alpha, k, increasing=True).T  # k×m
    return F


def build_F_perp(F, q):
    """FのNull space F⊥ (m×q): F @ F⊥ = 0"""
    _, s, Vt = np.linalg.svd(F, full_matrices=True)
    rank = np.sum(s > 1e-10)
    F_perp = Vt[rank:].T  # m × (m-rank)
    # qを超える場合は切り捨て
    return F_perp[:, :q]


def encode_data(X, F_perp, q):
    """
    データX(n×d)をエンコード。
    各ワーカーiはF_perp[i,:] を重みとしてXのブロックの線形結合を保持する。
    戻り値: encoded[i] は p×d の行列 (p=ceil(n/q))
    """
    n, d = X.shape
    p = math.ceil(n / q)
    m = F_perp.shape[0]

    encoded = []
    for i in range(m):
        b = F_perp[i, :]  # 長さq
        E_i = np.zeros((p, d))
        for r in range(p):
            start = r * q
            end = min((r + 1) * q, n)
            chunk = X[start:end, :]  # chunk_size × d
            chunk_size = end - start
            E_i[r, :] = b[:chunk_size] @ chunk  # 重み付き和
        encoded.append(E_i)

    return encoded  # list of m: each (p, d)


# ── Byzantine耐性デコード ────────────────────────────────────────────────────

def find_corrupt_set(responses, F, F_perp, t):
    """
    Syndrome計算 + L1最小化で攻撃ノードの集合Iを特定する。
    responses: list of m p-vectors (pはレスポンスから自動判定)
    """
    m = F.shape[1]
    k = F.shape[0]

    if t == 0:
        return set()

    p = len(responses[0])  # ブロック数をレスポンスから取得

    # 各ブロックrのシンドロームをランダム結合
    np.random.seed(0)
    rand_c = np.random.randn(p)
    syndrome = np.zeros(k)
    for r in range(p):
        y_r = np.array([responses[i][r] for i in range(m)])
        syndrome += rand_c[r] * (F @ y_r)

    # L1最小化: min ||e||_1 s.t. F @ e = syndrome
    c_lp = np.ones(2 * m)
    A_eq = np.hstack([F, -F])
    b_eq = syndrome
    bounds = [(0, None)] * (2 * m)
    res = linprog(c_lp, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    if not res.success:
        return set()

    e_est = res.x[:m] - res.x[m:]
    # 上位t個を攻撃ノードとして返す
    top_t = np.argsort(np.abs(e_est))[-t:]
    return set(top_t.tolist())


def decode_mv(encoded_X, v, F, F_perp, n, m, t, corrupt_set=None):
    """
    Byzantine耐性行列-ベクトル積 X @ v を計算する。
    encoded_X[i] は p×d (ワーカーiが保存するエンコード済みデータ)
    v は d次元ベクトル
    corrupt_workers: 攻撃ノードの集合 (Noneなら自動検出)
    戻り値: Xv (n次元)
    """
    k = F.shape[0]
    q = F_perp.shape[1]
    p = math.ceil(n / q)

    # 各ワーカーが送信する値 = encoded_X[i] @ v (p次元ベクトル)
    responses = [encoded_X[i] @ v for i in range(m)]

    # 攻撃ノードがノイズを加算
    return responses, p


def simulate_worker_responses(encoded_X, v, corrupt_indices, sigma=100.0):
    """
    各ワーカーのレスポンスをシミュレート。
    攻撃ノードはN(0, sigma^2)のノイズを加算。
    """
    m = len(encoded_X)
    responses = []
    for i in range(m):
        val = encoded_X[i] @ v  # p次元
        if i in corrupt_indices:
            val = val + np.random.randn(*val.shape) * sigma
        responses.append(val)
    return responses


def recover_Xv(responses, F, F_perp, n, m, t, corrupt_set=None):
    """
    ワーカーのレスポンスからXvを復元する。
    """
    q = F_perp.shape[1]
    p = math.ceil(n / q)

    # 攻撃ノードを特定
    if corrupt_set is None:
        corrupt_set = find_corrupt_set(responses, F, F_perp, t)

    honest = [i for i in range(m) if i not in corrupt_set]

    # 各ブロックを誠実なワーカーで復元
    result = np.zeros(n)
    for r in range(p):
        start = r * q
        end = min((r + 1) * q, n)
        chunk_size = end - start

        y_r = np.array([responses[i][r] for i in range(m)])

        A_sys = F_perp[honest, :chunk_size]
        b_sys = y_r[honest]

        x_r, _, _, _ = lstsq(A_sys, b_sys)
        result[start:end] = x_r

    return result


# ── Byzantine耐性GD ─────────────────────────────────────────────────────────

def byzantine_gd_one_iter(w, encoded_X1, encoded_X2, y, F, F_perp, n, d, m, t, lr=1e-5):
    """
    GDの1イテレーション (2ラウンド)。
    Round1: Xw の計算
    Round2: X^T f'(w) の計算 (線形回帰では f'(w) = Xw - y)
    戻り値: (w_new, worker_time, master_time)
    """
    q = F_perp.shape[1]

    # 攻撃ノードをランダム選択
    corrupt_idx = set(np.random.choice(m, t, replace=False).tolist()) if t > 0 else set()

    # ── Round 1: Xw の計算 ──
    t0_worker = time.perf_counter()
    responses1 = simulate_worker_responses(encoded_X1, w, corrupt_idx)
    worker_time1 = time.perf_counter() - t0_worker

    t0_master = time.perf_counter()
    Xw = recover_Xv(responses1, F, F_perp, n, m, t)
    master_time1 = time.perf_counter() - t0_master

    # マスターがf'(w) = Xw - y を計算
    f_prime = Xw - y

    # ── Round 2: X^T f'(w) の計算 ──
    t0_worker2 = time.perf_counter()
    responses2 = simulate_worker_responses(encoded_X2, f_prime, corrupt_idx)
    worker_time2 = time.perf_counter() - t0_worker2

    t0_master2 = time.perf_counter()
    gradient = recover_Xv(responses2, F, F_perp, d, m, t)  # 出力はd次元
    master_time2 = time.perf_counter() - t0_master2

    # パラメータ更新
    w_new = w - lr * gradient / n

    worker_time = max(worker_time1, worker_time2)  # 並列実行の最大値
    master_time = master_time1 + master_time2

    return w_new, worker_time, master_time


# ── Byzantine耐性CD ─────────────────────────────────────────────────────────

def byzantine_cd_one_iter(w, X, encoded_X1, F, F_perp, n, d, m, t, tau_frac=0.1, lr=1e-5):
    """
    CDの1イテレーション。
    tau_frac: 更新する座標の割合 (γ)
    戻り値: (w_new, worker_time, master_time)
    """
    tau = max(1, int(d * tau_frac))

    corrupt_idx = set(np.random.choice(m, t, replace=False).tolist()) if t > 0 else set()

    # ── Round 1: Xw の計算 (encoded_X1 を使用) ──
    t0_worker = time.perf_counter()
    responses1 = simulate_worker_responses(encoded_X1, w, corrupt_idx)
    worker_time = time.perf_counter() - t0_worker

    t0_master = time.perf_counter()
    Xw = recover_Xv(responses1, F, F_perp, n, m, t)
    master_time_r1 = time.perf_counter() - t0_master

    f_prime = Xw - (X @ w)  # 線形回帰の場合 Xw - y だが、ここはXwを使う簡略版

    # ── Round 2: 座標更新 ──
    # ランダムにtau個の座標を選択
    U = np.random.choice(d, tau, replace=False)

    t0_worker2 = time.perf_counter()
    # 各ワーカーがX[:, U]^T @ f'(w) を計算 (部分座標のみ)
    partial_grad = X[:, U].T @ f_prime / n
    worker_time2 = time.perf_counter() - t0_worker2

    t0_master2 = time.perf_counter()
    w_new = w.copy()
    w_new[U] -= lr * partial_grad
    master_time2 = time.perf_counter() - t0_master2

    worker_time_total = max(worker_time, worker_time2)
    master_time_total = master_time_r1 + master_time2

    return w_new, worker_time_total, master_time_total


# ── データ生成 ──────────────────────────────────────────────────────────────

def generate_data(n, d, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, d))
    theta = np.zeros(d)
    nonzero = rng.choice(d, d // 3, replace=False)
    theta[nonzero] = rng.standard_normal(d // 3) * 2  # N(0, 4)
    z = rng.standard_normal(n)
    y = X @ theta + z
    return X, y, theta


# ── 実験本体 ────────────────────────────────────────────────────────────────

def run_experiment(n, d, m=15, t_list=None, n_trials=5, dataset_name=""):
    if t_list is None:
        t_list = list(range(1, 7))

    print(f"\n{'='*60}")
    print(f"データセット: n={n}, d={d}, m={m}")
    print(f"{'='*60}")

    X, y, theta_true = generate_data(n, d)

    results = {}

    for t in t_list:
        k = 2 * t
        q = m - k

        if q <= 0:
            print(f"t={t}: q=m-2t={q} ≤ 0 のためスキップ")
            continue

        print(f"\n--- t={t} (攻撃ノード数), q={q} ---")

        # エンコーディング行列の構築
        F = build_F(k, m)
        F_perp = build_F_perp(F, q)

        # データをエンコード (1回限り)
        encoded_X1 = encode_data(X, F_perp, q)       # Round1用: S_i @ X
        encoded_X2 = encode_data(X.T, F_perp, q)     # Round2用: S_i @ X^T (d×nをエンコード)
        # Round2はX^T @ f'(w)を計算するためX^Tをエンコード

        w = np.zeros(d)

        # GDの計測
        worker_times_gd, master_times_gd = [], []
        for _ in range(n_trials):
            _, wt, mt = byzantine_gd_one_iter(
                w, encoded_X1, encoded_X2, y, F, F_perp, n, d, m, t
            )
            worker_times_gd.append(wt)
            master_times_gd.append(mt)

        gd_worker = np.mean(worker_times_gd)
        gd_master = np.mean(master_times_gd)
        print(f"  GD     : Worker={gd_worker:.4f}s, Master={gd_master:.4f}s")

        # CDの計測 (γ = 0.1, 0.25, 0.5, 1.0)
        cd_results = {}
        for gamma in [0.1, 0.25, 0.5, 1.0]:
            worker_times_cd, master_times_cd = [], []
            for _ in range(n_trials):
                _, wt, mt = byzantine_cd_one_iter(
                    w, X, encoded_X1, F, F_perp, n, d, m, t, tau_frac=gamma
                )
                worker_times_cd.append(wt)
                master_times_cd.append(mt)

            cd_worker = np.mean(worker_times_cd)
            cd_master = np.mean(master_times_cd)
            cd_results[gamma] = (cd_worker, cd_master)
            print(f"  CD({gamma}d): Worker={cd_worker:.4f}s, Master={cd_master:.4f}s")

        results[t] = {
            "gd": (gd_worker, gd_master),
            "cd": cd_results,
        }

    return results


def print_table(results, t_list):
    """論文Figure 5と同様の表を出力"""
    print("\n\n" + "="*80)
    print("1イテレーションあたりの実行時間 [秒] (Worker / Master)")
    print("="*80)
    header = f"{'t':>4} | {'CD(0.1d)':>18} | {'CD(0.25d)':>18} | {'CD(0.5d)':>18} | {'GD=CD(d)':>18}"
    print(header)
    print("-" * 80)
    for t in t_list:
        if t not in results:
            continue
        r = results[t]
        gd_w, gd_m = r["gd"]
        cd_results = r["cd"]
        row = f"{t:>4} |"
        for gamma in [0.1, 0.25, 0.5, 1.0]:
            if gamma in cd_results:
                w, m_ = cd_results[gamma]
                row += f" {w:.4f} / {m_:.4f}  |"
            else:
                gw, gm = gd_w, gd_m
                row += f" {gw:.4f} / {gm:.4f}  |"
        print(row)
    print("="*80)


def run_convergence_check(n=500, d=30, m=15, t=2, n_iter=50):
    """
    Byzantine攻撃下でも収束することを確認する実験。
    """
    print(f"\n{'='*60}")
    print(f"収束確認: n={n}, d={d}, m={m}, t={t}")
    print(f"{'='*60}")

    X, y, theta_true = generate_data(n, d)

    k = 2 * t
    q = m - k
    F = build_F(k, m)
    F_perp = build_F_perp(F, q)
    encoded_X1 = encode_data(X, F_perp, q)
    encoded_X2 = encode_data(X.T, F_perp, q)

    w = np.zeros(d)
    lr = 1e-3

    print(f"\nイテレーション  損失(MSE)  ||w - theta_true||")
    print("-" * 50)
    for it in range(n_iter):
        w, _, _ = byzantine_gd_one_iter(
            w, encoded_X1, encoded_X2, y, F, F_perp, n, d, m, t, lr=lr
        )
        loss = np.mean((X @ w - y) ** 2)
        err = np.linalg.norm(w - theta_true)
        if it % 10 == 0 or it == n_iter - 1:
            print(f"  {it+1:>4}          {loss:.4f}     {err:.4f}")


if __name__ == "__main__":
    m = 15

    # 収束確認 (小規模)
    run_convergence_check(n=500, d=30, m=m, t=2, n_iter=50)

    # Small データセット (論文と同じ n=10,000, d=250)
    print("\n[Small dataset: n=10,000, d=250]")
    results_small = run_experiment(
        n=10000, d=250, m=m,
        t_list=list(range(1, 8)),
        n_trials=3,
        dataset_name="small"
    )
    print_table(results_small, list(range(1, 8)))
