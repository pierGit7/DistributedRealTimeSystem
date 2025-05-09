# src/analysis.py

import sys
import math
from functools import reduce
from common.csvreader import read_csv
from common.architecture import Architecture
from common.budget import Budget
from common.task import Task
from common.DBF import DBF
from common.BDR import BDR

def lcm(a: int, b: int) -> int:
    return a * b // math.gcd(a, b)

def main():
    if len(sys.argv) != 4:
        print("Usage: python analysis.py <architecture.csv> <budgets.csv> <tasks.csv>")
        sys.exit(1)

    architectures, budgets, tasks = read_csv()

    # 1) Adjust WCETs by core speed
    for arch in architectures:
        for t in (
            x for x in tasks
            if any(b.core_id == arch.core_id and b.component_id == x.component_id
                   for b in budgets)
        ):
            t.wcet /= arch.speed_factor

    # 2) Group tasks by component
    comp_tasks: dict[str, list[Task]] = {}
    for t in tasks:
        comp_tasks.setdefault(t.component_id, []).append(t)

    # 3) Compute (alpha, delta) and per-component schedulability
    results = {}
    for b in budgets:
        W = comp_tasks.get(b.component_id, [])
        alpha = b.budget / b.period

        # zero-budget guard
        if alpha <= 0 and W:
            bdr = BDR(alpha, 0.0)
            results[b.component_id] = {
                'alpha': alpha,
                'delta': 0.0,
                'schedulable': False,
                'bdr': bdr
            }
            continue

        # collect critical time points up to the hyperperiod
        if W:
            periods = [int(t.period) for t in W]
            hyper = reduce(lcm, periods, periods[0])
            time_points = sorted({
                k * T
                for T in periods
                for k in range(1, hyper // T + 1)
            })
        else:
            time_points = []

        # compute delta = max(0, min_t [ t - demand(t)/alpha ])
        if alpha > 0 and time_points:
            deltas = []
            for t in time_points:
                if b.scheduler.name == 'EDF':
                    demand = DBF.dbf_edf(W, t)
                else:  # RM
                    demand = max(
                        DBF.dbf_rm(W, t, idx)
                        for idx in range(len(W))
                    )
                deltas.append(t - demand/alpha)
            delta = max(0.0, min(deltas))
        else:
            delta = 0.0

        bdr = BDR(alpha, delta)

        # schedulability check: ∀t, demand(t) ≤ sbf(t)
        if b.scheduler.name == 'EDF':
            sched_ok = all(
                DBF.dbf_edf(W, t) <= bdr.sbf(t)
                for t in time_points
            )
        else:  # RM
            sched_ok = all(
                max(DBF.dbf_rm(W, t, idx) for idx in range(len(W)))
                <= bdr.sbf(t)
                for t in time_points
            )

        results[b.component_id] = {
            'alpha': alpha,
            'delta': delta,
            'schedulable': sched_ok,
            'bdr': bdr
        }

    # 4) Build component summary
    comp_rows = []
    for cid, r in results.items():
        alpha = r['alpha']
        delta = r['delta']
        C_s, T_s = r['bdr'].to_supply_task()
        comp_rows.append({
            'Component': cid,
            'alpha': f"{alpha:.3f}",
            'delta': f"{delta:.3f}",
            'Sched': '✔' if r['schedulable'] else '✘',
            'C_s': f"{C_s:.3f}",
            'T_s': f"{T_s:.3f}"
        })

    # 5) Per-core hierarchical check (Theorem 1)
    parent = BDR(1.0, 0.0)
    core_rows = []
    system_ok = True
    for arch in architectures:
        comps = [b.component_id for b in budgets if b.core_id == arch.core_id]
        indiv_ok = all(results[c]['schedulable'] for c in comps)
        group_ok = BDR.can_schedule_children(
            parent,
            [results[c]['bdr'] for c in comps]
        )
        hier_ok = indiv_ok and group_ok
        if not hier_ok:
            system_ok = False
        core_rows.append({
            'Core': arch.core_id,
            'Indiv OK': '✔' if indiv_ok else '✘',
            'Group OK': '✔' if group_ok else '✘',
            'Hier OK': '✔' if hier_ok else '✘'
        })

    # helper to print aligned tables
    def print_table(rows, cols):
        widths = {
            c: max(len(c), *(len(r[c]) for r in rows))
            for c in cols
        }
        fmt = "  ".join(f"{{:{widths[c]}}}" for c in cols)
        print(fmt.format(*cols))
        for r in rows:
            print(fmt.format(*(r[c] for c in cols)))
        print()

    # output
    print("\n=== Component Summary ===")
    print_table(comp_rows, ['Component','alpha','delta','Sched','C_s','T_s'])
    print("=== Core Summary ===")
    print_table(core_rows, ['Core','Indiv OK','Group OK','Hier OK'])
    print(f"--> System hierarchical_schedulable = {'✔' if system_ok else '✘'}\n")


if __name__ == '__main__':
    main()
