import time
import json
from pydantic import BaseModel
from typing import List
import numpy as np

class MeasureTime(BaseModel):
    start_time: float
    end_time: float
    opt_time: List[float]
    t_time: List[float]

    def generate_report(self) -> str:
        process_time = self.end_time - self.start_time
        if not self.opt_time:
            self.opt_time=[-1]
        if not self.t_time:
            self.t_time=[-1]
        report = {
            'Average time per optimization': np.mean(self.opt_time),
            'Average time per condition': np.mean(self.t_time),
            'Total process time (minutes)': process_time / 60,
            'Total process time (hours)': process_time / 3600
        }
        return json.dumps(report, indent=4)


