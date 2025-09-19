
"""
edge_ai.py
Lightweight online anomaly detector suitable for edge devices (STM32 simulation).
- Uses exponential moving average + variance to compute z-scores per sensor
- Produces an `anomaly_score` in [0, +inf); higher means more anomalous
- Adaptable (simple online learning): updates running stats each sample
This implementation is intentionally dependency-light and deterministic.
"""
import math

class EdgeAnomalyDetector:
    def __init__(self, alpha=0.05):
        # alpha: EMA smoothing factor. Lower -> slower adaptation.
        self.alpha = alpha
        # running mean and variance (for temp, vib, sound)
        self.stats = {
            'temp': {'mean': None, 'var': None},
            'vib' : {'mean': None, 'var': None},
            'sound': {'mean': None, 'var': None}
        }
        # small floor to variance to avoid division by zero
        self.var_floor = 1e-6

    def _update_stat(self, key, value):
        s = self.stats[key]
        if s['mean'] is None:
            s['mean'] = float(value)
            s['var'] = 0.0
            return
        old_mean = s['mean']
        # EMA update for mean
        new_mean = (1 - self.alpha) * old_mean + self.alpha * float(value)
        # EMA update for variance (using squared difference)
        # var_t = (1 - alpha) * var_{t-1} + alpha*(x - mean_{t-1})^2
        new_var = (1 - self.alpha) * s['var'] + self.alpha * (float(value) - old_mean) ** 2
        s['mean'] = new_mean
        s['var'] = max(new_var, self.var_floor)

    def update_and_score(self, sample):
        """
        sample: dict with keys 'temp', 'vib', 'sound'
        returns anomaly_score (float)
        """
        # update stats and compute abs z-scores
        z_sum = 0.0
        weight_map = {'temp': 0.5, 'vib': 1.5, 'sound': 0.8}  # vibration often more important
        for k in ['temp','vib','sound']:
            x = float(sample[k])
            # if first sample, initialize
            if self.stats[k]['mean'] is None:
                # initialize with value and small var
                self.stats[k]['mean'] = x
                self.stats[k]['var'] = 1e-4
                z = 0.0
            else:
                mean = self.stats[k]['mean']
                var = self.stats[k]['var'] + self.var_floor
                std = math.sqrt(var)
                z = abs((x - mean) / std)
            z_sum += weight_map[k] * z
            # update running stat AFTER scoring to avoid instant dampening
            self._update_stat(k, x)
        # anomaly score is z_sum normalized
        return round(z_sum, 4)
