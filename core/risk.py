def risk_reward(entry, stop, target):
    risk = entry - stop
    reward = target - entry
    if risk <= 0:
        return 0
    return reward / risk


def position_size(account_size, risk_percent, entry, stop):
    dollar_risk = account_size * (risk_percent / 100)
    risk_per_share = max(entry - stop, 0)
    if risk_per_share <= 0:
        return {
            "shares": 0,
            "dollar_risk": round(dollar_risk, 2),
            "risk_per_share": 0,
            "position_cost": 0,
            "max_loss": 0,
        }
    shares = int(dollar_risk // risk_per_share)
    return {
        "shares": shares,
        "dollar_risk": round(dollar_risk, 2),
        "risk_per_share": round(risk_per_share, 2),
        "position_cost": round(shares * entry, 2),
        "max_loss": round(shares * risk_per_share, 2),
    }


def trade_plan(entry, stop, targets, account_size=10000, risk_percent=1):
    sizing = position_size(account_size, risk_percent, entry, stop)
    rows = []
    for idx, target in enumerate(targets, start=1):
        rr = risk_reward(entry, stop, target)
        profit = sizing["shares"] * (target - entry)
        rows.append({
            "target": idx,
            "price": round(target, 2),
            "risk_reward": round(rr, 2),
            "expected_profit": round(profit, 2),
        })
    return sizing, rows
