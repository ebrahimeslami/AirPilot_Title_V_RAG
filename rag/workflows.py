from dataclasses import dataclass
from typing import List, Dict

@dataclass
class StepResult:
    name: str
    status: str  # pending/complete/needs-human
    notes: str = ""

def applicability_check(pte_tpy: Dict[str, float], hap_single: float, hap_total: float, ozone_class: str|None) -> List[StepResult]:
    steps = []
    # Simple screening — conservative thresholds; human review required.
    major = any(v >= 100 for v in pte_tpy.values())
    major_hap = hap_single >= 10 or hap_total >= 25
    if ozone_class in {"Serious"} and (pte_tpy.get("VOC",0)>=50 or pte_tpy.get("NOx",0)>=50):
        major = True
    if ozone_class in {"Severe"} and (pte_tpy.get("VOC",0)>=25 or pte_tpy.get("NOx",0)>=25):
        major = True
    if ozone_class in {"Extreme"} and (pte_tpy.get("VOC",0)>=10 or pte_tpy.get("NOx",0)>=10):
        major = True

    steps.append(StepResult("Title V Major Source?", "complete" if (major or major_hap) else "pending",
                           notes="Screening only; confirm per 40 CFR 70 and 30 TAC 122."))
    steps.append(StepResult("Identify all applicable requirements", "pending"))
    steps.append(StepResult("Select SOP vs GOP pathway", "pending"))
    steps.append(StepResult("Prepare compliance monitoring plan (incl. CAM screen)", "pending"))
    steps.append(StepResult("Public notice/EPA review (if Title V)", "pending"))
    steps.append(StepResult("Reporting calendar (semiannual, ACC, EI)", "pending"))
    return steps
