import numpy as np
from scipy import stats
import random

def runs_test(x):
    """实现检验"""
    n = len(x)
    runs, n1, n2 = 1, sum(x), n - sum(x)
    
    for i in range(1, n):
        if x[i] != x[i-1]:
            runs += 1
    
    expected = (2 * n1 * n2) / n + 1
    std_dev = np.sqrt((2 * n1 * n2 * (2 * n1 * n2 - n)) / (n**2 * (n - 1)))
    z = (runs - expected) / std_dev
    pvalue = 2 * (1 - stats.norm.cdf(abs(z)))
    return pvalue

def proportion_test(count, nobs, value):
    """实现比例检验"""
    p = count / nobs
    se = np.sqrt(value * (1 - value) / nobs)
    z = (p - value) / se
    pvalue = 2 * (1 - stats.norm.cdf(abs(z)))
    return z, pvalue

def test_online_conformal_prediction():
    # 参数设置
    N = 10000  
    alpha = 0.1  
    random.seed(42)  
    
    # 模拟数据生成
    def generate_data(n):
        x = np.random.normal(0, 1, size=2)
        y = 1 if np.sum(x) > 0 else 0
        return x, y
    
    # 模拟共形预测器
    def mock_conformal_predictor(train_data, x_new, alpha=0.1):
        if random.random() > alpha:
            if train_data:
                _, last_y = train_data[-1]
                return {last_y, 1-last_y}
            return {0, 1}
        true_y = 1 if np.sum(x_new) > 0 else 0
        return {1 - true_y}
    
    # 运行流程
    errors = []
    train_data = []
    
    for n in range(1, N+1):
        x_new, y_new = generate_data(n)
        gamma = mock_conformal_predictor(train_data, x_new, alpha)
        errors.append(1 if y_new not in gamma else 0)
        train_data.append((x_new, y_new))
    
    # 验证错误率
    empirical_error = sum(errors) / N
    se = np.sqrt(alpha * (1 - alpha) / N)
    ci_low, ci_high = alpha - 1.96*se, alpha + 1.96*se
    print(f"Empirical error rate: {empirical_error:.4f} (expected: {alpha})")
    print(f"95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
    assert ci_low <= empirical_error <= ci_high
    
    # 验证分布性质
    runs_pvalue = runs_test(errors)
    _, prop_pvalue = proportion_test(sum(errors), N, alpha)
    print(f"Runs test p-value: {runs_pvalue:.4f}")
    print(f"Proportion test p-value: {prop_pvalue:.4f}")
    assert runs_pvalue > 0.01 and prop_pvalue > 0.01
    print("ok")

test_online_conformal_prediction()