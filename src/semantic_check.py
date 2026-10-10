"""Semantic check of generated CPMpy models against the ground truth, run after the CP-Bench pipeline.

under: exists a schedule the generated model accepts but the rule forbids   (one exact solve, real instance size)
over:  number of rule-valid schedules the generated model rejects           (exhaustive, 1 nurse x OVER_DAYS)
correct = no under-constraint and 0 over-rejections.

usage: python semantic_check.py <cp-bench results log.json>
"""
import sys, json, re, itertools, pathlib, contextlib, io
import cpmpy as cp
from cpmpy.transformations.get_variables import get_variables
from cpmpy.transformations.normalize import toplevel_list

OVER_DAYS = 7
N_NURSES, N_DAYS = 3, 14


def extract_code(answer):
    return answer.split("```python")[-1].split("```")[0] if "```python" in answer else None


def build(code, n_nurses, n_days):
    """Execute code up to (not including) solving; return the constraints and the schedule array."""
    code = re.sub(r"\bn_nurses\s*=\s*\d+", f"n_nurses = {n_nurses}", code)
    code = re.sub(r"\bn_days\s*=\s*\d+", f"n_days = {n_days}", code)
    captured = {}
    orig = cp.Model.solve
    def fake_solve(self, *a, **k):
        captured["model"] = self
        raise StopIteration
    cp.Model.solve = fake_solve
    ns = {"__name__": "__main__"}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, ns)
    except StopIteration:
        pass
    finally:
        cp.Model.solve = orig
    S = cp.cpm_array(ns["schedule"])
    if S.shape != (n_nurses, n_days):
        raise ValueError(f"schedule shape {S.shape} != {(n_nurses, n_days)} (data hardcoded?)")
    return toplevel_list(captured["model"].constraints), S


def none_of(cons):
    """Negation of a conjunction; an empty conjunction is True, so its negation is False."""
    return ~cp.all(cons) if cons else cp.BoolVal(False)


def check(gen_code, gt_code):
    # under-constraint: gen(S) and not GT(S), same S
    g_cons, gS = build(gen_code, N_NURSES, N_DAYS)
    t_cons, tS = build(gt_code, N_NURSES, N_DAYS)
    m = cp.Model(g_cons, gS == tS, none_of(t_cons))
    under = m.solve(time_limit=60)
    witness = gS.value().tolist() if under else None

    # over-constraint: a rule-valid schedule the generated model rejects.
    # Exact single solve if the generated model has no variables besides `schedule`;
    # otherwise negating it is unsound (extra variables are existential), so enumerate 1 nurse x OVER_DAYS.
    extra = set(get_variables(g_cons)) - set(gS.flatten())
    if not extra:
        m = cp.Model(t_cons, gS == tS, none_of(g_cons))
        over = int(m.solve(time_limit=60))
        if over:
            witness_over = tS.value().tolist()
    else:
        try:
            g_cons, gS = build(gen_code, 1, OVER_DAYS)
            t_cons, tS = build(gt_code, 1, OVER_DAYS)
            valid = []
            cp.Model(t_cons).solveAll(display=lambda: valid.append(tS.value()[0].tolist()))
            lits = {(d, v): cp.boolvar() for d in range(OVER_DAYS) for v in range(4)}
            s = cp.SolverLookup.get("ortools", cp.Model(g_cons, [lits[d, v] == (gS[0, d] == v) for (d, v) in lits]))
            over = sum(not s.solve(assumptions=[lits[d, x] for d, x in enumerate(seq)]) for seq in valid)
        except Exception as e:
            over = f"n/a ({type(e).__name__}: {e})"
    return bool(under), witness, over


if __name__ == "__main__":
    log = json.loads(pathlib.Path(sys.argv[1]).read_text())
    for inst in log["instance_logs"]:
        gt_code = pathlib.Path(inst["file_path"]).read_text()
        name = pathlib.Path(inst["file_path"]).stem
        code = extract_code(inst["final_answer"])
        if code is None:
            print(f"{name}: no code"); continue
        try:
            under, witness, over = check(code, gt_code)
            ok = (not under) and over == 0
            print(f"{name}: SIA={inst['success']}  under={under}  over={over}  semantic_correct={ok}")
            if under:
                print("   accepted but forbidden:", " ".join("".join("MENR"[x] for x in row) for row in witness))
        except Exception as e:
            print(f"{name}: SIA={inst['success']}  semantic check failed: {type(e).__name__}: {e}")
